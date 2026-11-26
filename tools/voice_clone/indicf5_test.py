"""Owner's own voice as an AI voice (free): AI4Bharat IndicF5 zero-shot voice cloning, Tamil.

Makes out/*.mp3: each test line in the owner's cloned voice (raw + RJ-polished) and, for comparison, Gemini Charon.
Engine (MYVOICE_ENGINE): auto = free Hugging Face GPU Space first, then the slow CPU model; or space / cpu.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, ".")
from tools.voice_clone import myvoice_tts as V  # noqa: E402
from tools.rj_voice import polish  # noqa: E402

OUT = Path("out")
OUT.mkdir(exist_ok=True)

SHORT = ("ஒரு ராத்திரி, சென்னைக்குப் போற ஒரு சாதாரண ரயில்ல, கோடிக்கணக்கான பணம் இருந்துச்சு. யாருக்கும் தெரியாம, "
         "அந்த ரயிலோட கூரையைத் துளைச்சு, அந்தப் பணத்தை ஒரு கும்பல் அள்ளிட்டுப் போச்சு. ரயில் நிக்கவே இல்ல. "
         "யாரும் எதையும் பார்க்கல. ஆனா ரெண்டு வருஷம் கழிச்சு, ஒரே ஒரு செல்போன் சிக்னல், அவங்க எல்லாரையும் காட்டிக் கொடுத்துச்சு. "
         "அது எப்படி நடந்துச்சு? முழுக் கதையையும் பார்க்கலாம்.")
LINES = {
    "story": os.environ.get("TEXT_1") or (
        "ஒரு காலத்துல தமிழ்நாட்டை ஆண்ட ஒரு பெரிய வம்சம், திடீர்னு வரலாற்றுல இருந்தே காணாமப் போச்சு. "
        "அவங்க யாரு? என்ன நடந்துச்சு? இன்னைக்கு அந்தக் கதையைத்தான் பார்க்கப் போறோம்."),
    "crime_short": os.environ.get("TEXT_2") or SHORT,
}


def to_mp3(wav, mp3):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "160k", str(mp3)], check=True)


print("reference text length:", len(V.ref_text()), "characters", flush=True)   # the words are not printed (public logs)
for name, text in LINES.items():
    t0 = time.time()
    raw = V.speak(text, OUT / f"{name}_raw.wav")
    to_mp3(raw, OUT / f"{name}_1_my_ai_voice.mp3")
    to_mp3(polish(raw, OUT / f"{name}_rj.wav", preset="male"), OUT / f"{name}_2_my_ai_voice_RJ.mp3")
    secs = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(raw)],
                                capture_output=True, text=True).stdout)
    print(f"{name}: {secs:.1f} s of audio in {time.time() - t0:.0f} s", flush=True)
print("engine use:", V.STATS, flush=True)

try:   # same lines in Gemini Charon, to compare side by side
    import pipeline as P
    os.environ["GEMINI_VOICE"] = "Charon"
    for name, text in LINES.items():
        P.make_voice_gemini(text, str(OUT / f"{name}_3_gemini_charon.mp3"))
except Exception as e:  # noqa: BLE001
    print("Charon comparison skipped:", e)

for f in OUT.glob("*.wav"):
    f.unlink()
print("done:", sorted(p.name for p in OUT.iterdir()))
