"""One-off test: can a free Hugging Face Space (FLUX.1 schnell) draw the comic style of the long-video sample?
Saves ONE 16:9 picture into out/image-test/ for a person to look at. Uploads nothing to YouTube.
HF_TOKEN is optional: without it the Space is called anonymously (smaller free quota)."""
import os, pathlib, shutil, sys, time

from gradio_client import Client

PROMPT = ("Indian comic book illustration, bold clean black ink outlines, flat bright colours with soft cel shading, "
          "warm cheerful palette, richly detailed background, friendly expressive faces. "
          "Delhi in the year 1200: Sultan Qutb-ud-din Aibak in royal robes and turban riding a decorated horse in the foreground, "
          "pointing at the tall Qutb Minar tower being built by workers on wooden scaffolding, soldiers holding flags, sunny blue sky. "
          "No text, no letters, no watermark.")
SPACES = ["black-forest-labs/FLUX.1-schnell", "evalstate/flux1_schnell"]
out = pathlib.Path("out/image-test"); out.mkdir(parents=True, exist_ok=True)
token = os.environ.get("HF_TOKEN") or None
print("HF token:", "set" if token else "not set (anonymous call)")
for space in SPACES:
    for attempt in range(2):
        try:
            c = Client(space, hf_token=token) if token else Client(space)
            res = c.predict(prompt=PROMPT, seed=41, randomize_seed=False, width=1280, height=720,
                            num_inference_steps=4, api_name="/infer")
            img = res[0] if isinstance(res, (list, tuple)) else res
            if isinstance(img, dict):
                img = img.get("path") or img.get("url")
            dst = out / ("sultanate_qutb_flux" + (pathlib.Path(str(img)).suffix or ".webp"))
            shutil.copy(img, dst)
            print(f"saved {dst.name} from {space} ({dst.stat().st_size // 1024} KB)")
            sys.exit(0)
        except Exception as e:
            print(f"{space}: try {attempt + 1} failed -> {str(e)[:300]}")
            time.sleep(20)
print("no picture could be made")
sys.exit(1)
