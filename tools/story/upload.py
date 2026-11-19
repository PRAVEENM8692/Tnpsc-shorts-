"""Makes the thumbnail for a finished story video and (UPLOAD=1) uploads the video to YouTube with title, description,
tags and the thumbnail. The video comes from the story's side branch (story-out for delhi1, story-<name> for the others). Privacy follows the YT_PRIVACY setting like the Shorts."""
import json
import base64, os, subprocess, sys
from pathlib import Path

sys.path.insert(0, ".")
import pipeline as P

NAME = os.environ.get("NAME") or "delhi1"
PLAYLIST = "தமிழ்நாட்டு வரலாறு கதைகள் | Long Videos" if os.environ.get("NAME", "").startswith("tn") else "TNPSC வரலாறு கதைகள் | Long Videos"   # every Long story video goes into this one playlist (made when missing)
if os.environ.get("SHORT_THUMB_FIX"):   # "k:videoId,..." - replace a rollout thumbnail on a Short with a clean frame of the Short itself (no text)
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    import seo_meta
    yt = build("youtube", "v3", credentials=Credentials(None, refresh_token=P.env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
               client_id=P.env("YT_CLIENT_ID"), client_secret=P.env("YT_CLIENT_SECRET"), scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]))
    _sh = json.loads(Path(f"tools/story/{NAME}.json").read_text(encoding="utf-8"))["shorts"]
    for item in os.environ["SHORT_THUMB_FIX"].split(","):
        k, vid_ = item.split(":"); a, b, hook, topic = _sh[int(k) - 1]
        out = OUT / f"{NAME}_fix{k}.mp4"; jpg = OUT / f"{NAME}_fix{k}.jpg"
        subprocess.run([sys.executable, "tools/story/shorts_cut.py", str(VIDEO), NAME, str(a), str(b), hook, str(out)], check=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", "1.0", "-i", str(out), "-frames:v", "1", "-q:v", "2", str(jpg)], check=True)
        P.log(f"clean thumbnail for {vid_}: {seo_meta.set_thumbnail(yt, vid_, jpg)}")
    sys.exit(0)
if os.environ.get("DELETE_IDS"):   # remove the listed videos from the channel (owner asked)
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    yt = build("youtube", "v3", credentials=Credentials(None, refresh_token=P.env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
               client_id=P.env("YT_CLIENT_ID"), client_secret=P.env("YT_CLIENT_SECRET"), scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]))
    for v in os.environ["DELETE_IDS"].split(","):
        try:
            yt.videos().delete(id=v.strip()).execute(); P.log(f"deleted {v.strip()}")
        except Exception as e:
            P.log(f"delete FAILED {v.strip()}: {str(e)[:150]}")
    sys.exit(0)
if os.environ.get("PLAYLIST_ONLY_ID"):   # a video that is already on YouTube: only put it into the playlist, nothing else
    P.add_to_playlists(os.environ["PLAYLIST_ONLY_ID"].strip(), [PLAYLIST])
    sys.exit(0)
OUT = Path("out/story"); OUT.mkdir(parents=True, exist_ok=True)
VIDEO = OUT / f"{NAME}.mp4"
BRANCH = "story-out" if NAME == "delhi1" else f"story-{NAME}"
subprocess.run(["git", "fetch", "-q", "origin", BRANCH], check=True)
VIDEO.write_bytes(subprocess.run(["git", "show", f"FETCH_HEAD:{NAME}.mp4"], check=True, capture_output=True).stdout)


def upload_shorts(vid):
    # Owner's rule (2026-11-17): when a Long video is uploaded, its Shorts go up with it (same privacy), no separate approval.
    import json
    shorts = json.loads(Path(f"tools/story/{NAME}.json").read_text(encoding="utf-8")).get("shorts", []) if Path(f"tools/story/{NAME}.json").exists() else []
    for k, (a, b, hook, topic) in enumerate(shorts, 1):
        try:
            out = OUT / f"{NAME}_short{k}.mp4"
            subprocess.run([sys.executable, "tools/story/shorts_cut.py", str(VIDEO), NAME, str(a), str(b), hook, str(out)], check=True)
            sdesc = f"{topic} - {hook}\n\nமுழு வீடியோ: https://youtube.com/watch?v={vid}\n\nTNPSC Bites சேனலை SUBSCRIBE செய்யுங்கள்.\n\n#Shorts #TNPSC #தமிழ்நாட்டுவரலாறு #TNPSCBites"
            sid = P.upload(out, f"{hook} | {topic} #Shorts", sdesc, ["TNPSC", "TNPSC Bites", "Tamil Nadu history", topic, "Shorts"])
            (OUT / "uploaded.txt").write_text(((OUT / "uploaded.txt").read_text() if (OUT / "uploaded.txt").exists() else "") + f"\nshort{k}: https://youtube.com/shorts/{sid}")
        except Exception as e:   # a failed Short never undoes the Long video
            P.log(f"short {k} skipped: {e}")

if os.environ.get("SHORTS_ONLY_ID"):   # Long video already on YouTube: only cut and upload its Shorts
    upload_shorts(os.environ["SHORTS_ONLY_ID"].strip())
    sys.exit(0)


