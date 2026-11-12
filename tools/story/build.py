"""Builds a long comic-story video from tools/story/<name>.json (hand-run; uploads NOTHING to YouTube).
pictures (Cloudflare FLUX, 16:9 crop) + Tamil voice (Gemini TTS via pipeline.py) + on-screen text (drawn by a browser, so
Tamil letters are always right) + NCS background music -> out/story/<name>.mp4.  Pictures are kept on the side branch
story-out and re-used by the next run, so a re-run only draws what is missing.
Env: CF_ACCOUNT_ID, CF_API_TOKEN, GEMINI_API_KEY (+ optional LLM_API_KEY for the voice check). NAME=delhi1."""
import base64, io, json, os, random, re, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

sys.path.insert(0, ".")
import pipeline as P  # voice helpers (Gemini TTS -> edge-tts fallback), ffmpeg helpers

NAME = os.environ.get("NAME") or "delhi1"
DATA = json.load(open(f"tools/story/{NAME}.json", encoding="utf-8"))
OUT = Path("out/story"); IMG = OUT / "sq"; OLD = OUT / "old"; WORK = OUT / "work"   # sq = whole square pictures; old = first cropped version (fallback only)
for d in (IMG, OLD, WORK):
    d.mkdir(parents=True, exist_ok=True)
CF_ID, CF_TOKEN = os.environ.get("CF_ACCOUNT_ID"), os.environ.get("CF_API_TOKEN")
VW, VH = 1280, 720
STYLE = ("Indian comic book illustration, bold clean black ink outlines, flat bright colours with soft cel shading, "
         "warm palette, richly detailed background, expressive faces, cinematic. ")
FRAME = " Full figure of every character visible from head to feet, nothing cut off at the frame edges."
END = " No text, no letters, no watermark."
log = P.log


def restore_cached():
    """Pictures drawn by earlier runs live on the branch story-out; bring them back instead of drawing again."""
    subprocess.run(["git", "fetch", "-q", "origin", "story-out"], capture_output=True)
    for s in DATA["shots"]:
        for folder, dst in (("sq", IMG), ("old", OLD), ("img", OLD)):   # img = the very first (cropped) run
            f = dst / f"{s['n']:02d}.jpg"
            if f.exists():
                continue
            r = subprocess.run(["git", "show", f"FETCH_HEAD:{folder}/{f.name}"], capture_output=True)
            if r.returncode == 0 and len(r.stdout) > 5000:
                f.write_bytes(r.stdout)


def draw(prompt, dst):
    from PIL import Image
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    last = None
    for n in range(4):
        try:
            body = json.dumps({"prompt": prompt[:2000], "steps": 4}).encode()
            req = urllib.request.Request(url, body, {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"})
            raw = base64.b64decode(json.load(urllib.request.urlopen(req, timeout=180))["result"]["image"])
            Image.open(io.BytesIO(raw)).convert("RGB").save(dst, quality=90)   # keep the WHOLE square picture
            return True
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:300]!r}"
        except Exception as e:
            last = str(e)
        time.sleep(4 * (n + 1))
    log(f"picture failed: {last}")
    return False


def make_pictures():
    restore_cached()
    missing, fails = [], 0
    for s in DATA["shots"]:
        f = IMG / f"{s['n']:02d}.jpg"
        if f.exists():
            continue
        if fails < 3 and CF_ID and CF_TOKEN and draw(STYLE + s["scene"] + FRAME + END, f):
            fails = 0
            log(f"picture {s['n']:02d} drawn")
        else:
            fails += 1   # after 3 failures in a row (daily free limit?) stop asking; the old picture is used for the rest
            missing.append(s["n"])
    log(f"pictures ready: {len(DATA['shots']) - len(missing)}/{len(DATA['shots'])}; missing: {missing}")
    return missing


# ---------------------------------------------------------------- text on screen (browser renders Tamil correctly)
CSS = "body{margin:0;width:1280px;height:720px;font-family:'Noto Sans Tamil','Noto Sans',sans-serif;color:#fff}"


