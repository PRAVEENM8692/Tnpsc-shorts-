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
QUERIES = [
    "Tamil Nadu government announcement news",
    "India national news important today",
    "India economy RBI government scheme news",
    "India awards appointments sports science news",
]


def search_news():
    key = env("TAVILY_API_KEY")
    seen, items = set(), []
    for q in QUERIES:
        r = requests.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {key}"},
            json={"query": q, "topic": "news", "days": 2, "max_results": 5},
            timeout=60,
        )
        r.raise_for_status()
        for x in r.json().get("results", []):
            if x["url"] in seen:
                continue
            seen.add(x["url"])
            host = urllib.parse.urlparse(x["url"]).netloc.replace("www.", "")
            items.append({"title": x.get("title", ""), "host": host, "text": (x.get("content") or "")[:450]})
    if len(items) < 3:
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
                   "temperature": 0.5}
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        return requests.post(base + "/chat/completions", headers=headers, json=payload, timeout=120)

    r = call()
    if r.status_code in (400, 404):
        log(f"LLM error {r.status_code}: {r.text[:300]}")
        if not user_model:  # you did not choose a model, so pick a current one automatically
            _MODEL["name"] = pick_model(base, headers)
            log(f"using model: {_MODEL['name']}")
            r = call()
        if r.status_code == 400:
            r = call(json_mode=False)
    if not r.ok:
        sys.exit(f"LLM error {r.status_code}: {r.text[:500]}")
    txt = r.json()["choices"][0]["message"]["content"].strip()
    a, b = txt.find("{"), txt.rfind("}")
    return json.loads(txt[a:b + 1])


def write_script(notes, today):
    prompt = f"""You write 45-second YouTube Shorts for TNPSC aspirants in simple spoken TAMIL.
Date: {today}.
Use ONLY facts that appear in these news notes. Do not add facts from memory:
{notes}

Pick the 5 most exam-relevant facts (Tamil Nadu first, then India). Make them EASY TO REMEMBER: a punchy hook
line, one short sentence per fact, ONE memory trick (a catchy word, acronym or rhyme in Tamil), then a quick
question for viewers and a line asking them to follow for daily current affairs.
The voiceover must be 90-115 Tamil words, written exactly as it should be spoken (no emojis, no bullets).

Return JSON with keys:
title (Tamil, under 85 characters),
description (Tamil, 3-5 line recap of the facts),
tags (list of 8 strings, Tamil and English),
voiceover (Tamil),
scenes (list of exactly 3 English prompts for vertical cinematic images that suit a motivational study video,
e.g. aspirant studying at dawn, Tamil Nadu temple towers, Chennai Marina. NO text, NO logos, NO real people)."""
    for attempt in range(3):
        d = llm_json(prompt)
        words = len(d.get("voiceover", "").split())
        if all(k in d for k in ("title", "description", "tags", "voiceover", "scenes")) \
                and 70 <= words <= 150 and len(d["scenes"]) >= 3:
            return d
        log(f"script attempt {attempt + 1} invalid (words={words}); retrying")
    sys.exit("Could not get a valid script from the LLM.")


# ---------------------------------------------------------------- 3. voice
def make_voice(text, path):
    import edge_tts

    async def go():
        await edge_tts.Communicate(text, env("TTS_VOICE", "ta-IN-PallaviNeural"), rate="+0%").save(str(path))

    asyncio.run(go())


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


def fetch_image(prompt, path, seed):
    style = ". Cinematic, soft warm light, vertical composition, no text, no watermark"
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt + style)
           + f"?width={W}&height={H}&nologo=true&seed={seed}")
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=150)
            if r.ok and r.headers.get("content-type", "").startswith("image") and len(r.content) > 10_000:
                path.write_bytes(r.content)
                return
        except requests.RequestException:
            pass
        time.sleep(8 * (attempt + 1))
    log(f"image failed for '{prompt[:40]}', using plain background")
    fallback_image(path, ["0x14213d", "0x1b4332", "0x3d2c5a"][seed % 3])


# ---------------------------------------------------------------- 5. video
def make_clip(img, seconds, out, zoom_in):
    frames = int(seconds * 30) + 1
    z = "min(zoom+0.0007,1.25)" if zoom_in else "if(eq(on,1),1.25,max(zoom-0.0007,1.0))"
    vf = (f"scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=30,"
          f"format=yuv420p")
    run(["ffmpeg", "-y", "-i", str(img), "-vf", vf, "-t", f"{seconds:.2f}", "-r", "30",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(out)])


def build_video(images, voice, out, workdir, bgm=BGM):
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
def main():
    OUT.mkdir(exist_ok=True)
    today = dt.datetime.now(IST).strftime("%d %B %Y")
    stamp = dt.datetime.now(IST).strftime("%Y%m%d")
    work = OUT / f"work-{stamp}"
    work.mkdir(exist_ok=True)

    log("searching news")
    notes, hosts = search_news()
    (OUT / f"notes-{stamp}.txt").write_text(notes, encoding="utf-8")

    log("writing Tamil script")
    s = write_script(notes, today)
    (OUT / f"script-{stamp}.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")

    log("making voiceover")
    voice = work / "voice.mp3"
    make_voice(s["voiceover"], voice)

    log("making images")
    imgs = []
    for i, scene in enumerate(s["scenes"][:3]):
        p = work / f"img{i}.png"
        fetch_image(scene, p, seed=int(stamp) % 1000 + i)
        imgs.append(p)

    log("building video")
    final = OUT / f"tnpsc-{stamp}.mp4"
    secs = build_video(imgs, voice, final, work)
    log(f"video ready ({secs:.0f}s): {final}")

    if env("UPLOAD", "true").lower() == "true":
        desc = (s["description"] + "\n\nSources: " + ", ".join(hosts)
                + "\nAI-assisted video. Verify facts with official sources.\n#TNPSC #CurrentAffairs #Shorts")
        upload(final, s["title"] + " #Shorts", desc, [str(t) for t in s["tags"]])
    else:
        log("UPLOAD=false, skipping YouTube upload")


if __name__ == "__main__":
    main()
