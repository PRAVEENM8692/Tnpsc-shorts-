"""News-card video for the current-affairs Shorts (HTML/CSS cards drawn by a browser, joined by ffmpeg).

Why a browser: it wraps and shrinks Tamil text to fit its box (see fit() below), so words never overlap or run
off the card. Each part of the voiceover (hook, fact 1-5, memory tip, outro) gets one card; the card slides in
exactly when that part of the voice starts. The channel header, running captions and LIKE/SUBSCRIBE buttons are
added afterwards by pipeline.py (same as the Manim aptitude video), so the cards only use the middle of the screen.

Needs:  pip install playwright  (it uses the Chrome that GitHub runners already have, or `playwright install chromium`)
        and the font "Noto Sans Tamil" (apt: fonts-noto-core, already installed by daily.yml).
"""
import html
import subprocess
from pathlib import Path

W, H = 1080, 1920
TOP, HEIGHT = 480, 780          # the card area: below the header panel, above the captions (y 480-1260)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0B1B3A;
  font-family:'Noto Sans Tamil','Latha','Nirmala UI','FreeSans',sans-serif;color:#fff}
#bg{position:absolute;inset:0;background-size:cover;background-position:center;filter:blur(9px) brightness(.5) saturate(1.1);
  transform:scale(1.08)}
#bgshade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,27,58,.55),rgba(11,27,58,.15) 40%%,rgba(11,27,58,.65))}
#fg{position:absolute;left:40px;top:%(top)dpx;width:1000px;height:%(h)dpx}
.card{width:100%%;height:100%%;border-radius:36px;padding:30px 36px;display:flex;flex-direction:column;gap:18px;
  background:linear-gradient(160deg,rgba(18,48,107,.93),rgba(11,27,58,.93));border:3px solid rgba(255,201,60,.85);
  box-shadow:0 18px 60px rgba(0,0,0,.45)}
