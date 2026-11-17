"""Cut a vertical YouTube Short out of a finished long story video (owner's choice, 2026-11-17: option 1, cut from the long video).

usage: python tools/story/shorts_cut.py <video.mp4> <name> <first_shot> <last_shot> "<hook text>" <out.mp4>
 - shot boundaries are found from the hard cuts of the finished video (every shot is a new picture); it stops if the count
   does not match the script (shots + exam cards), so a wrong cut is never made.
 - result: 1080x1920, the 16:9 picture in the middle over a blurred copy of itself, the hook on top, the spoken line as a
   caption under the picture, and a "full video" strip at the bottom. Voice and music are kept as they are.
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

video, name, a, b, hook, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], Path(sys.argv[6])
data = json.loads(Path(f"tools/story/{name}.json").read_text(encoding="utf-8"))
shots = data["shots"]
total = len(shots) + len(data.get("exam_cards") or []) + 2   # script shots + intro card + exam cards + outro card
p = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-vf", "select='gt(scene,0.1)',showinfo", "-an", "-f", "null", "-"],
                   capture_output=True, text=True)
cuts = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", p.stderr)]
if len(cuts) != total - 1:
    sys.exit(f"found {len(cuts)} cuts but expected {total - 1}: refusing to cut")
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                           capture_output=True, text=True).stdout)
starts = [0.0] + cuts            # start of shot k (1-based) = starts[k-1]
ends = cuts + [dur]
t0, t1 = starts[a - 1], ends[b - 1]
length = t1 - t0
print(f"shots {a}-{b}: {t0:.2f}s to {t1:.2f}s ({length:.1f}s)")
if length > 58:
    sys.exit("longer than 58 s: pick fewer shots")
part = re.search(r"(\d+)$", name).group(1)
tmp = Path(tempfile.mkdtemp())

def box(css, html):
    return f'<div style="{css}">{html}</div>'

CSS = """body{margin:0;width:1080px;height:1920px;background:transparent;font-family:'Noto Sans Tamil',sans-serif}
.t{position:absolute;left:40px;right:40px;top:150px;text-align:center;font-size:96px;font-weight:900;color:#ffd21f;line-height:1.2;
 text-shadow:5px 5px 0 #000,-5px 5px 0 #000,5px -5px 0 #000,-5px -5px 0 #000}
.c{position:absolute;left:50px;right:50px;top:1300px;text-align:center;font-size:54px;font-weight:800;color:#fff;line-height:1.35;
 text-shadow:4px 4px 0 #000,-4px 4px 0 #000,4px -4px 0 #000,-4px -4px 0 #000}
.f{position:absolute;left:60px;right:60px;bottom:50px;text-align:center;font-size:44px;font-weight:900;color:#fff;background:#d81818;
 border:5px solid #fff;border-radius:26px;padding:14px 10px;line-height:1.3}"""
pages = [("hook", f'<div class="t">{hook}</div>')]
for k in range(a, b + 1):
    pages.append((f"c{k}", f'<div class="c">{shots[k - 1]["nar"]}</div>'))
pages.append(("foot", f'<div class="f">முழு வீடியோ பாருங்கள்<br>தமிழ்நாட்டு வரலாறு பகுதி {part} | TNPSC Bites</div>'))
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={"width": 1080, "height": 1920})
    for nm, html in pages:
        pg.set_content(f"<html><style>{CSS}</style><body>{html}</body></html>")
        pg.screenshot(path=str(tmp / f"{nm}.png"), omit_background=True)
    br.close()

inputs = ["-ss", f"{t0:.3f}", "-t", f"{length:.3f}", "-i", video]
names = ["hook"] + [f"c{k}" for k in range(a, b + 1)] + ["foot"]
for nm in names:
    inputs += ["-i", str(tmp / f"{nm}.png")]
fc = ("[0:v]split[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:6,eq=brightness=-0.18[b];"
      "[fg]scale=1080:-2[f];[b][f]overlay=0:(H-h)/2[v0]")
last = "v0"
idx = 1
def add(png_idx, en, i):
    global fc, last
    fc += f";[{last}][{png_idx}:v]overlay=0:0:enable='{en}'[v{i}]"
    last = f"v{i}"
n = 1
add(1, f"between(t,0,{length:.3f})", n); n += 1                                 # hook, all the time
for k in range(a, b + 1):
    s0, s1 = starts[k - 1] - t0, ends[k - 1] - t0
    add(1 + (k - a) + 1, f"between(t,{s0:.3f},{s1:.3f})", n); n += 1
add(len(names), f"gte(t,{max(length - 5, 0):.3f})", n)                          # footer strip in the last 5 seconds
subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", fc, "-map", f"[{last}]", "-map", "0:a",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                "-t", f"{length:.3f}", "-movflags", "+faststart", str(out)], check=True, capture_output=True)
print("short ready:", out, f"{out.stat().st_size // 1024} KB")