def render_pngs(items):
    """items: [(html, out_path, transparent)]"""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": VW, "height": VH})
        for html, out, transparent in items:
            pg.set_content(html)
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(out), omit_background=transparent)
        b.close()


def overlay_html(text):
    return (f"<html><style>{CSS}body{{background:transparent}}"
            ".b{position:absolute;left:50%;bottom:46px;transform:translateX(-50%);max-width:1120px;text-align:center;"
            "background:rgba(10,10,20,.78);border:3px solid #ffd54a;border-radius:22px;padding:16px 34px;"
            "font-size:44px;font-weight:800;line-height:1.35;box-shadow:0 6px 24px rgba(0,0,0,.5)}</style>"
            f"<body><div class='b'>{text}</div></body></html>")


def card_html(i, total, text):
    return (f"<html><style>{CSS}body{{background:linear-gradient(135deg,#1b1f4a,#3b1a5e 55%,#7a2a4b);}}"
            ".n{position:absolute;left:70px;top:50px;font-size:34px;font-weight:700;color:#ffd54a}"
            ".t{position:absolute;left:90px;right:90px;top:50%;transform:translateY(-50%);font-size:58px;font-weight:800;"
            "line-height:1.5;text-align:center}.f{position:absolute;bottom:34px;width:100%;text-align:center;font-size:28px;"
            "color:#cfd3ff}</style>"
            f"<body><div class='n'>தேர்வுக்கான குறிப்பு {i} / {total}</div><div class='t'>{text}</div>"
            "<div class='f'>TNPSC Bites</div></body></html>")


# ---------------------------------------------------------------- shots, voice, timing
def build_shots(missing):
    shots = [dict(s) for s in DATA["shots"]]
    cards = DATA.get("exam_cards") or []
    base = len(shots)
    if cards:
        shots.append({"n": base + 1, "nar": "TNPSC-க்குப் படிப்பவர்கள் இந்த ஐந்தையும் குறித்துக்கொள்ளுங்கள்.", "card": 0})
        for i, c in enumerate(cards, 1):
            shots.append({"n": base + 1 + i, "nar": c, "card": i})
        shots.append({"n": base + len(cards) + 2, "nar": "அடுத்த பகுதியைத் தவறவிடாமல் இருக்க TNPSC Bites சேனலை subscribe செய்யுங்கள்.", "card": -1})
    return shots


def weight(nar):
    t = P.tts_text(nar)
    return len(re.sub(r"[\s.,?]", "", t)) + 5 * len(re.findall(r"[.?]", t))


def group(shots, size=7):
    """Voice is made in groups of ~7 sentences (a few calls instead of one per picture); the exam notes are one group."""
    groups, cur = [], []
    for s in shots:
        if "card" in s:
            if cur:
                groups.append(cur); cur = []
            groups.append([x for x in shots if "card" in x]); break
        cur.append(s)
        if len(cur) == size:
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    return groups


def snap(bounds, spans, total):
    """Move each internal boundary to the nearest pause in the voice (within 0.8 s) so pictures change between sentences."""
    pauses = [(spans[i][1] + spans[i + 1][0]) / 2 for i in range(len(spans) - 1)]
    out, prev = [], 0.0
    for b in bounds:
        near = min(pauses, key=lambda p: abs(p - b), default=None)
        if near is not None and abs(near - b) <= 0.8:
            b = near
        b = max(b, prev + 1.2)
        out.append(min(b, total - 0.5))
        prev = out[-1]
    return out