.card.gold{background:linear-gradient(160deg,#FFD866,#FFC93C);border-color:#fff;color:#0B1B3A}
.row{display:flex;align-items:center;justify-content:space-between;height:62px;flex:none}
.chip{background:#FFC93C;color:#0B1B3A;font-weight:800;font-size:34px;padding:6px 26px;border-radius:40px;white-space:nowrap}
.card.gold .chip{background:#0B1B3A;color:#FFC93C}
.dots{display:flex;gap:12px}
.dot{width:20px;height:20px;border-radius:50%%;background:rgba(255,255,255,.28)}
.dot.on{background:#FFC93C}.dot.cur{background:#3DDC84;transform:scale(1.35)}
.t{font-weight:800;line-height:1.3;overflow:hidden;color:#fff;flex:none}
.big{font-weight:900;line-height:1.15;overflow:hidden;color:#FFC93C;flex:none;text-align:center;
  background:rgba(255,255,255,.08);border-radius:22px;display:flex;align-items:center;justify-content:center}
.d{font-weight:500;line-height:1.45;overflow:hidden;color:#E8EEFF;flex:1;min-height:0}
.card.gold .t,.card.gold .d{color:#0B1B3A}
.center{flex:1;display:flex;flex-direction:column;justify-content:center;gap:26px;min-height:0}
.sub{font-weight:700;font-size:38px;color:#3DDC84;text-align:center;flex:none}
"""

JS = """
() => {
  const fit = (el, max, min) => {
    let s = max; el.style.fontSize = s + 'px';
    while ((el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1) && s > min) {
      s -= 2; el.style.fontSize = s + 'px';
    }
  };
  document.querySelectorAll('[data-fit]').forEach(el => {
    const [mx, mn] = el.dataset.fit.split(',').map(Number); fit(el, mx, mn);
  });
}
"""


def _e(x):
    return html.escape(str(x or "").strip())


def _dots(i, n=5):
    return "".join(f'<div class="dot {"cur" if k == i else ("on" if k < i else "")}"></div>' for k in range(n))


def _card(kind, d, today):
    """HTML of the card for one segment. kind: hook | fact | tip | outro."""
    if kind == "hook":
        return (f'<div class="card"><div class="row"><div class="chip">{_e(d.get("chip") or "நடப்பு நிகழ்வுகள்")}</div>'
                f'<div class="chip" style="background:#3DDC84">{_e(today)}</div></div>'
                f'<div class="center"><div class="t" data-fit="96,44" style="height:430px;display:flex;align-items:center;'
                f'text-align:center;justify-content:center">{_e(d["headline"])}</div>'
                f'<div class="sub">இன்னைக்கு தெரிஞ்சுக்க வேண்டிய 5 தகவல்கள்</div></div></div>')
    if kind == "fact":
        big = d.get("big", "").strip()
        n, i = d["n"], d["n"] - 1
        big_html = f'<div class="big" data-fit="110,44" style="height:130px">{_e(big)}</div>' if big else ""
        t_h = 190 if big else 230
        return (f'<div class="card"><div class="row"><div class="chip">தகவல் {n} / 5</div>'
                f'<div class="dots">{_dots(i)}</div></div>'
                f'<div class="t" data-fit="74,38" style="height:{t_h}px">{_e(d["title"])}</div>{big_html}'
                f'<div class="d" data-fit="52,30">{_e(d["detail"])}</div></div>')
    if kind == "tip":
        return (f'<div class="card gold"><div class="row"><div class="chip">நினைவில் வை</div></div>'
                f'<div class="center"><div class="t" data-fit="84,40" style="height:520px;display:flex;align-items:center;'
                f'text-align:center;justify-content:center">{_e(d["remember"])}</div></div></div>')
    return (f'<div class="card"><div class="row"><div class="chip">உங்க பதில் என்ன?</div></div>'
            f'<div class="center"><div class="t" data-fit="80,40" style="height:400px;display:flex;align-items:center;'
            f'text-align:center;justify-content:center">{_e(d["question"])}</div>'
            f'<div class="sub">கமெண்ட்ல சொல்லுங்க. தினமும் வர ஃபாலோ பண்ணுங்க!</div></div></div>')


def segments_from_script(s):
    """The 8 segments in the order they are spoken: [(part name, kind, data)]."""
    cards = s["cards"]
    segs = [("hook", "hook", {"headline": s["headline"]})]
    for i, c in enumerate(cards[:5], 1):
        segs.append((f"f{i}", "fact", {"n": i, "title": c.get("title", ""), "detail": c.get("detail", ""),
                                       "big": c.get("big", "")}))
    segs.append(("tip", "tip", {"remember": s["remember"]}))
    segs.append(("outro", "outro", {"question": s["quiz"]}))
    return segs


def render_pngs(segs, bg_images, workdir, today):
    """One background PNG (blurred picture) and one transparent card PNG per segment. Returns [(bg, fg)]."""
    from playwright.sync_api import sync_playwright

    workdir = Path(workdir)
    out = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")   # the Chrome that GitHub runners already have
        except Exception:
            browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        for i, (name, kind, d) in enumerate(segs):
            bg_img = Path(bg_images[min(i, len(bg_images) - 1)]).resolve()
            doc = (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS % {'top': TOP, 'h': HEIGHT}}</style></head>"
                   f"<body><div id='bg' style=\"background-image:url('{bg_img.as_uri()}')\"></div><div id='bgshade'></div>"
                   f"<div id='fg'>{_card(kind, d, today)}</div></body></html>")
            hp = workdir / f"card_{name}.html"
            hp.write_text(doc, encoding="utf-8")
            page.goto(hp.resolve().as_uri())
            page.evaluate("document.fonts.ready")
            page.evaluate(JS)
            bg_png, fg_png = workdir / f"card_{name}_bg.png", workdir / f"card_{name}_fg.png"
            page.evaluate("document.getElementById('fg').style.visibility='hidden'")
            page.screenshot(path=str(bg_png))
            page.evaluate("document.getElementById('fg').style.visibility='visible';"
                          "document.getElementById('bg').style.display='none';"
                          "document.getElementById('bgshade').style.display='none';"
                          "document.documentElement.style.background='transparent';document.body.style.background='transparent'")
            page.screenshot(path=str(fg_png), omit_background=True)
            out.append((bg_png, fg_png))
        browser.close()
    return out


def _run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError("ffmpeg failed: " + p.stderr[-600:])


def render_cards_video(s, starts, total, workdir, today, bg_images):
    """Builds the silent picture track (mp4, 1080x1920, 30 fps, `total` seconds) and returns its path."""
    workdir = Path(workdir)
    segs = segments_from_script(s)
    pngs = render_pngs(segs, bg_images, workdir, today)
    names = [n for n, _, _ in segs]
    begin = [max(starts[n] - 0.1, 0.0) for n in names]
    begin[0] = 0.0
    ends = begin[1:] + [total]
    clips = []
    for i, ((bg, fg), b, e) in enumerate(zip(pngs, begin, ends)):
        d = max(e - b, 0.8)
        frames = int(d * 30) + 2
        z = "min(zoom+0.0005,1.12)" if i % 2 == 0 else "if(eq(on,1),1.12,max(zoom-0.0005,1.0))"
        bgclip = workdir / f"cbg{i}.mp4"
        _run(["ffmpeg", "-y", "-i", str(bg), "-vf",
              f"scale=1296:2304,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=30,"
              f"format=yuv420p", "-t", f"{d:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(bgclip)])
        clip = workdir / f"cclip{i}.mp4"
        _run(["ffmpeg", "-y", "-i", str(bgclip), "-loop", "1", "-framerate", "30", "-t", f"{d:.2f}", "-i", str(fg),
              "-filter_complex",
              "[1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[f];"
              "[0:v][f]overlay=x=0:y='if(lt(t,0.35),70*(1-t/0.35),0)':format=auto:shortest=1,format=yuv420p[v]",
              "-map", "[v]", "-t", f"{d:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(clip)])
        clips.append(clip)
    lst = workdir / "cards_list.txt"
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    out = workdir / "cards.mp4"
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out
