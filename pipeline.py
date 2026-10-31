"""Free daily TNPSC current-affairs Tamil Short (runs on GitHub Actions).

news search (Tavily) -> Tamil script (Groq/OpenAI-compatible LLM) -> Tamil voice (edge-tts)
-> images (Pollinations) -> zoom/pan video + BGM (ffmpeg) -> YouTube upload (Data API)
"""
import asyncio
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

IST = ZoneInfo("Asia/Kolkata")
OUT = Path("out")
BGM = Path("assets/bgm.mp3")
W, H = 1080, 1920


def env(name, default=None):
    v = os.environ.get(name) or default  # GitHub passes unset variables as empty text
    if not v:
        sys.exit(f"Missing setting: {name}")
    return v


def log(msg):
    print(f"[{dt.datetime.now(IST):%H:%M:%S}] {msg}", flush=True)


# ---------------------------------------------------------------- 1. news search
# 5 videos a day: 3 current affairs + 2 aptitude (see .github/workflows/daily.yml for the clock times)
SLOTS = {
    1: ("news", "Tamil Nadu", ["Tamil Nadu government announcement news", "Tamil Nadu scheme policy news today"],
        "Tamil Nadu government, schemes, places, appointments"),
    2: ("news", "India & economy", ["India national news important today", "India economy RBI budget scheme news"],
        "India national affairs, government decisions, laws, polity, economy, banking"),
    3: ("aptitude", "Aptitude A", None, None),
    4: ("news", "Science, sports & world", ["India science technology ISRO environment news",
                                          "India sports awards international summit news"],
        "science, technology, space, environment, sports, awards, international events"),
    5: ("aptitude", "Aptitude B", None, None),
}
APTITUDE_TOPICS = [
    "Percentage shortcuts", "Ratio and proportion", "Time and work", "Speed, time and distance",
    "Simple interest", "Compound interest shortcut", "Average", "Profit and loss", "HCF and LCM",
    "Ages problems", "Number series", "Square and cube tricks", "Mixtures and alligation",
    "Pipes and cisterns", "Trains problems", "Boats and streams", "Mensuration (area, perimeter)",
    "Divisibility rules", "Simplification (BODMAS tricks)", "Calendar and clock problems",
]





def search_news(queries):
    key = env("TAVILY_API_KEY")
    seen, items = set(), []
    for q in queries:
        r = requests.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {key}"},
            json={"query": q, "topic": "news", "days": 2, "max_results": 6},
            timeout=60,
        )
        r.raise_for_status()
        for x in r.json().get("results", []):
            if x["url"] in seen:
                continue
            seen.add(x["url"])
            host = urllib.parse.urlparse(x["url"]).netloc.replace("www.", "")
            items.append({"title": x.get("title", ""), "host": host, "text": (x.get("content") or "")[:450]})
    if len(items) < 2:
        sys.exit("Too little news found; stopping instead of inventing facts.")
    notes = "\n".join(f"- {i['title']} ({i['host']}): {i['text']}" for i in items)
    hosts = []
    for i in items:
        if i["host"] not in hosts:
            hosts.append(i["host"])
    return notes, hosts[:6]


# ---------------------------------------------------------------- 2. Tamil script
_MODEL = {"name": None}


def pick_model(base, headers):
    """Ask the provider which chat models exist today and choose a good one."""
    r = requests.get(base + "/models", headers=headers, timeout=60)
    r.raise_for_status()
    ids = [m["id"] for m in r.json().get("data", []) if m.get("active", True)]
    bad = ("whisper", "guard", "tts", "orpheus", "embed", "safeguard")
    ids = [i for i in ids if not any(b in i.lower() for b in bad)]
    for pref in ("gpt-oss-120b", "llama-3.3-70b", "llama-4-maverick", "llama-4-scout",
                 "qwen", "kimi", "gpt-oss-20b", "llama-3.1-8b"):
        for i in ids:
            if pref in i.lower():
                return i
    if ids:
        return ids[0]
    sys.exit("No usable chat model found on the LLM provider.")