def main():
    missing = make_pictures()
    shots = build_shots(missing)
    groups = group(shots)
    gap = 0.35
    parts = [(f"g{i}", " ".join(s["nar"] for s in g)) for i, g in enumerate(groups)]
    voice = OUT / "voice.mp3"
    os.environ.setdefault("VOICES", "Charon")
    starts = P.make_voice_parts(parts, voice, WORK, gap=gap)
    log(f"voice ready: {P.duration(voice):.1f} s in {len(parts)} parts")

    # text pictures
    jobs = []
    ncards = len(DATA.get("exam_cards") or [])
    for s in shots:
        n = s["n"]
        if "card" in s:
            c = s["card"]
            text = s["nar"] if c > 0 else ("இந்த 5 குறிப்புகள் தேர்வுக்கு" if c == 0 else "அடுத்த பகுதியைத் தவறவிடாதீர்கள்<br>TNPSC Bites – Subscribe")
            jobs.append((card_html(c, ncards, text) if c > 0 else card_html(0, ncards, text).replace("தேர்வுக்கான குறிப்பு 0 / %d" % ncards, ""),
                         WORK / f"card_{n:02d}.png", False))
        elif s.get("text"):
            jobs.append((overlay_html(s["text"]), WORK / f"ov_{n:02d}.png", True))
    render_pngs(jobs)

    # per-shot durations
    clips, total = [], 0.0
    for gi, g in enumerate(groups):
        part = WORK / f"part_g{gi}.mp3"
        D = P.duration(part)
        spans = P.speech_spans(part)
        ws = [weight(s["nar"]) for s in g]
        acc, bounds = 0, []
        for w in ws[:-1]:
            acc += w
            bounds.append(D * acc / sum(ws))
        bounds = snap(bounds, spans, D) if len(g) > 1 else []
        edges = [0.0] + bounds + [D + gap]
        for k, s in enumerate(g):
            dur = edges[k + 1] - edges[k]
            img = IMG / f"{s['n']:02d}.jpg"
            if "card" in s:
                src, ov = WORK / f"card_{s['n']:02d}.png", None
            else:
                old = OLD / img.name
                src = img if img.exists() else (old if old.exists() else None)
                ov = WORK / f"ov_{s['n']:02d}.png" if (WORK / f"ov_{s['n']:02d}.png").exists() else None
            clip = WORK / f"clip_{s['n']:02d}.mp4"
            is_sq = src is not None and src.parent == IMG
            if src is None:   # picture missing: dark placeholder, the run still finishes
                cmd = ["ffmpeg", "-y", "-f", "lavfi", "-t", f"{dur:.3f}", "-i", f"color=c=0x1b1f4a:s={VW}x{VH}:r=30"]
            else:
                cmd = ["ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.3f}", "-i", str(src)]
            if is_sq:   # whole square picture in the middle, its own blurred copy fills the sides: nothing is cut off
                base = (f"[0:v]split[a][b];[a]scale={VW}:{VH}:force_original_aspect_ratio=increase,crop={VW}:{VH},"
                        f"boxblur=28:4,eq=brightness=-0.15[bg];[b]scale=-2:{VH}[fg];[bg][fg]overlay=(W-w)/2:0,setsar=1[b0]")
            else:
                base = f"[0:v]scale={VW}:{VH},setsar=1[b0]"
            if ov:
                cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", str(ov)]
                fc = f"{base};[b0][1:v]overlay=0:0,format=yuv420p[v]"
            else:
                fc = f"{base};[b0]format=yuv420p[v]"
            cmd += ["-filter_complex", fc, "-map", "[v]", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", str(clip)]
            P.run(cmd)
            clips.append(clip)
            total += dur
    lst = WORK / "clips.txt"
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    silent = WORK / "silent.mp4"
    P.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(silent)])

    bgm = P.pick_bgm()
    final = OUT / f"{NAME}.mp4"
    T = P.duration(voice)
    if bgm:
        fc = f"[2:a]volume=0.16,afade=t=out:st={max(T - 3, 0):.2f}:d=3[m];[1:a][m]amix=inputs=2:duration=first:normalize=0[a]"
        P.run(["ffmpeg", "-y", "-i", str(silent), "-i", str(voice), "-stream_loop", "-1", "-i", str(bgm),
               "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(final)])
    else:
        P.run(["ffmpeg", "-y", "-i", str(silent), "-i", voice and str(voice), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
               "-c:a", "aac", "-b:a", "160k", "-shortest", str(final)])
    log(f"video ready: {final} {P.duration(final):.1f} s, {final.stat().st_size // 1024 // 1024} MB; missing pictures: {missing}")
    (OUT / "report.json").write_text(json.dumps({"missing": missing, "seconds": P.duration(final), "shots": len(shots)}))


main()
