"""Owner's own voice as an AI voice (free): AI4Bharat IndicF5 zero-shot voice cloning, Tamil.

Input : myvoice/ref.wav (decrypted in the workflow from assets/myvoice/ref.enc) + REF_TEXT (exact words spoken in it)
Output: out/*.mp3 - the same Tamil lines in the owner's cloned voice (raw + RJ-polished) and, for comparison, Gemini Charon.
CPU only (GitHub Actions), so it is slow but free. The model is gated on Hugging Face: the HF_TOKEN account must have
pressed 'Agree' on https://hf.co/ai4bharat/IndicF5 once.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, ".")
OUT = Path("out")
OUT.mkdir(exist_ok=True)
REF = "myvoice/ref.wav"
REF_TEXT = os.environ["REF_TEXT"].strip()

LINES = {
    "story": os.environ.get("TEXT_1") or (
        "ஒரு காலத்துல தமிழ்நாட்டை ஆண்ட ஒரு பெரிய வம்சம், திடீர்னு வரலாற்றுல இருந்தே காணாமப் போச்சு. "
        "அவங்க யாரு? என்ன நடந்துச்சு? இன்னைக்கு அந்தக் கதையைத்தான் பார்க்கப் போறோம்."),
    "crime": os.environ.get("TEXT_2") or (
        "அந்த ராத்திரி, அந்த வீட்டுக்குள்ள யாருமே போகல, யாருமே வெளியே வரல. ஆனா காலையில கதவைத் திறந்தப்போ, "
        "போலீஸ் பார்த்தது எல்லாரையும் அதிர வைச்சது. ஒரே ஒரு சின்ன தடயம், இந்த முழு கேஸையும் உடைச்சது."),
}


def to_mp3(wav, mp3):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "160k", str(mp3)], check=True)


from transformers import AutoModel  # noqa: E402

t0 = time.time()
model = AutoModel.from_pretrained("ai4bharat/IndicF5", trust_remote_code=True, token=os.environ.get("HF_TOKEN"))
print(f"model loaded in {time.time() - t0:.0f} s", flush=True)

from tools.rj_voice import polish  # noqa: E402

for name, text in LINES.items():
    t0 = time.time()
    audio = model(text, ref_audio_path=REF, ref_text=REF_TEXT)
    audio = np.asarray(audio)
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    raw = OUT / f"{name}_my_voice_raw.wav"
    sf.write(raw, audio, samplerate=24000)
    to_mp3(raw, OUT / f"{name}_1_my_ai_voice.mp3")
    rj = polish(raw, OUT / f"{name}_rj.wav", preset="male")
    to_mp3(rj, OUT / f"{name}_2_my_ai_voice_RJ.mp3")
    print(f"{name}: {len(audio) / 24000:.1f} s of audio in {time.time() - t0:.0f} s", flush=True)

# same lines in Gemini Charon, to compare side by side (skipped quietly if Gemini is not available)
try:
    import pipeline as P
    os.environ["GEMINI_VOICE"] = "Charon"
    for name, text in LINES.items():
        P.make_voice_gemini(text, str(OUT / f"{name}_3_gemini_charon.mp3"))
except Exception as e:  # noqa: BLE001
    print("Charon comparison skipped:", e)

for f in OUT.glob("*.wav"):
    f.unlink()
print("done:", sorted(p.name for p in OUT.iterdir()))
