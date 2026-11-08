"""News-card video for the current-affairs Shorts (HTML/CSS cards drawn by a browser, joined by ffmpeg).

Why a browser: it wraps and shrinks Tamil text to fit its box (see fit() below), so words never overlap or run
off the card. Each part of the voiceover (hook, fact 1-5, outro) gets one card; the card slides in
exactly when that part of the voice starts. The channel header and the LIKE/SUBSCRIBE buttons are added
afterwards by pipeline.py (same as the Manim aptitude video). There are NO running subtitles: instead the text of
each card is dim at first and a soft golden light sweeps down over it while that part is spoken, so the lit text
shows where the voice is (see _lit_clip()).

Needs:  pip install playwright  (it uses the Chrome that GitHub runners already have, or `playwright install chromium`)
        and the font "Noto Sans Tamil" (apt: fonts-noto-core, already installed by daily.yml).
"""
import html
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

W, H = 1080, 1920
TOP, HEIGHT = 480, 900          # the card area: below the header panel, above the LIKE / SUBSCRIBE buttons (y 480-1380)

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:var(--page);
  font-family:'Noto Sans Tamil','Latha','Nirmala UI','FreeSans',sans-serif;color:#fff}
#bg{position:absolute;inset:0;background-size:cover;background-position:center;filter:blur(9px) brightness(var(--bgbright)) saturate(1.1);
  transform:scale(1.08)}
#bgshade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(var(--shade),.55),rgba(var(--shade),.15) 40%%,rgba(var(--shade),.65))}
#fg{position:absolute;left:40px;top:%(top)dpx;width:1000px;height:%(h)dpx}
.card{width:100%%;height:100%%;border-radius:var(--radius);padding:30px 36px;display:flex;flex-direction:column;gap:18px;
  background:linear-gradient(160deg,var(--c1),var(--c2));border:var(--bw) var(--bstyle) var(--border);
  box-shadow:0 18px 60px rgba(0,0,0,.45)}
.row{display:flex;align-items:center;justify-content:space-between;height:62px;flex:none}
.chip{background:var(--accent);color:var(--onaccent);font-weight:800;font-size:34px;padding:6px 26px;border-radius:var(--chip);white-space:nowrap}
.dots{display:flex;gap:12px}
.dot{width:20px;height:20px;border-radius:50%%;background:var(--dot)}
.dot.on{background:var(--accent)}.dot.cur{background:var(--good);transform:scale(1.35)}
.t{font-weight:800;line-height:1.3;overflow:hidden;color:var(--title);flex:none}
.big{font-weight:900;line-height:1.15;overflow:hidden;color:var(--bigc);flex:none;text-align:center;
  background:var(--bigbg);border-radius:22px;display:flex;align-items:center;justify-content:center}
.d{font-weight:500;line-height:1.45;overflow:hidden;color:var(--body);flex:1;min-height:0}
.center{flex:1;display:flex;flex-direction:column;justify-content:center;gap:26px;min-height:0}
.sub{font-weight:700;font-size:38px;color:var(--good);text-align:center;flex:none}
body.dim .t,body.dim .d,body.dim .big,body.dim .sub{opacity:var(--dimop)}
body.lit .card{background:none !important;border-color:transparent !important;box-shadow:none !important}
body.lit .chip,body.lit .dots,body.lit .row{visibility:hidden}
body.lit .big{background:none !important}
.strip{position:absolute;left:20px;top:920px;width:880px;text-align:center;font-weight:800;font-size:44px;line-height:1.25;color:#fff;
  text-shadow:0 3px 12px rgba(0,0,0,.85),0 0 4px rgba(0,0,0,.9)}