def llm_json(prompt):
    base = env("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    headers = {"Authorization": f"Bearer {env('LLM_API_KEY')}"}
    user_model = os.environ.get("LLM_MODEL") or ""
    if not _MODEL["name"]:
        _MODEL["name"] = user_model or "llama-3.3-70b-versatile"

    def call(json_mode=True):
        payload = {"model": _MODEL["name"], "messages": [{"role": "user", "content": prompt}],
                   "temperature": 0.5, "max_tokens": 6000}
        if "gpt-oss" in _MODEL["name"]:
            payload["reasoning_effort"] = "low"  # reasoning models can use up the budget and return nothing
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        return requests.post(base + "/chat/completions", headers=headers, json=payload, timeout=180)

    r = call()
    if r.status_code in (400, 404):
        log(f"LLM error {r.status_code}: {r.text[:300]}")
        if not user_model:  # you did not choose a model, so pick a current one automatically
            _MODEL["name"] = pick_model(base, headers)
            log(f"using model: {_MODEL['name']}")
            r = call()
        if r.status_code == 400:
            r = call(json_mode=False)
    for attempt in range(4):
        if r.status_code == 429:  # free-tier rate limit: wait and retry
            log("LLM rate limited; waiting 30s")
            time.sleep(30)
            r = call()
            continue
        if r.status_code == 400:
            log(f"LLM 400 (attempt {attempt + 1}); retrying without JSON mode")
            time.sleep(3)
            r = call(json_mode=False)
            continue
        if not r.ok:
            sys.exit(f"LLM error {r.status_code}: {r.text[:500]}")
        txt = (r.json()["choices"][0]["message"].get("content") or "").strip()
        a, b = txt.find("{"), txt.rfind("}")
        if a >= 0 and b > a:
            try:
                return json.loads(txt[a:b + 1])
            except json.JSONDecodeError:
                pass
        log(f"LLM returned no valid JSON (attempt {attempt + 1}); retrying")
        time.sleep(5)
        r = call()
    sys.exit("LLM kept returning invalid JSON.")


def write_script(notes, today, focus="", part=1, total=1):
    prompt = f"""You write 45-second YouTube Shorts for TNPSC aspirants in simple spoken TAMIL.
Date: {today}.
Use ONLY facts that appear in these news notes. Do not add facts from memory:
{notes}

This is video {part} of {total} today, so cover ONLY this theme: {focus}. Pick the 5 most exam-relevant facts for that theme. Make them EASY TO REMEMBER: a punchy hook
line, one short sentence per fact, ONE memory trick (a catchy word, acronym or rhyme in Tamil), then a quick
question for viewers and a line asking them to follow for daily current affairs.
The voiceover must be 90-115 Tamil words, written exactly as it should be spoken (no emojis, no bullets).

Return JSON with keys:
title (Tamil, under 85 characters),
description (Tamil, 3-5 line recap of the facts),
tags (list of 8 strings, Tamil and English),
voiceover (Tamil),
scenes (list of exactly 5 English prompts, one per fact in the order they are spoken. Each is a vertical
cinematic image that visually relates to THAT fact: places, buildings, objects and symbols, for example
Fort St George Chennai, a laptop with students, a glowing light bulb, a gold ring on silk, Tamil Nadu map
with festival lamps. NO text or letters in the image, NO logos, NO faces, NO real people or politicians)."""
    hint = ""
    for attempt in range(5):
        d = llm_json(prompt + hint)
        words = len(d.get("voiceover", "").split())
        lo = 70 if attempt < 3 else 55
        if all(k in d for k in ("title", "description", "tags", "voiceover", "scenes")) \
                and lo <= words <= 150 and len(d["scenes"]) >= 4:
            return d
        log(f"script attempt {attempt + 1} invalid (words={words}); retrying")
        hint = f"\n\nYour previous voiceover had only {words} words. Write at least 95 Tamil words."
    sys.exit("Could not get a valid script from the LLM.")


def safe_eval(expr):
    import ast
    import operator as op
    ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow,
           ast.USub: op.neg, ast.UAdd: op.pos, ast.Mod: op.mod}

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            l, r = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(r) > 6:
                raise ValueError("power too large")
            return ops[type(n.op)](l, r)
        if isinstance(n, ast.UnaryOp) and type(n.op) in ops:
            return ops[type(n.op)](ev(n.operand))
        raise ValueError("unsupported expression")
    return ev(ast.parse(str(expr), mode="eval"))


