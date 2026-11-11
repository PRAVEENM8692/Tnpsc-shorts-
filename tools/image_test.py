"""Hand-run test for the long story video: draws the storyboard of the first 30 seconds (9 pictures, 16:9)
with a free Hugging Face Space (FLUX.1 schnell) into out/image-test/. Uploads nothing to YouTube.
HF_TOKEN is optional: without it the Space is called anonymously (smaller free quota)."""
import os, pathlib, shutil, sys, time

from gradio_client import Client

STYLE = ("Indian comic book illustration, bold clean black ink outlines, flat bright colours with soft cel shading, "
         "warm palette, richly detailed background, expressive faces, cinematic wide 16:9 frame. ")
END = " No text, no letters, no watermark."
BOY = "a thin 10-year-old Turkic boy with short black hair, sharp eyes, plain brown tunic"
AIBAK = "Qutb-ud-din Aibak, a strong man with a short black beard, sharp eyes, red-and-gold turban"
SHOTS = [
    ("01_bazaar", "A crowded 12th-century Central Asian bazaar seen from above, cloth stalls, camels, merchants and buyers, dusty golden sunlight."),
    ("02_slave_market", "A slave market in that bazaar: a wooden platform with a row of sad people standing, a rich merchant in a big turban pointing at them, buyers watching."),
    ("03_boy_closeup", f"Close-up of {BOY} standing alone on the wooden platform of a slave market, determined face, the crowd behind him looking away."),
    ("04_boy_to_king", f"The same person grown up: {AIBAK} in royal robes sitting on a golden throne in a grand Delhi court, courtiers bowing."),
    ("05_qutb_minar_today", "The Qutb Minar tower in Delhi today, tall red sandstone tower against a bright blue sky, small tourists at its base, green lawns."),
    ("06_three_rulers", "Three thrones in a row in a medieval Indian court: a bearded sultan on the left, a brave young queen in royal armour and crown in the centre, a stern older sultan on the right."),
    ("07_delhi_sunrise", "Medieval Delhi at sunrise seen from a hill: fort walls, domes, a half-built tall tower with scaffolding, birds in an orange sky."),
    ("08_stable", f"A royal stable in Ghazni: young {AIBAK.replace('red-and-gold turban', 'simple cloth cap')} as a servant brushing a fine horse, a king in rich robes watching him with approval from the doorway."),
    ("09_general", f"{AIBAK} in steel armour riding at the head of a cavalry army with green banners across a dusty plain, sword raised."),
]
out = pathlib.Path("out/image-test"); out.mkdir(parents=True, exist_ok=True)
token = os.environ.get("HF_TOKEN") or None
print("HF token:", "set" if token else "not set (anonymous call)")
client, ok = None, 0
for name, scene in SHOTS:
    for attempt in range(3):
        try:
            if client is None:
                client = Client("black-forest-labs/FLUX.1-schnell", hf_token=token) if token else Client("black-forest-labs/FLUX.1-schnell")
            res = client.predict(prompt=STYLE + scene + END, seed=41, randomize_seed=False, width=1280, height=720,
                                 num_inference_steps=4, api_name="/infer")
            img = res[0] if isinstance(res, (list, tuple)) else res
            if isinstance(img, dict):
                img = img.get("path") or img.get("url")
            dst = out / (name + (pathlib.Path(str(img)).suffix or ".webp"))
            shutil.copy(img, dst); ok += 1
            print(f"saved {dst.name} ({dst.stat().st_size // 1024} KB, try {attempt + 1})")
            break
        except Exception as e:
            print(f"{name}: try {attempt + 1} failed -> {str(e)[:300]}")
            client = None
            time.sleep(30 * (attempt + 1))
    time.sleep(5)
print(f"done: {ok}/{len(SHOTS)} pictures")
sys.exit(0 if ok else 1)