body.lit .strip{visibility:hidden}
body.lit .t,body.lit .d,body.lit .big,body.lit .sub{text-shadow:0 0 12px rgba(var(--glow),.95),0 0 30px rgba(var(--glow),.6)}
"""

# A different look for each video, chosen at random (set the repo variable CARD_THEME to a theme name to force one).
# c1/c2: card gradient, border, accent: chips / dots / numbers, good: the "current" dot and subtitle line, glow: the light.
THEMES = {
    "navy-gold": dict(page="#0B1B3A", shade="11,27,58", c1="rgba(18,48,107,.93)", c2="rgba(11,27,58,.93)", border="rgba(255,201,60,.85)",
                      accent="#FFC93C", onaccent="#0B1B3A", good="#3DDC84", title="#fff", body="#E8EEFF", bigc="#FFC93C",
                      glow="255,214,102", dot="rgba(255,255,255,.28)", bigbg="rgba(255,255,255,.08)", dimop=".55",
                      radius="36px", bw="3px", bstyle="solid", chip="40px", bgbright=".5"),
    "emerald": dict(page="#06261C", shade="6,38,28", c1="rgba(14,92,66,.94)", c2="rgba(6,38,28,.94)", border="rgba(160,255,200,.8)",
                    accent="#7CF0B0", onaccent="#06261C", good="#FFD866", title="#fff", body="#E4FFF1", bigc="#B8FFD9",
                    glow="160,255,200", dot="rgba(255,255,255,.28)", bigbg="rgba(255,255,255,.09)", dimop=".55",
                    radius="52px", bw="3px", bstyle="solid", chip="14px", bgbright=".45"),
    "maroon-gold": dict(page="#2A0A12", shade="42,10,18", c1="rgba(122,22,44,.94)", c2="rgba(52,8,20,.95)", border="rgba(255,196,90,.9)",
                        accent="#FFC45A", onaccent="#3A0A16", good="#7BE0C3", title="#FFF6E6", body="#FFE9DA", bigc="#FFC45A",
                        glow="255,200,110", dot="rgba(255,255,255,.28)", bigbg="rgba(255,200,110,.12)", dimop=".55",
                        radius="22px", bw="5px", bstyle="double", chip="10px", bgbright=".42"),
    "violet-neon": dict(page="#150A33", shade="21,10,51", c1="rgba(70,34,150,.93)", c2="rgba(24,10,60,.95)", border="rgba(120,230,255,.85)",
                        accent="#5CE1FF", onaccent="#150A33", good="#FF8AD8", title="#fff", body="#EDE6FF", bigc="#5CE1FF",
                        glow="120,230,255", dot="rgba(255,255,255,.3)", bigbg="rgba(92,225,255,.12)", dimop=".55",
                        radius="64px", bw="3px", bstyle="solid", chip="40px", bgbright=".42"),
    "teal-orange": dict(page="#052A30", shade="5,42,48", c1="rgba(9,92,104,.94)", c2="rgba(4,36,42,.95)", border="rgba(255,150,70,.9)",
                        accent="#FF9A47", onaccent="#052A30", good="#B9F2FF", title="#fff", body="#DFF8FC", bigc="#FFB170",
                        glow="255,176,110", dot="rgba(255,255,255,.28)", bigbg="rgba(255,154,71,.14)", dimop=".55",
                        radius="30px", bw="4px", bstyle="dashed", chip="40px", bgbright=".48"),
    "cream-paper": dict(page="#2B2418", shade="43,36,24", c1="rgba(255,248,230,.97)", c2="rgba(255,236,196,.97)", border="rgba(196,82,28,.95)",
                        accent="#D9531E", onaccent="#FFF8E6", good="#1E8A5A", title="#2A1708", body="#3F2A14", bigc="#C4401A",
                        glow="255,140,40", dot="rgba(60,40,20,.25)", bigbg="rgba(196,82,28,.10)", dimop=".5",
                        radius="26px", bw="6px", bstyle="solid", chip="8px", bgbright=".5"),
    "charcoal-lime": dict(page="#0C0F10", shade="12,15,16", c1="rgba(34,40,42,.95)", c2="rgba(12,15,16,.96)", border="rgba(170,255,60,.9)",
                          accent="#B4FF3C", onaccent="#0C0F10", good="#FFD23C", title="#fff", body="#E9EEF0", bigc="#B4FF3C",
                          glow="190,255,90", dot="rgba(255,255,255,.26)", bigbg="rgba(180,255,60,.10)", dimop=".5",
                          radius="14px", bw="4px", bstyle="solid", chip="6px", bgbright=".4"),
}


def pick_theme():
    import os
    import random
    name = (os.environ.get("CARD_THEME") or "").strip().lower()
    if name not in THEMES:
        name = random.choice(list(THEMES))
    print(f"card theme for this video: {name}", flush=True)
    return name, THEMES[name]


def _root(theme):
    return ":root{" + ";".join(f"--{k}:{v}" for k, v in theme.items()) + "}"


BOUNDS_JS = """
() => {
  let a = 1e9, b = 0;
  document.querySelectorAll('.t,.d,.big,.sub').forEach(e => {
    if (!e.textContent.trim()) return;
    const r = document.createRange(); r.selectNodeContents(e);
    const q = r.getBoundingClientRect();
    if (q.height > 0) { a = Math.min(a, q.top); b = Math.max(b, q.bottom); }
  });
  return [a, b];
}
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