def write_aptitude_script(topic, today):
    prompt = f"""You write 45-second YouTube Shorts for TNPSC / Tamil Nadu competitive-exam aspirants, in simple
spoken TAMIL. Date: {today}. Topic: {topic}.

Teach ONE solved aptitude question using a SHORTCUT TRICK that saves time compared with the long method.
Use small, easy numbers. Structure of the voiceover: a punchy hook, the question stated slowly, the shortcut
in 3-4 very short steps with the numbers, the final answer, a one-line memory tip, then a similar practice
question for the viewer and a line asking them to follow for daily TNPSC aptitude tricks.
The voiceover must be 90-115 Tamil words, written exactly as spoken (no emojis, no bullets, no markdown).
The maths MUST be correct.

Return JSON with keys:
title (Tamil, under 85 characters, mention the topic),
description (Tamil, 3-5 lines: the question, the trick, the answer),
tags (list of 8 strings, Tamil and English),
voiceover (Tamil),
check_expr (a plain Python arithmetic expression using only numbers and + - * / ** that evaluates to the final answer),
answer (the final numeric answer as a number),
scenes (list of exactly 5 English prompts for vertical cinematic images that relate to the problem's story or to
studying maths: for example a notebook and pencil on a desk, an old analog clock, coins and a calculator, a
train on a bridge, a balance scale. NO text or letters in the image, NO logos, NO faces, NO real people)."""
    hint = ""
    for attempt in range(6):
        d = llm_json(prompt + hint)
        words = len(d.get("voiceover", "").split())
        ok = all(k in d for k in ("title", "description", "tags", "voiceover", "scenes", "check_expr", "answer"))
        lo = 70 if attempt < 3 else 55  # accept slightly shorter scripts on later attempts
        if ok and lo <= words <= 150 and len(d["scenes"]) >= 4:
            try:
                got, want = float(safe_eval(d["check_expr"])), float(d["answer"])
                if abs(got - want) <= 1e-6 * max(1.0, abs(want)):
                    return d
                log(f"aptitude attempt {attempt + 1}: maths mismatch ({got} vs {want}); retrying")
                continue
            except Exception as e:
                log(f"aptitude attempt {attempt + 1}: cannot verify maths ({e}); retrying")
                continue
        log(f"aptitude attempt {attempt + 1} invalid (words={words}); retrying")
        hint = (f"\n\nYour previous voiceover had only {words} words. Write MORE: at least 95 Tamil words, "
                "with every step of the trick spoken in full sentences.")
    sys.exit("Could not get a verified aptitude script from the LLM.")


# ---------------------------------------------------------------- 3. voice
def make_voice(text, path):
    """Makes the voiceover and returns timing segments (start_s, dur_s, text) for the captions."""
    import edge_tts

    segs = []

    async def go():
        voice = env("TTS_VOICE", "ta-IN-PallaviNeural")
        try:
            comm = edge_tts.Communicate(text, voice, rate="+0%", boundary="WordBoundary")
        except TypeError:  # older edge-tts versions
            comm = edge_tts.Communicate(text, voice, rate="+0%")
        with open(path, "wb") as f:
            async for ch in comm.stream():
                if ch["type"] == "audio":
                    f.write(ch["data"])
                elif ch["type"] in ("WordBoundary", "SentenceBoundary"):
                    segs.append((ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"]))

    asyncio.run(go())
    return segs


# ---------------------------------------------------------------- 4. images
def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        sys.exit(f"ffmpeg failed: {p.stderr[-800:]}")


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return float(out.strip())


def fallback_image(path, color):
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s={W}x{H}", "-frames:v", "1", str(path)])


_LAST_GOOD = {"path": None}


def fetch_image(prompt, path, seed):
    style = ". Cinematic, soft warm light, vertical composition, no text, no watermark"
    for attempt in range(5):
        # smaller size is faster and more reliable on the free service; ffmpeg scales it up
        url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt + style)
               + f"?width=720&height=1280&nologo=true&seed={seed + attempt}")
        try:
            r = requests.get(url, timeout=120)
            if r.ok and r.headers.get("content-type", "").startswith("image") and len(r.content) > 10_000:
                path.write_bytes(r.content)
                _LAST_GOOD["path"] = path
                return
        except requests.RequestException:
            pass
        time.sleep(10 * (attempt + 1))
    prev = _LAST_GOOD["path"]
    if prev and Path(prev).exists():
        log(f"image failed for '{prompt[:40]}', reusing previous image")
        path.write_bytes(Path(prev).read_bytes())
        return
    log(f"image failed for '{prompt[:40]}', using plain background")
    fallback_image(path, ["0x14213d", "0x1b4332", "0x3d2c5a"][seed % 3])