def pic(n):   # picture n from the story-out branch (whole square one if it exists, else the first cropped one)
    for folder in ("sq", "old", "img"):
        r = subprocess.run(["git", "show", f"FETCH_HEAD:{folder}/{n:02d}.jpg"], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 5000:
            return "data:image/jpeg;base64," + base64.b64encode(r.stdout).decode()
    raise SystemExit(f"picture {n} not found")


if NAME == "delhi1":
    LEFT, RIGHT, BIG, SUB = pic(3), pic(17), "அடிமை ➜ அரசன்!", "டெல்லி சுல்தானியம் | பகுதி 1"
elif NAME == "delhi3":   # the scholar-king (left, grey) and the long march of a whole city (right)
    LEFT, RIGHT, BIG, SUB = pic(1), pic(25), "மேதையா? முட்டாளா?", "டெல்லி சுல்தானியம் | பகுதி 3"
elif NAME == "delhi4":   # the proud last sultan (left, grey) and the man who ended the sultanate (right)
    LEFT, RIGHT, BIG, SUB = pic(45), pic(43), "ஒரே நாளில் முடிந்தது!", "டெல்லி சுல்தானியம் | பகுதி 4"
elif NAME == "tn1":   # three kings, three panels: Chera bow, Chola tiger, Pandya fish
    LEFT, RIGHT, BIG, SUB = pic(6), pic(8), "மூவேந்தர்?", "தமிழ்நாட்டு வரலாறு | பகுதி 1"
    MID = pic(7)
elif NAME == "tn2":   # half dark, half light: the mysterious Kalabhras (left) and the Mamallapuram monuments (right)
    import json as _json
    _t = _json.loads(Path("tools/story/tn2.json").read_text(encoding="utf-8"))["thumb"]
    LEFT, RIGHT, BIG, SUB = pic(_t[0]), pic(_t[1]), "இருண்ட காலமா?", "தமிழ்நாட்டு வரலாறு | பகுதி 2"
elif NAME == "tn3":   # tn3: whole temple picture behind, king in a tilted gold frame on the right, big "no crane?" question on the left
    import json as _json
    _t = _json.loads(Path("tools/story/tn3.json").read_text(encoding="utf-8"))["thumb"]
    LEFT, RIGHT, BIG, SUB = pic(_t[0]), pic(_t[1]), "கிரேன் இல்லாமல்?", "தமிழ்நாட்டு வரலாறு | பகுதி 3"
elif NAME == "tn4":   # tn4: two stacked wide pictures (the Ganga march above, the fleet below) split by a slanted red band with the headline
    import json as _json
    _t = _json.loads(Path("tools/story/tn4.json").read_text(encoding="utf-8"))["thumb"]
    LEFT, RIGHT, BIG, SUB = pic(_t[0]), pic(_t[2]), "கங்கை ➜ கடாரம்", "தமிழ்நாட்டு வரலாறு | பகுதி 4"
else:   # delhi2: the gentle old king (left, grey) and the man who killed him (right)
    LEFT, RIGHT, BIG, SUB = pic(11), pic(6), "மாமனாரையே கொன்றான்!", "டெல்லி சுல்தானியம் | பகுதி 2"
BOY, KING = LEFT, RIGHT
HTML = f"""<html><style>
body{{margin:0;width:1280px;height:720px;position:relative;overflow:hidden;font-family:'Noto Sans Tamil',sans-serif;background:#111}}
.l,.r{{position:absolute;top:0;height:720px;background-size:cover;background-position:center}}
.l{{left:0;width:660px;background-image:url({BOY});filter:grayscale(.85) contrast(1.1) brightness(.8);clip-path:polygon(0 0,100% 0,82% 100%,0 100%)}}
.r{{right:0;width:700px;background-image:url({KING});filter:saturate(1.35) contrast(1.08);clip-path:polygon(18% 0,100% 0,100% 100%,0 100%)}}
.shade{{position:absolute;left:0;right:0;bottom:0;height:330px;background:linear-gradient(transparent,rgba(0,0,0,.88))}}
.t{{position:absolute;left:0;right:0;bottom:92px;text-align:center;font-size:{140 if NAME == 'delhi1' else 118}px;font-weight:900;color:#ffd21f;line-height:1.1;
 text-shadow:5px 5px 0 #000,-5px 5px 0 #000,5px -5px 0 #000,-5px -5px 0 #000,0 10px 24px rgba(0,0,0,.8)}}
.s{{position:absolute;left:0;right:0;bottom:24px;text-align:center;font-size:48px;font-weight:800;color:#fff;
 text-shadow:3px 3px 0 #000,-3px 3px 0 #000,3px -3px 0 #000,-3px -3px 0 #000}}
.b{{position:absolute;left:26px;top:24px;background:#e11d1d;color:#fff;font-size:44px;font-weight:900;padding:6px 26px;border-radius:12px;
 border:4px solid #fff;font-family:'DejaVu Sans',sans-serif}}
.q{{position:absolute;left:50%;top:150px;transform:translateX(-50%) rotate(-8deg);font-size:120px;font-weight:900;color:#fff;
 background:#e11d1d;border:6px solid #fff;border-radius:50%;width:150px;height:150px;line-height:146px;text-align:center;
 font-family:'DejaVu Sans',sans-serif;box-shadow:0 8px 20px rgba(0,0,0,.6)}}
</style><body><div class="l"></div><div class="r"></div><div class="shade"></div>
<div class="b">TNPSC</div><div class="q">&#10140;</div>
<div class="t">{BIG}</div><div class="s">{SUB}</div></body></html>"""
HTML2 = f"""<html><style>
body{{margin:0;width:1280px;height:720px;position:relative;overflow:hidden;font-family:'Noto Sans Tamil',sans-serif;background:#111}}
.bg{{position:absolute;inset:0;background:url({RIGHT}) center/cover;filter:saturate(1.25) contrast(1.1)}}
.vig{{position:absolute;inset:0;background:radial-gradient(ellipse at 60% 40%,transparent 35%,rgba(0,0,0,.65) 100%)}}
.rib{{position:absolute;left:0;right:0;bottom:0;height:250px;background:linear-gradient(transparent,rgba(0,0,0,.92) 45%)}}
.yr{{position:absolute;left:34px;top:26px;font-family:'DejaVu Sans',sans-serif;font-size:190px;font-weight:900;color:#ffd21f;line-height:1;
 text-shadow:7px 7px 0 #b3121b,-4px -4px 0 #000,4px -4px 0 #000,-4px 4px 0 #000,0 14px 26px rgba(0,0,0,.8)}}
.in{{position:absolute;right:46px;top:34px;width:290px;height:290px;border-radius:50%;background:url({LEFT}) center/cover;border:9px solid #e11d1d;
 box-shadow:0 0 0 6px #fff,0 12px 30px rgba(0,0,0,.7);filter:grayscale(.9) contrast(1.15)}}
.cr{{position:absolute;right:56px;top:304px;width:270px;text-align:center;background:#e11d1d;color:#fff;font-size:34px;font-weight:900;padding:4px 0;border-radius:10px;border:4px solid #fff}}
.t{{position:absolute;left:30px;right:30px;bottom:74px;text-align:left;font-size:104px;font-weight:900;color:#fff;line-height:1.1;
 text-shadow:5px 5px 0 #000,-5px 5px 0 #000,5px -5px 0 #000,-5px -5px 0 #000}}
.s{{position:absolute;left:30px;bottom:18px;font-size:44px;font-weight:800;color:#ffd21f;text-shadow:3px 3px 0 #000,-3px 3px 0 #000,3px -3px 0 #000,-3px -3px 0 #000}}
.b{{position:absolute;right:30px;bottom:22px;background:#e11d1d;color:#fff;font-size:40px;font-weight:900;padding:4px 22px;border-radius:12px;border:4px solid #fff;font-family:'DejaVu Sans',sans-serif}}
</style><body><div class="bg"></div><div class="vig"></div><div class="rib"></div>
<div class="yr">1526</div><div class="in"></div><div class="cr">கடைசி சுல்தான்</div>
<div class="t">{BIG}</div><div class="s">{SUB}</div><div class="b">TNPSC</div></body></html>"""
HTML3 = f"""<html><style>
body{{margin:0;width:1280px;height:720px;position:relative;overflow:hidden;font-family:'Noto Sans Tamil',sans-serif;background:#111}}
.p{{position:absolute;top:0;height:720px;width:440px;background-size:cover;background-position:center;filter:saturate(1.3) contrast(1.08)}}
.p1{{left:0;background-image:url({LEFT if NAME == 'tn1' else ''});box-shadow:inset 0 0 0 0 #000}}
.p2{{left:420px;background-image:url({MID if NAME == 'tn1' else ''})}}
.p3{{left:840px;background-image:url({RIGHT})}}
.tint1{{position:absolute;left:0;top:0;width:440px;height:720px;background:linear-gradient(transparent 45%,rgba(20,120,50,.75))}}
.tint2{{position:absolute;left:420px;top:0;width:440px;height:720px;background:linear-gradient(transparent 45%,rgba(190,25,25,.75))}}
.tint3{{position:absolute;left:840px;top:0;width:440px;height:720px;background:linear-gradient(transparent 45%,rgba(20,70,190,.75))}}
.d1,.d2{{position:absolute;top:0;width:14px;height:720px;background:#fff;transform:skewX(-6deg)}}
.d1{{left:426px}}.d2{{left:846px}}
.n{{position:absolute;bottom:128px;width:440px;text-align:center;font-size:70px;font-weight:900;color:#fff;text-shadow:4px 4px 0 #000,-4px 4px 0 #000,4px -4px 0 #000,-4px -4px 0 #000}}
.t{{position:absolute;left:0;right:0;top:22px;text-align:center;font-size:130px;font-weight:900;color:#ffd21f;line-height:1.1;
 text-shadow:6px 6px 0 #000,-6px 6px 0 #000,6px -6px 0 #000,-6px -6px 0 #000,0 10px 24px rgba(0,0,0,.8)}}
.s{{position:absolute;left:0;right:0;bottom:22px;text-align:center;font-size:46px;font-weight:800;color:#fff;text-shadow:3px 3px 0 #000,-3px 3px 0 #000,3px -3px 0 #000,-3px -3px 0 #000}}
.b{{position:absolute;left:24px;bottom:24px;background:#e11d1d;color:#fff;font-size:38px;font-weight:900;padding:4px 20px;border-radius:12px;border:4px solid #fff;font-family:'DejaVu Sans',sans-serif}}
</style><body><div class="p p1"></div><div class="p p2"></div><div class="p p3"></div><div class="tint1"></div><div class="tint2"></div><div class="tint3"></div>
<div class="d1"></div><div class="d2"></div>
<div class="n" style="left:0">சேரன்</div><div class="n" style="left:420px">சோழன்</div><div class="n" style="left:840px">பாண்டியன்</div>
<div class="t">{BIG}</div><div class="s">{SUB}</div></body></html>"""
HTML4 = f"""<html><style>
body{{margin:0;width:1280px;height:720px;position:relative;overflow:hidden;font-family:'Noto Sans Tamil',sans-serif;background:#000}}
.l{{position:absolute;left:0;top:0;width:800px;height:720px;background:url({LEFT}) center/cover;filter:grayscale(.9) brightness(.55) contrast(1.25);clip-path:polygon(0 0,100% 0,62% 100%,0 100%)}}
.r{{position:absolute;right:0;top:0;width:800px;height:720px;background:url({RIGHT}) center/cover;filter:saturate(1.45) brightness(1.12) contrast(1.08);clip-path:polygon(38% 0,100% 0,100% 100%,0 100%)}}
.glow{{position:absolute;left:560px;top:0;width:120px;height:720px;background:linear-gradient(90deg,transparent,rgba(255,225,120,.9),transparent);transform:skewX(-9deg);filter:blur(10px)}}
.shade{{position:absolute;left:0;right:0;bottom:0;height:300px;background:linear-gradient(transparent,rgba(0,0,0,.9))}}
.q{{position:absolute;left:46px;top:30px;font-family:'DejaVu Sans',sans-serif;font-size:300px;font-weight:900;color:#ff3030;line-height:1;text-shadow:6px 6px 0 #000,0 0 40px rgba(255,40,40,.7)}}
.t{{position:absolute;left:0;right:0;bottom:84px;text-align:center;font-size:122px;font-weight:900;color:#ffd21f;line-height:1.1;
 text-shadow:6px 6px 0 #000,-6px 6px 0 #000,6px -6px 0 #000,-6px -6px 0 #000,0 10px 24px rgba(0,0,0,.8)}}
.s{{position:absolute;left:0;right:0;bottom:22px;text-align:center;font-size:44px;font-weight:800;color:#fff;text-shadow:3px 3px 0 #000,-3px 3px 0 #000,3px -3px 0 #000,-3px -3px 0 #000}}
.b{{position:absolute;right:26px;top:24px;background:#e11d1d;color:#fff;font-size:42px;font-weight:900;padding:5px 24px;border-radius:12px;border:4px solid #fff;font-family:'DejaVu Sans',sans-serif}}
</style><body><div class="l"></div><div class="r"></div><div class="glow"></div><div class="shade"></div>
<div class="q">?</div><div class="b">TNPSC</div><div class="t">{BIG}</div><div class="s">{SUB}</div></body></html>"""
HTML5 = f"""<html><style>
body{{margin:0;width:1280px;height:720px;position:relative;overflow:hidden;font-family:'Noto Sans Tamil',sans-serif;background:#000}}
.bg{{position:absolute;inset:0;background:url({LEFT}) center/cover;filter:saturate(1.3) brightness(.7) contrast(1.15)}}
.fade{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.88) 0%,rgba(0,0,0,.55) 48%,rgba(0,0,0,0) 75%)}}
.k{{position:absolute;right:46px;top:70px;width:470px;height:560px;background:url({RIGHT}) center/cover;border:10px solid #ffd21f;border-radius:18px;transform:rotate(4deg);box-shadow:0 0 50px rgba(255,200,40,.6),12px 14px 0 rgba(0,0,0,.6);filter:saturate(1.2) contrast(1.05)}}
.t1,.t2{{position:absolute;left:44px;font-size:150px;font-weight:900;line-height:1.05;text-shadow:7px 7px 0 #000,-7px 7px 0 #000,7px -7px 0 #000,-7px -7px 0 #000}}
.t1{{top:150px;color:#fff}} .t2{{top:315px;color:#ffd21f}}
.h{{position:absolute;left:44px;bottom:112px;background:#e11d1d;color:#fff;font-size:62px;font-weight:900;padding:6px 30px;border-radius:14px;border:5px solid #fff}}
.s{{position:absolute;left:44px;bottom:36px;font-size:44px;font-weight:800;color:#fff;text-shadow:3px 3px 0 #000,-3px 3px 0 #000,3px -3px 0 #000,-3px -3px 0 #000}}
.b{{position:absolute;left:44px;top:26px;background:#e11d1d;color:#fff;font-size:42px;font-weight:900;padding:5px 24px;border-radius:12px;border:4px solid #fff;font-family:'DejaVu Sans',sans-serif}}
</style><body><div class="bg"></div><div class="fade"></div><div class="k"></div><div class="b">TNPSC</div>
<div class="t1">கிரேன்</div><div class="t2">இல்லாமல்?</div><div class="h">216 அடி கோபுரம்!</div><div class="s">{SUB}</div></body></html>"""
if NAME == "tn3":
    HTML = HTML5
HTML6 = f"""<html><style>
body{{margin:0;width:1280px;height:720px;position:relative;overflow:hidden;font-family:'Noto Sans Tamil',sans-serif;background:#000}}
.a{{position:absolute;left:0;top:0;width:1280px;height:430px;background:url({LEFT}) center/cover;filter:saturate(1.35) contrast(1.1);clip-path:polygon(0 0,100% 0,100% 62%,0 100%)}}
.c{{position:absolute;left:0;bottom:0;width:1280px;height:430px;background:url({RIGHT}) center/cover;filter:saturate(1.4) contrast(1.1);clip-path:polygon(0 38%,100% 0,100% 100%,0 100%)}}
.band{{position:absolute;left:-40px;right:-40px;top:268px;height:176px;background:#d91414;transform:rotate(-5deg);border-top:8px solid #fff;border-bottom:8px solid #fff;box-shadow:0 14px 40px rgba(0,0,0,.7)}}
.t{{position:absolute;left:0;right:0;top:282px;text-align:center;font-size:132px;font-weight:900;color:#ffe14a;line-height:1.15;transform:rotate(-5deg);
 text-shadow:6px 6px 0 #000,-6px 6px 0 #000,6px -6px 0 #000,-6px -6px 0 #000}}
.s{{position:absolute;left:0;right:0;bottom:20px;text-align:center;font-size:46px;font-weight:800;color:#fff;text-shadow:3px 3px 0 #000,-3px 3px 0 #000,3px -3px 0 #000,-3px -3px 0 #000}}
.b{{position:absolute;left:26px;top:22px;background:#e11d1d;color:#fff;font-size:42px;font-weight:900;padding:5px 24px;border-radius:12px;border:4px solid #fff;font-family:'DejaVu Sans',sans-serif}}
</style><body><div class="a"></div><div class="c"></div><div class="band"></div><div class="t">{BIG}</div><div class="b">TNPSC</div><div class="s">{SUB}</div></body></html>"""
if NAME == "tn4":
    HTML = HTML6
if NAME == "tn2":
    HTML = HTML4
if NAME == "tn1":
    HTML = HTML3
if NAME == "delhi4":   # part 4 uses a different thumbnail layout (full picture, big year, round inset) so the channel does not look like one template
    HTML = HTML2
thumb = OUT / "thumb.jpg"
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.set_content(HTML)
    pg.wait_for_timeout(400)
    pg.screenshot(path=str(thumb), type="jpeg", quality=92)
    b.close()
P.log(f"thumbnail ready: {thumb.stat().st_size // 1024} KB")

TITLE1 = "அடிமையாக விற்கப்பட்டவன் டெல்லியின் அரசனான கதை! | டெல்லி சுல்தானியம் பகுதி 1 | TNPSC"
DESC1 = """சந்தையில் அடிமையாக விற்கப்பட்ட சிறுவன் ஒரு நாள் டெல்லியின் அரசனானான். அவனுக்குப் பிறகு அரியணையில் அமர்ந்த இருவரும் அடிமைகள். அவர்களுக்கு நடுவில் ஒரு பெண்ணும்!

டெல்லி சுல்தானியத்தின் முதல் அத்தியாயமான அடிமை (மம்லுக்) வம்சத்தின் முழுக் கதை, 6 நிமிடத்தில்:
• குத்புதீன் ஐபக் - அடிமையிலிருந்து அரசன், லாக் பக்ஷ், குதுப் மினார்
• இல்துமிஷ் - டங்கா, ஜிட்டால், இக்தா முறை, நாற்பதின்மர் குழு
• ரசியா சுல்தானா - டெல்லியின் முதல் மற்றும் ஒரே பெண் ஆட்சியாளர்
• பால்பன் - இரத்தமும் இரும்பும், சிஜ்தா, பைபோஸ்

எல்லோரும் ரசிக்கக்கூடிய கதை. TNPSC Group 1, 2, 4 தேர்வுக்கும் பயனுள்ளது. வீடியோவின் இறுதியில் 5 முக்கியத் தேர்வுக் குறிப்புகள் உள்ளன.

அடுத்த பகுதி: அலாவுதீன் கில்ஜி, தன் மாமனாரைக் கொன்று அரசனானவன், மதுரை வரை படை அனுப்பியவன். தவறவிடாமல் இருக்க TNPSC Bites சேனலை SUBSCRIBE செய்யுங்கள், LIKE செய்யுங்கள்.

உங்கள் கருத்து: இந்த நான்கு ஆட்சியாளர்களில் உங்களுக்கு மிகவும் பிடித்தவர் யார்? கீழே கமெண்டில் சொல்லுங்கள்!

குறிப்பு: இந்த வீடியோவில் உள்ள படங்களும் குரலும் AI மூலம் உருவாக்கப்பட்டவை. வரலாற்றுத் தகவல்கள் பொதுவான பாடநூல் அறிவின்படி எழுதப்பட்டவை; தேர்வுக்குப் படிக்கும்போது உங்கள் பாடநூலுடன் ஒப்பிட்டுப் பார்க்கவும்.

#TNPSC #DelhiSultanate #டெல்லிசுல்தானியம் #TNPSCHistory #ரசியாசுல்தானா #குதுப்மினார் #TamilHistory #TNPSCBites"""
TAGS1 = ["TNPSC", "Delhi Sultanate", "டெல்லி சுல்தானியம்", "குத்புதீன் ஐபக்", "இல்துமிஷ்", "ரசியா சுல்தானா", "பால்பன்",
        "குதுப் மினார்", "TNPSC history", "Mamluk dynasty", "அடிமை வம்சம்", "Tamil history story", "TNPSC Group 4", "TNPSC Bites"]


TITLE2 = "மாமனாரையே கொன்று அரசனானவன்! மதுரை வரை வந்த படை | டெல்லி சுல்தானியம் பகுதி 2 | TNPSC"
DESC2 = """தன்னை நம்பிய மாமனாரையே கொன்றான். அந்தக் கறையோடு டெல்லி அரியணையில் அமர்ந்தான். ஆனால் அதே மனிதன் மங்கோலியர்களை விரட்டினான், சந்தையில் விலையை நிர்ணயித்தான், அவனுடைய படை தமிழ்நாட்டின் மதுரை வரை வந்தது. அவன் வீரனா, வில்லனா?

டெல்லி சுல்தானியத்தின் இரண்டாம் அத்தியாயமான கில்ஜி வம்சத்தின் முழுக் கதை, 6 நிமிடத்தில்:
• ஜலாலுதீன் கில்ஜி - 1290, கில்ஜி வம்சத்தின் தொடக்கம்
• அலாவுதீன் கில்ஜி - காரா துரோகம், மங்கோலியர் தோல்வி, சந்தைச் சீர்திருத்தம், தாக், சேரா
• மாலிக் கபூர் - தேவகிரி, வாரங்கல், துவாரசமுத்திரம், மதுரை (1311)
• அலாய் தர்வாசா, சிரி கோட்டை, அமீர் குஸ்ரு

எல்லோரும் ரசிக்கக்கூடிய கதை. TNPSC Group 1, 2, 4 தேர்வுக்கும் பயனுள்ளது. வீடியோவின் இறுதியில் 5 முக்கியத் தேர்வுக் குறிப்புகள் உள்ளன.

முந்தைய பகுதி: அடிமை வம்சம் (பகுதி 1). அடுத்த பகுதி: தலைநகரையே தூக்கிக்கொண்டு போன அரசன். தவறவிடாமல் இருக்க TNPSC Bites சேனலை SUBSCRIBE செய்யுங்கள், LIKE செய்யுங்கள்.

உங்கள் கருத்து: அலாவுதீன் வீரனா, வில்லனா? கீழே கமெண்டில் சொல்லுங்கள்!

குறிப்பு: இந்த வீடியோவில் உள்ள படங்களும் குரலும் AI மூலம் உருவாக்கப்பட்டவை. வரலாற்றுத் தகவல்கள் பொதுவான பாடநூல் அறிவின்படி எழுதப்பட்டவை; தேர்வுக்குப் படிக்கும்போது உங்கள் பாடநூலுடன் ஒப்பிட்டுப் பார்க்கவும்.

#TNPSC #DelhiSultanate #டெல்லிசுல்தானியம் #KhaljiDynasty #அலாவுதீன்கில்ஜி #மாலிக்கபூர் #TNPSCHistory #TamilHistory #TNPSCBites"""
TAGS2 = ["TNPSC", "Delhi Sultanate", "டெல்லி சுல்தானியம்", "கில்ஜி வம்சம்", "அலாவுதீன் கில்ஜி", "ஜலாலுதீன் கில்ஜி", "மாலிக் கபூர்",
         "Khalji dynasty", "Alauddin Khalji", "TNPSC history", "Tamil history story", "TNPSC Group 4", "TNPSC Bites"]
TITLE3 = "தலைநகரையே தூக்கிச் சென்ற அரசன்! மேதையா? முட்டாளா? | டெல்லி சுல்தானியம் பகுதி 3 | TNPSC"
DESC3 = """பெரிய அறிவாளி. ஆனால் வரலாறு அவனை முட்டாள் என்கிறது. தலைநகரையே ஆயிரம் கிலோமீட்டர் தூரத்துக்குத் தூக்கிச் சென்றான். வெள்ளிக்குப் பதிலாக செம்பு நாணயம் வெளியிட்டான். அவன் காலத்தில்தான் தெற்கே மதுரை சுல்தானியம், விஜயநகரம், பாமனி அரசுகள் பிறந்தன. அவன் மேதையா? முட்டாளா?

டெல்லி சுல்தானியத்தின் மூன்றாம் அத்தியாயமான துக்ளக் வம்சத்தின் முழுக் கதை, 6 நிமிடத்தில்:
• கியாசுதீன் துக்ளக் - 1320, துக்ளகாபாத், மரக் கூடாரம் இடிந்து மரணம்
• முகமது பின் துக்ளக் - தோவாப் வரி 1326, தலைநகர் தௌலதாபாத் 1327, செப்பு நாணயம் 1329
• இபன் பதூதா 1333, மதுரை சுல்தானியம் 1334, விஜயநகரம் 1336, பாமனி 1347
• பிரோஸ் ஷா துக்ளக் - கால்வாய்கள், ஃபிரோசாபாத், திவான்-இ-கைராத்
• தைமூர் படையெடுப்பு 1398, வம்சத்தின் முடிவு 1413

எல்லோரும் ரசிக்கக்கூடிய கதை. TNPSC Group 1, 2, 4 தேர்வுக்கும் பயனுள்ளது. வீடியோவின் இறுதியில் 5 முக்கியத் தேர்வுக் குறிப்புகள் உள்ளன.

முந்தைய பகுதிகள்: அடிமை வம்சம் (பகுதி 1), கில்ஜி வம்சம் (பகுதி 2). அடுத்த பகுதி: சையது, லோடி வம்சங்கள், பாபர். தவறவிடாமல் இருக்க TNPSC Bites சேனலை SUBSCRIBE செய்யுங்கள், LIKE செய்யுங்கள்.

உங்கள் கருத்து: முகமது பின் துக்ளக் மேதையா? முட்டாளா? கீழே கமெண்டில் சொல்லுங்கள்!

குறிப்பு: இந்த வீடியோவில் உள்ள படங்களும் குரலும் AI மூலம் உருவாக்கப்பட்டவை. வரலாற்றுத் தகவல்கள் பொதுவான பாடநூல் அறிவின்படி எழுதப்பட்டவை; தேர்வுக்குப் படிக்கும்போது உங்கள் பாடநூலுடன் ஒப்பிட்டுப் பார்க்கவும்.

#TNPSC #DelhiSultanate #டெல்லிசுல்தானியம் #TughlaqDynasty #முகமதுபின்துக்ளக் #இபன்பதூதா #TNPSCHistory #TamilHistory #TNPSCBites"""
TAGS3 = ["TNPSC", "Delhi Sultanate", "டெல்லி சுல்தானியம்", "துக்ளக் வம்சம்", "முகமது பின் துக்ளக்", "பிரோஸ் ஷா துக்ளக்", "இபன் பதூதா",
         "Tughlaq dynasty", "Muhammad bin Tughluq", "TNPSC history", "Tamil history story", "TNPSC Group 4", "TNPSC Bites"]
TITLE4 = "ஒரே நாளில் முடிந்த சுல்தானியம்! பானிப்பட் 1526 | டெல்லி சுல்தானியம் பகுதி 4 | TNPSC"
DESC4 = """320 ஆண்டுகள் இந்தியாவை ஆண்ட டெல்லி சுல்தானியம், 1526 ஏப்ரல் 21-ஆம் தேதி ஒரே போரில் முடிவுக்கு வந்தது. ஒரு லட்சம் வீரர்களும் நூற்றுக்கணக்கான யானைகளும் இருந்தும், ஏன் இப்ராகிம் லோடி தோற்றான்? வெறும் 12 ஆயிரம் வீரர்களோடு வந்த பாபர் எப்படி வென்றான்?

டெல்லி சுல்தானியத்தின் நான்காம் மற்றும் கடைசி அத்தியாயம், சுமார் 5 நிமிடத்தில்:
• சையது வம்சம் - கிசர் கான் 1414, சோம்பேறி அரசன் ஆலம் ஷா, "டெல்லியிலிருந்து பாலம் வரை" பழமொழி
• லோடி வம்சம் - பகலோல் லோடி 1451, சிக்கந்தர் லோடி, ஆக்ரா நகரம் 1504, கஸ்-இ-சிக்கந்தரி
• இப்ராகிம் லோடி - தௌலத் கான் லோடி பாபரை அழைத்தது
• முதல் பானிப்பட் போர் 1526 - பீரங்கிகள், துப்பாக்கிகள், மிரண்ட யானைகள்

எல்லோரும் ரசிக்கக்கூடிய கதை. TNPSC Group 1, 2, 4 தேர்வுக்கும் பயனுள்ளது. வீடியோவின் இறுதியில் 5 முக்கியத் தேர்வுக் குறிப்புகள் உள்ளன.

முந்தைய பகுதிகள்: அடிமை வம்சம், கில்ஜி வம்சம், துக்ளக் வம்சம். அடுத்த தொடர்: தமிழ்நாட்டின் வரலாறு. தவறவிடாமல் இருக்க TNPSC Bites சேனலை SUBSCRIBE செய்யுங்கள், LIKE செய்யுங்கள்.

உங்கள் கருத்து: டெல்லி சுல்தானியத்தின் ஐந்து வம்சங்களில் உங்களுக்குப் பிடித்தது எது? கீழே கமெண்டில் சொல்லுங்கள்!

குறிப்பு: இந்த வீடியோவில் உள்ள படங்களும் குரலும் AI மூலம் உருவாக்கப்பட்டவை. வரலாற்றுத் தகவல்கள் பொதுவான பாடநூல் அறிவின்படி எழுதப்பட்டவை; தேர்வுக்குப் படிக்கும்போது உங்கள் பாடநூலுடன் ஒப்பிட்டுப் பார்க்கவும்.

#TNPSC #DelhiSultanate #டெல்லிசுல்தானியம் #FirstBattleOfPanipat #பானிப்பட் #பாபர் #TNPSCHistory #TamilHistory #TNPSCBites"""
TAGS4 = ["TNPSC", "Delhi Sultanate", "டெல்லி சுல்தானியம்", "சையது வம்சம்", "லோடி வம்சம்", "இப்ராகிம் லோடி", "பாபர்",
         "முதல் பானிப்பட் போர்", "First Battle of Panipat", "Lodi dynasty", "TNPSC history", "Tamil history story", "TNPSC Group 4", "TNPSC Bites"]
TITLETN1 = "2000 வருஷம் முன் கட்டிய அணை, இன்றும் ஓடுது! | தமிழ்நாட்டு வரலாறு பகுதி 1 | TNPSC"
DESCTN1 = """தமிழ்நாட்டு வரலாறு, பகுதி 1: சங்க காலம். 2000 வருஷத்துக்கு முன் கரிகால சோழன் கட்டிய கல்லணை இன்றும் தண்ணீர் பாய்ச்சுகிறது. சேரர், சோழர், பாண்டியர் என்ற மூவேந்தர் யார்? சங்க காலத்தின் முழுக் கதை, சுமார் 5 நிமிடத்தில்.

இந்த வீடியோவில்:
• மூவேந்தர் அடையாளம் - வில், புலி, மீன்; பனம்பூ, ஆத்திப்பூ, வேப்பம்பூ
• சங்கம் மற்றும் சங்க நூல்கள் - தொல்காப்பியம், எட்டுத்தொகை, பத்துப்பாட்டு
• கரிகால சோழன் - வெண்ணிப் போர், கல்லணை, பூம்புகார்
• சிலப்பதிகாரம் - கண்ணகி, நெடுஞ்செழியன், செங்குட்டுவன்
• ரோமானிய வணிகம் - முசிறி, கொற்கை, பூம்புகார், அரிக்கமேடு

எல்லோரும் ரசிக்கக்கூடிய கதை. TNPSC Group 1, 2, 4 தேர்வுக்கும் பயனுள்ளது. வீடியோவின் இறுதியில் 5 முக்கியத் தேர்வுக் குறிப்புகள் உள்ளன.

அடுத்த பகுதி: களப்பிரர் மற்றும் பல்லவர். தவறவிடாமல் இருக்க TNPSC Bites சேனலை SUBSCRIBE செய்யுங்கள், LIKE செய்யுங்கள்.

உங்கள் கருத்து: சேரன், சோழன், பாண்டியன் மூவரில் உங்களுக்குப் பிடித்தவர் யார்? கீழே கமெண்டில் சொல்லுங்கள்!

குறிப்பு: இந்த வீடியோவில் உள்ள படங்களும் குரலும் AI மூலம் உருவாக்கப்பட்டவை. சங்க காலத்தின் ஆண்டுகள் வரலாற்றாசிரியர்களிடையே சற்று மாறுபடும். கண்ணகி கதை இலக்கிய மரபு. தேர்வுக்குப் படிக்கும்போது உங்கள் பாடநூலுடன் ஒப்பிட்டுப் பார்க்கவும்.

#TNPSC #தமிழ்நாட்டுவரலாறு #சங்ககாலம் #கல்லணை #கரிகாலசோழன் #சிலப்பதிகாரம் #TNPSCHistory #TamilHistory #TNPSCBites"""
TAGSTN1 = ["TNPSC", "தமிழ்நாட்டு வரலாறு", "சங்க காலம்", "மூவேந்தர்", "கரிகால சோழன்", "கல்லணை", "சிலப்பதிகாரம்", "கண்ணகி",
           "Sangam age", "Tamil Nadu history", "Kallanai", "Karikala Chola", "TNPSC history", "Tamil history story", "TNPSC Group 4", "TNPSC Bites"]
TITLETN2 = "தமிழகத்தின் இருண்ட காலம் உண்மையா? களப்பிரர் முதல் பல்லவர் வரை | தமிழ்நாட்டு வரலாறு பகுதி 2 | TNPSC"
DESCTN2 = """தமிழ்நாட்டு வரலாறு, பகுதி 2: களப்பிரர் மற்றும் பல்லவர். தங்கள் கல்வெட்டுகளையே கிட்டத்தட்ட விட்டுவைக்காத ஒரு வம்சம் தமிழகத்தை ஆண்டது. அவர்களைப் பற்றி நமக்குத் தெரிந்தது எதிரிகள் எழுதியதுதான். இருண்ட காலம் என்று சொல்லப்படுவது உண்மையா? பிறகு வந்த பல்லவர் மாமல்லபுரத்தை எப்படிப் படைத்தார்கள்? சுமார் 4 நிமிடத்தில் முழுக் கதை.

இந்த வீடியோவில்:
• களப்பிரர் - வேள்விக்குடிச் செப்பேடு, இருண்ட காலம் உண்மையா?
• அந்தக் காலத்தின் நூல்கள் - பதினெண் கீழ்க்கணக்கு, புத்ததத்தர், வஜ்ரநந்தி
• பல்லவர் - சிம்மவிஷ்ணு, காஞ்சிபுரம்
• மகேந்திரவர்மன் - மத்தவிலாசப் பிரகசனம், குடைவரைக் கோயில், மண்டகப்பட்டுக் கல்வெட்டு
• நரசிம்மவர்மன் மாமல்லன் - வாதாபி வெற்றி 642, மாமல்லபுரம், பஞ்சரதம், கடற்கரைக் கோயில், யுனெஸ்கோ 1984

எல்லோரும் ரசிக்கக்கூடிய கதை. TNPSC Group 1, 2, 4 தேர்வுக்கும் பயனுள்ளது. வீடியோவின் இறுதியில் 5 முக்கியத் தேர்வுக் குறிப்புகள் உள்ளன.

முந்தைய பகுதி: சங்க காலம். அடுத்த பகுதி: சோழர்களின் எழுச்சி. தவறவிடாமல் இருக்க TNPSC Bites சேனலை SUBSCRIBE செய்யுங்கள், LIKE செய்யுங்கள்.

உங்கள் கருத்து: மகாபலிபுரத்தை நேரில் பார்த்திருக்கிறீர்களா? கீழே கமெண்டில் சொல்லுங்கள்!

குறிப்பு: இந்த வீடியோவில் உள்ள படங்களும் குரலும் AI மூலம் உருவாக்கப்பட்டவை. களப்பிரர் காலம், திருக்குறள் காலம் ஆகியவை வரலாற்றாசிரியர்களிடையே விவாதத்திற்கு உரியவை. தேர்வுக்குப் படிக்கும்போது உங்கள் பாடநூலுடன் ஒப்பிட்டுப் பார்க்கவும்.

#TNPSC #தமிழ்நாட்டுவரலாறு #களப்பிரர் #பல்லவர் #மாமல்லபுரம் #TNPSCHistory #TamilHistory #TNPSCBites"""
TAGSTN2 = ["TNPSC", "தமிழ்நாட்டு வரலாறு", "களப்பிரர்", "பல்லவர்", "மகேந்திரவர்மன்", "நரசிம்மவர்மன்", "மாமல்லபுரம்", "இருண்ட காலம்",
           "Kalabhras", "Pallavas", "Mamallapuram", "Tamil Nadu history", "TNPSC history", "Tamil history story", "TNPSC Group 4", "TNPSC Bites"]
TITLETN3 = "ராஜராஜ சோழன் எப்படி அரசனானான்? பிற்காலச் சோழர் | தமிழ்நாட்டு வரலாறு பகுதி 3 | TNPSC"
DESCTN3 = """தமிழ்நாட்டு வரலாறு, பகுதி 3: பிற்காலச் சோழர்கள். 1,000 ஆண்டுகளுக்கு முன், கிரேன் இல்லாத காலத்தில் 216 அடி உயரக் கோபுரம் எப்படி எழுந்தது? காவிரிக் கரையில் ஒரு சின்ன அரசாக எழுந்த சோழர், இராஜராஜன் காலத்தில் எப்படிப் பேரரசானார்கள்? சுமார் 5 நிமிடத்தில் முழுக் கதை.

இந்த வீடியோவில்:
• விஜயாலயன், ஆதித்த சோழன் - திருப்புறம்பியம் போர், பல்லவர் முடிவு
• முதலாம் பராந்தகன் - மதுரை கொண்டான், தக்கோலம் போர் 949
• உத்தரமேரூர் கல்வெட்டு - குடவோலை முறைத் தேர்தல்
• ஆதித்த கரிகாலன் மர்மம், செம்பியன் மாதேவி
• இராஜராஜ சோழன் - நில அளவை, காந்தளூர்ச் சாலை, இலங்கை வெற்றி, தேவாரம் மீட்பு
• தஞ்சாவூர் பெரிய கோயில் - 1003 முதல் 1010, யுனெஸ்கோ 1987

TNPSC Group 1, 2, 4 தேர்வுக்கும் பயனுள்ளது. வீடியோவின் இறுதியில் 5 முக்கியத் தேர்வுக் குறிப்புகள் உள்ளன.

முந்தைய பகுதி: களப்பிரர், பல்லவர். அடுத்த பகுதி: இராஜேந்திர சோழன். தவறவிடாமல் இருக்க TNPSC Bites சேனலை SUBSCRIBE செய்யுங்கள், LIKE செய்யுங்கள்.

உங்கள் கருத்து: தஞ்சாவூர் பெரிய கோயிலை நேரில் பார்த்திருக்கிறீர்களா? கீழே கமெண்டில் சொல்லுங்கள்!

குறிப்பு: இந்த வீடியோவில் உள்ள படங்களும் குரலும் AI மூலம் உருவாக்கப்பட்டவை. சில தகவல்கள் (80 டன் கல், சாரப்பள்ளம், தேவாரம் மீட்புக் கதை) மரபுச் செய்திகள். தேர்வுக்குப் படிக்கும்போது உங்கள் பாடநூலுடன் ஒப்பிட்டுப் பார்க்கவும்.

#TNPSC #தமிழ்நாட்டுவரலாறு #சோழர் #இராஜராஜசோழன் #தஞ்சைபெரியகோயில் #TNPSCHistory #TNPSCBites"""
TAGSTN3 = ["TNPSC", "தமிழ்நாட்டு வரலாறு", "சோழர்", "இராஜராஜ சோழன்", "தஞ்சை பெரிய கோயில்", "குடவோலை", "பொன்னியின் செல்வன்", "Cholas", "Rajaraja Chola", "Brihadisvara temple", "Tamil Nadu history", "TNPSC history", "Tamil history story", "TNPSC Group 4", "TNPSC Bites"]
TITLETN4 = "கங்கையையும் கடலையும் வென்ற மன்னன்! இராஜேந்திர சோழன் | தமிழ்நாட்டு வரலாறு பகுதி 4 | TNPSC"
DESCTN4 = """தமிழ்நாட்டு வரலாறு, பகுதி 4: இராஜேந்திர சோழன். தோற்ற அரசர்களின் தலையில் கங்கை நீர்க் குடங்களை சுமக்க வைத்த படை, கடல் கடந்து கடாரத்தை வென்ற கடற்படை. சுமார் 5 நிமிடத்தில் முழுக் கதை.

இந்த வீடியோவில்:
• இலங்கை முழுவதும் வெற்றி, ஐந்தாம் மகிந்தன் சிறை
• கங்கைப் படையெடுப்பு (சுமார் 1021): கலிங்கம், வங்காளம், மகிபாலன்
• கங்கைகொண்ட சோழபுரம், சோழ கங்கம் ஏரி, கங்கைகொண்ட சோழீஸ்வரம் (யுனெஸ்கோ 2004)
• கடாரப் படையெடுப்பு (சுமார் 1025): ஸ்ரீவிஜயம், 14 இடங்கள்
• சீனாவுக்குச் சோழர் தூதுக்குழு (1015)

TNPSC Group 1, 2, 4 தேர்வுக்கும் பயனுள்ளது. வீடியோவின் இறுதியில் 5 முக்கியத் தேர்வுக் குறிப்புகள் உள்ளன.

முந்தைய பகுதி: பிற்காலச் சோழர்கள். அடுத்த பகுதி: பாண்டியர், நாயக்கர், மராட்டியர். தவறவிடாமல் இருக்க TNPSC Bites சேனலை SUBSCRIBE செய்யுங்கள், LIKE செய்யுங்கள்.

உங்கள் கருத்து: இராஜேந்திரனின் எந்த வெற்றி உங்களை மிகவும் வியக்க வைத்தது? கீழே கமெண்டில் சொல்லுங்கள்!

குறிப்பு: இந்த வீடியோவில் உள்ள படங்களும் குரலும் AI மூலம் உருவாக்கப்பட்டவை. சில தகவல்கள் (கங்கை நீர்க் குடங்கள், சோழ கங்கம் ஏரி, ஸ்ரீவிஜயத் தடை) கல்வெட்டு மற்றும் மரபுச் செய்திகள். தேர்வுக்குப் படிக்கும்போது உங்கள் பாடநூலுடன் ஒப்பிட்டுப் பார்க்கவும்.

#TNPSC #தமிழ்நாட்டுவரலாறு #இராஜேந்திரசோழன் #கங்கைகொண்டசோழபுரம் #கடாரம்கொண்டான் #TNPSCHistory #TNPSCBites"""
TAGSTN4 = ["TNPSC", "தமிழ்நாட்டு வரலாறு", "இராஜேந்திர சோழன்", "கங்கை கொண்ட சோழன்", "கடாரம் கொண்டான்", "கங்கைகொண்ட சோழபுரம்", "சோழர்", "Rajendra Chola", "Gangaikonda Cholapuram", "Chola navy", "Tamil Nadu history", "TNPSC history", "Tamil history story", "TNPSC Group 4", "TNPSC Bites"]
TITLE, DESC, TAGS = {"tn4": (TITLETN4, DESCTN4, TAGSTN4), "tn3": (TITLETN3, DESCTN3, TAGSTN3), "tn2": (TITLETN2, DESCTN2, TAGSTN2), "tn1": (TITLETN1, DESCTN1, TAGSTN1), "delhi1": (TITLE1, DESC1, TAGS1), "delhi3": (TITLE3, DESC3, TAGS3),
                     "delhi4": (TITLE4, DESC4, TAGS4)}.get(NAME, (TITLE2, DESC2, TAGS2))

if os.environ.get("UPLOAD") == "1":
    vid = P.upload(VIDEO, TITLE, DESC, TAGS, thumb=thumb)
    (OUT / "uploaded.txt").write_text(f"https://youtube.com/watch?v={vid}")
    if vid:
        P.add_to_playlists(vid, [PLAYLIST])
        upload_shorts(vid)
    P.log(f"DONE https://youtube.com/watch?v={vid}")
else:
    P.log("preview only: nothing uploaded (UPLOAD is not 1)")