STRIP_TEXT = {   # one clear call to action under the card (YouTube covers the bottom and the right edge, so this sits just under the card)
    "hook": "கடைசியில் ஒரு கேள்வி இருக்கு!",
    "fact": "தினமும் புதிய வீடியோ • SUBSCRIBE",
    "outro": "நண்பர்களுக்கு SHARE பண்ணுங்க",
}


def _strip(kind):
    return f'<div class="strip">{_e(STRIP_TEXT.get(kind, ""))}</div>'


def _dots(i, n=5):
    return "".join(f'<div class="dot {"cur" if k == i else ("on" if k < i else "")}"></div>' for k in range(n))


def _card(kind, d, today):
    """HTML of the card for one segment. kind: hook | fact | outro."""
    if kind == "hook":
        return (f'<div class="card"><div class="row"><div class="chip">{_e(d.get("chip") or "நடப்பு நிகழ்வுகள்")}</div>'
                f'</div>'
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
    return (f'<div class="card"><div class="row"><div class="chip">உங்க பதில் என்ன?</div></div>'
            f'<div class="center"><div class="t" data-fit="80,40" style="height:400px;display:flex;align-items:center;'
            f'text-align:center;justify-content:center">{_e(d["question"])}</div>'
            f'<div class="sub">கமெண்ட்ல சொல்லுங்க. தினமும் ஃபாலோ பண்ணுங்க!</div></div></div>')


def segments_from_script(s):
    """The 8 segments in the order they are spoken: [(part name, kind, data)]."""
    cards = s["cards"]
    segs = [("hook", "hook", {"headline": s["headline"], "chip": s.get("chip", "")})]
    for i, c in enumerate(cards[:5], 1):
        segs.append((f"f{i}", "fact", {"n": i, "title": c.get("title", ""), "detail": c.get("detail", ""),
                                       "big": c.get("big", "")}))
    segs.append(("outro", "outro", {"question": s["quiz"]}))
    return segs


def render_pngs(segs, bg_images, workdir, today, theme=None):
    """Per segment: the blurred background, the normal card, the card with dim text, the lit text alone, and the
    vertical range of the text. Returns [(bg, fg, dim, lit, (y0, y1))]."""
    from playwright.sync_api import sync_playwright

    workdir = Path(workdir)
    out = []
    root = _root(theme or THEMES["navy-gold"])
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")   # the Chrome that GitHub runners already have
        except Exception:
            browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        for i, (name, kind, d) in enumerate(segs):
            bg_img = Path(bg_images[min(i, len(bg_images) - 1)]).resolve()
            doc = (f"<!doctype html><html><head><meta charset='utf-8'><style>{root}{CSS % {'top': TOP, 'h': HEIGHT}}</style></head>"
                   f"<body><div id='bg' style=\"background-image:url('{bg_img.as_uri()}')\"></div><div id='bgshade'></div>"
                   f"<div id='fg'>{_card(kind, d, today)}{_strip(kind)}</div></body></html>")
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
            bounds = page.evaluate(BOUNDS_JS)
            dim_png, lit_png = workdir / f"card_{name}_dim.png", workdir / f"card_{name}_lit.png"
            page.evaluate("document.body.classList.add('dim')")
            page.screenshot(path=str(dim_png), omit_background=True)
            page.evaluate("document.body.classList.remove('dim');document.body.classList.add('lit')")
            page.screenshot(path=str(lit_png), omit_background=True)
            out.append((bg_png, fg_png, dim_png, lit_png, bounds))
        browser.close()
    return out


def _run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError("ffmpeg failed: " + p.stderr[-600:])


def _lit_clip(bgclip, dim, lit, bounds, d, out):
    """Card clip with the lighting effect: the card (dim text) slides in, then a soft golden light sweeps down over
    the text from the first line to the last while the part is spoken. The light is a gray mask video (made small
    and scaled up, so it is cheap) that decides how much of the 'lit text' picture shows on top of the dim card."""
    y0, y1 = bounds if bounds and 0 < bounds[0] < bounds[1] < H else (TOP, TOP + HEIGHT)
    f = 5.0                                    # soft edge of the light, in mask pixels (1 mask pixel = 10 screen pixels)
    y0s, y1s = y0 / 10.0, y1 / 10.0
    t0 = 0.45                                  # start after the card has slid in
    t1 = max(d - 0.5, t0 + 0.8)                # finish just before the next card
    expr = f"255*clip(({y0s:.2f}+({y1s - y0s + f:.2f})*clip((T-{t0:.2f})/{t1 - t0:.2f},0,1)-Y)/{f:.1f},0,1)"
    slide = "if(lt(t,0.35),70*(1-t/0.35),0)"
    fc = (f"[1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[dim];"
          f"[2:v]format=rgba,split[l1][l2];[l2]alphaextract[la];"
          f"[3:v]format=gray,geq=lum='{expr}',scale={W}:{H}:flags=bicubic,format=gray[mk];"
          f"[la][mk]blend=all_mode=multiply,format=gray[a2];"
          f"[l1][a2]alphamerge,fade=t=in:st=0:d=0.35:alpha=1[lit];"
          f"[0:v][dim]overlay=x=0:y='{slide}':format=auto:shortest=1[t1];"
          f"[t1][lit]overlay=x=0:y='{slide}':format=auto:shortest=1,format=yuv420p[v]")
    _run(["ffmpeg", "-y", "-i", str(bgclip),
          "-loop", "1", "-framerate", "30", "-t", f"{d:.2f}", "-i", str(dim),
          "-loop", "1", "-framerate", "30", "-t", f"{d:.2f}", "-i", str(lit),
          "-f", "lavfi", "-i", f"color=c=black:s={W // 10}x{H // 10}:r=30:d={d:.2f}",
          "-filter_complex", fc, "-map", "[v]", "-t", f"{d:.2f}", "-r", "30",
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(out)])


def render_cards_video(s, starts, total, workdir, today, bg_images):
    """Builds the silent picture track (mp4, 1080x1920, 30 fps, `total` seconds) and returns its path."""
    workdir = Path(workdir)
    segs = segments_from_script(s)
    pngs = render_pngs(segs, bg_images, workdir, today, pick_theme()[1])
    names = [n for n, _, _ in segs]
    begin = [max(starts[n] - 0.1, 0.0) for n in names]
    begin[0] = 0.0
    ends = begin[1:] + [total]
    def make_clip_i(args):
        i, (bg, fg, dim, lit, bounds), b, e = args
        d = max(e - b, 0.8)
        frames = int(d * 30) + 2
        z = "min(zoom+0.0005,1.12)" if i % 2 == 0 else "if(eq(on,1),1.12,max(zoom-0.0005,1.0))"
        bgclip = workdir / f"cbg{i}.mp4"
        _run(["ffmpeg", "-y", "-threads", "2", "-i", str(bg), "-vf",
              f"scale=1296:2304,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=30,"
              f"format=yuv420p", "-t", f"{d:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(bgclip)])
        clip = workdir / f"cclip{i}.mp4"
        try:
            _lit_clip(bgclip, dim, lit, bounds, d, clip)
            return clip
        except RuntimeError as err:   # never lose the video because of the light effect: fall back to the plain card
            print(f"light effect failed for card {i}, using the plain card: {str(err)[-200:]}", flush=True)
        _run(["ffmpeg", "-y", "-i", str(bgclip), "-loop", "1", "-framerate", "30", "-t", f"{d:.2f}", "-i", str(fg),
              "-filter_complex",
              "[1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1[f];"
              "[0:v][f]overlay=x=0:y='if(lt(t,0.35),70*(1-t/0.35),0)':format=auto:shortest=1,format=yuv420p[v]",
              "-map", "[v]", "-t", f"{d:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(clip)])
        return clip

    # the 8 cards are independent: build them three at a time (the runner has 4 CPU cores)
    with ThreadPoolExecutor(max_workers=3) as pool:
        clips = list(pool.map(make_clip_i, [(i, p, b, e) for i, (p, b, e) in enumerate(zip(pngs, begin, ends))]))
    lst = workdir / "cards_list.txt"
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    out = workdir / "cards.mp4"
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out