# ---------------------------------------------------------------- 5. video
def make_clip(img, seconds, out, zoom_in):
    frames = int(seconds * 30) + 1
    z = "min(zoom+0.0007,1.25)" if zoom_in else "if(eq(on,1),1.25,max(zoom-0.0007,1.0))"
    vf = (f"scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=30,"
          f"eq=brightness=-0.12:saturation=1.05,format=yuv420p")  # slightly darker so text stands out
    run(["ffmpeg", "-y", "-i", str(img), "-vf", vf, "-t", f"{seconds:.2f}", "-r", "30",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(out)])


def tamil_chunks(text, max_words=4):
    """Split the voiceover into short on-screen phrases (sentence ends first, then every few words)."""
    import re
    chunks = []
    for sent in re.split(r"(?<=[.!?।—])\s+|\n+", text.strip()):
        words = [w for w in sent.replace("{", "").replace("}", "").replace("\\", "").split() if w]
        for i in range(0, len(words), max_words):
            chunks.append(words[i:i + max_words])
    return [c for c in chunks if c]


def ass_time(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def write_ass(text, speech_seconds, path, start=0.15, date_text="", head2="CURRENT AFFAIRS", head3="நடப்பு நிகழ்வுகள்"):
    """Running Tamil text: each phrase appears and its words light up as they are spoken.
    Timing is spread over the voice length by letter count (works with any TTS).
    Also adds the 'TNPSC CURRENT AFFAIRS' title block with the date at the top for the whole video."""
    font = os.environ.get("SUB_FONT") or "Noto Sans Tamil"
    latin = os.environ.get("SUB_LATIN_FONT") or "DejaVu Sans"
    chunks = tamil_chunks(text)
    weights = [sum(len(w) for w in c) for c in chunks]
    scale = max(speech_seconds - start, 1.0) / max(sum(weights), 1)
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,"
        "Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,"
        "MarginV,Encoding\n"
        f"Style: Run,{font},78,&H0000D7FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,2,2,70,70,430,1\n"
        f"Style: Head,{latin},60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,3,1,8,40,40,100,1\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,MarginL,MarginR,MarginV,Effect,Text\n"
    )
    total = speech_seconds + 1.2
    gold = r"\c&H3CC8FF&"
    white = r"\c&HFFFFFF&"
    title = (rf"{{\fs125{gold}}}TNPSC\N{{\fs62{white}}}{head2}\N"
             rf"{{\fn{font}\fs54{white}}}{head3}\N"
             rf"{{\fn{latin}\fs50{gold}}}{date_text}")
    lines, t = [f"Dialogue: 0,{ass_time(0)},{ass_time(total)},Head,0,0,0,,{title}"], start
    for c, wt in zip(chunks, weights):
        dur = wt * scale
        ks, used = [], 0
        for w in c:
            k = int(round(dur * 100 * len(w) / max(wt, 1)))
            ks.append(k)
            used += k
        ks[-1] += int(round(dur * 100)) - used
        body = "".join(f"{{\\kf{max(k, 1)}}}{w} " for k, w in zip(ks, c)).strip()
        lines.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + dur + 0.05)},Run,0,0,0,,{{\\fad(120,60)}}{body}")
        t += dur
    Path(path).write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def build_video(images, voice, out, workdir, bgm=BGM, subs=None):
    total = duration(voice) + 1.0
    per = total / len(images)
    clips = []
    for i, img in enumerate(images):
        c = workdir / f"clip{i}.mp4"
        make_clip(img, per + 0.1, c, zoom_in=(i % 2 == 0))
        clips.append(c)
    lst = workdir / "list.txt"
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    joined = workdir / "joined.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    cmd = ["ffmpeg", "-y", "-i", str(joined), "-i", str(voice)]
    if Path(bgm).exists():
        cmd += ["-stream_loop", "-1", "-i", str(bgm), "-filter_complex",
                f"[1:a]apad=pad_dur=1[v];[2:a]volume=0.15,afade=t=in:d=1.5[b];"
                f"[v][b]amix=inputs=2:duration=first:dropout_transition=0[m];"
                f"[m]volume=1.8,afade=t=out:st={total - 1.5:.2f}:d=1.5[a]"]
    else:
        log("WARNING: assets/bgm.mp3 not found, publishing without BGM")
        cmd += ["-filter_complex", "[1:a]apad=pad_dur=1[a]"]
    if subs:
        # dark panel behind the title block, then the title and running Tamil text from the .ass file
        cmd += ["-vf", f"drawbox=x=0:y=70:w=iw:h=370:color=black@0.55:t=fill,ass={Path(subs).resolve()}"]
    cmd += ["-map", "0:v", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    run(cmd)
    return total


# ---------------------------------------------------------------- 6. YouTube upload
def upload(video, title, description, tags):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials(
        None,
        refresh_token=env("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=env("YT_CLIENT_ID"),
        client_secret=env("YT_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    yt = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {"title": title[:100], "description": description[:4800], "tags": tags[:15],
                    "categoryId": "27", "defaultLanguage": "ta"},
        "status": {"privacyStatus": env("YT_PRIVACY", "private"), "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": True},
    }
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    log(f"uploaded: https://youtube.com/watch?v={resp['id']} (privacy: {body['status']['privacyStatus']})")


# ---------------------------------------------------------------- main
def make_one(slot, today, stamp, upload_it):
    kind, name, queries, focus = SLOTS[slot]
    tag = f"{stamp}-s{slot}"
    work = OUT / f"work-{tag}"
    work.mkdir(parents=True, exist_ok=True)
    hosts = []

    if kind == "news":
        log(f"[slot {slot}] {name}: searching news")
        notes, hosts = search_news(queries)
        (OUT / f"notes-{tag}.txt").write_text(notes, encoding="utf-8")
        log(f"[slot {slot}] writing Tamil script")
        s = write_script(notes, today, focus, slot, 5)
        head2, head3, hashtags = "CURRENT AFFAIRS", "நடப்பு நிகழ்வுகள்", "#TNPSC #CurrentAffairs #Shorts"
        pre, post = "Sources: " + ", ".join(hosts), "AI-assisted video. Verify facts with official sources."
    else:
        doy = dt.datetime.now(IST).timetuple().tm_yday
        topic = APTITUDE_TOPICS[(doy * 2 + (0 if slot == 3 else 1)) % len(APTITUDE_TOPICS)]
        log(f"[slot {slot}] aptitude topic: {topic}")
        s = write_aptitude_script(topic, today)
        head2, head3, hashtags = "APTITUDE TRICKS", "கணிதம் - குறுக்கு வழி", "#TNPSC #Aptitude #MathsTricks #Shorts"
        pre, post = "Topic: " + topic, "AI-assisted video. Practise the method on your own."
    (OUT / f"script-{tag}.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")

    voice = work / "voice.mp3"
    make_voice(s["voiceover"], voice)

    imgs = []
    for i, scene in enumerate(s["scenes"][:5]):
        p = work / f"img{i}.png"
        fetch_image(scene, p, seed=(int(stamp) % 1000) * 10 + slot * 7 + i)
        imgs.append(p)

    final = OUT / f"tnpsc-{tag}.mp4"
    subs = work / "captions.ass"
    write_ass(s["voiceover"], duration(voice), subs, date_text=today, head2=head2, head3=head3)
    secs = build_video(imgs, voice, final, work, subs=subs)
    log(f"[slot {slot}] video ready ({secs:.0f}s): {final}")

    if upload_it:
        desc = s["description"] + f"\n\n{pre}\n{post}\n{hashtags}"
        upload(final, f"{s['title']} #Shorts", desc, [str(t) for t in s["tags"]])
    else:
        log("UPLOAD=false, skipping YouTube upload")


def pick_slots():
    v = (os.environ.get("SLOT") or "").strip().lower()
    if v == "all":
        return list(SLOTS)
    if v.isdigit() and int(v) in SLOTS:
        return [int(v)]
    # no slot given: choose by the IST clock (8, 10:30, 13, 15:30, 18)
    h = dt.datetime.now(IST).hour + dt.datetime.now(IST).minute / 60
    starts = {1: 8.0, 2: 10.5, 3: 13.0, 4: 15.5, 5: 18.0}
    return [min(starts, key=lambda k: abs(starts[k] - h))]


def main():
    OUT.mkdir(exist_ok=True)
    now = dt.datetime.now(IST)
    today, stamp = now.strftime("%d %B %Y"), now.strftime("%Y%m%d")
    upload_it = env("UPLOAD", "true").lower() == "true"
    slots = pick_slots()
    log(f"slots to build: {slots}")

    done, failed = 0, []
    for slot in slots:
        try:
            make_one(slot, today, stamp, upload_it)
            done += 1
            time.sleep(20)  # ease free-tier rate limits
        except BaseException as e:  # with SLOT=all, one bad video does not cancel the rest
            if isinstance(e, KeyboardInterrupt):
                raise
            failed.append(slot)
            log(f"slot {slot} FAILED: {e!r}")
    log(f"finished: {done}/{len(slots)} videos; failed: {failed or 'none'}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
