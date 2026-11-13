"""Makes the thumbnail for a finished story video and (UPLOAD=1) uploads the video to YouTube with title, description,
tags and the thumbnail. The video comes from the story's side branch (story-out for delhi1, story-<name> for the others). Privacy follows the YT_PRIVACY setting like the Shorts."""
import base64, os, subprocess, sys
from pathlib import Path

sys.path.insert(0, ".")
import pipeline as P

NAME = os.environ.get("NAME") or "delhi1"
PLAYLIST = "TNPSC வரலாறு கதைகள் | Long Videos"   # every Long story video goes into this one playlist (made when missing)
if os.environ.get("PLAYLIST_ONLY_ID"):   # a video that is already on YouTube: only put it into the playlist, nothing else
    P.add_to_playlists(os.environ["PLAYLIST_ONLY_ID"].strip(), [PLAYLIST])
    sys.exit(0)
OUT = Path("out/story"); OUT.mkdir(parents=True, exist_ok=True)
VIDEO = OUT / f"{NAME}.mp4"
BRANCH = "story-out" if NAME == "delhi1" else f"story-{NAME}"
subprocess.run(["git", "fetch", "-q", "origin", BRANCH], check=True)
VIDEO.write_bytes(subprocess.run(["git", "show", f"FETCH_HEAD:{NAME}.mp4"], check=True, capture_output=True).stdout)


def pic(n):   # picture n from the story-out branch (whole square one if it exists, else the first cropped one)
    for folder in ("sq", "old", "img"):
        r = subprocess.run(["git", "show", f"FETCH_HEAD:{folder}/{n:02d}.jpg"], capture_output=True)
        if r.returncode == 0 and len(r.stdout) > 5000:
            return "data:image/jpeg;base64," + base64.b64encode(r.stdout).decode()
    raise SystemExit(f"picture {n} not found")


if NAME == "delhi1":
    LEFT, RIGHT, BIG, SUB = pic(3), pic(17), "அடிமை ➜ அரசன்!", "டெல்லி சுல்தானியம் | பகுதி 1"
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
TITLE, DESC, TAGS = (TITLE1, DESC1, TAGS1) if NAME == "delhi1" else (TITLE2, DESC2, TAGS2)

if os.environ.get("UPLOAD") == "1":
    vid = P.upload(VIDEO, TITLE, DESC, TAGS, thumb=thumb)
    (OUT / "uploaded.txt").write_text(f"https://youtube.com/watch?v={vid}")
    if vid:
        P.add_to_playlists(vid, [PLAYLIST])
    P.log(f"DONE https://youtube.com/watch?v={vid}")
else:
    P.log("preview only: nothing uploaded (UPLOAD is not 1)")
