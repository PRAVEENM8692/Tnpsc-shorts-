"""One-off test: can the free image service (Pollinations) draw the comic style of the long-video sample?
Saves a few 16:9 pictures into out/image-test/ for a person to look at. Uploads nothing."""
import pathlib, sys, time, urllib.parse
import requests

STYLE = (". Indian comic book illustration, bold clean black ink outlines, flat bright colours with soft cel shading, "
         "warm cheerful palette, richly detailed background, friendly expressive faces, wide 16:9 composition, "
         "no text, no letters, no watermark")
SCENES = {
    "sultanate_qutb": "Delhi in the year 1200, Sultan Qutb-ud-din Aibak in royal robes and turban on a decorated horse, "
                      "pointing at the Qutb Minar being built by workers on scaffolding, soldiers with flags, sunny sky",
    "sultanate_court": "Royal court of the Delhi Sultanate, Sultan Iltutmish seated on a throne under arches, nobles and scholars "
                       "standing on both sides, silver coins on a tray in front, lamps and carpets",
    "chola_temple": "Chola king Rajaraja Chola in silk dhoti and gold ornaments standing before the great Thanjavur temple tower, "
                    "sculptors carving stone, an elephant, coconut trees, bright morning light",
}
out = pathlib.Path("out/image-test"); out.mkdir(parents=True, exist_ok=True)
ok = 0
for name, prompt in SCENES.items():
    for attempt in range(4):
        url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt + STYLE)
               + f"?width=1280&height=720&nologo=true&seed={41 + attempt}")
        try:
            r = requests.get(url, timeout=180)
            if r.ok and r.headers.get("content-type", "").startswith("image") and len(r.content) > 10_000:
                (out / f"{name}.jpg").write_bytes(r.content); ok += 1
                print(f"saved {name} ({len(r.content)//1024} KB, try {attempt + 1})"); break
            print(f"{name}: try {attempt + 1} -> HTTP {r.status_code}")
        except requests.RequestException as e:
            print(f"{name}: try {attempt + 1} -> {e!r}"[:200])
        time.sleep(15)
print(f"done: {ok}/{len(SCENES)} pictures")
sys.exit(0 if ok else 1)
