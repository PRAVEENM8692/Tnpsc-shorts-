"""Owner's AI voice, one new line per mood, each spoken with that mood's own reference clip (+ RJ polish), and the same
lines in Gemini Charon to compare. Output: out/<NN>_<mood>_1_my_voice_RJ.mp3, out/<NN>_<mood>_2_charon.mp3"""
import os
import sys
from pathlib import Path

sys.path.insert(0, ".")
from tools.voice_clone import myvoice_tts as V  # noqa: E402
from tools.rj_voice import polish  # noqa: E402

LINES = {
    "hook": "அன்னைக்கு ராத்திரி, அந்த ஊர்ல யாருமே தூங்கல. ஏன்னா, அந்தக் காட்டுக்குள்ள இருந்து ஒரு சத்தம் கேட்டுக்கிட்டே இருந்துச்சு.",
    "calm": "அவர் ஒரு சாதாரண பள்ளிக்கூட வாத்தியார். காலையில ஸ்கூல், சாயங்காலம் வீடு. இதுதான் அவரோட தினசரி வாழ்க்கை.",
    "suspense": "அவன் போன் ஆன் ஆனது வெறும் முப்பது வினாடி தான். அதுக்குள்ள, சைபர் டீம் அவன் இருக்கற டவரைக் கண்டுபிடிக்கணும்.",
    "twist": "எல்லாரும் சந்தேகப்பட்டது அந்த டிரைவரை. ஆனா உண்மையான குற்றவாளி, முதல்ல போலீஸுக்கு போன் பண்ணவர் தான்!",
    "question": "ஒரு கொலைகாரன், ஏன் தானே போலீஸ் ஸ்டேஷனுக்கு வந்து புகார் கொடுக்கணும்? அதுக்குப் பின்னாடி என்ன திட்டம் இருந்திருக்கும்?",
    "sad": "அந்தக் குழந்தையோட ஸ்கூல் பை இன்னும் அந்த வீட்டு மூலையில தான் இருக்கு. அதைத் தொட யாருக்கும் மனசு வரல.",
    "success": "மூணு மாநிலம், நூறு சிசிடிவி கேமரா, ஒரு டீ கடை பில். இதை வச்சு தான், போலீஸ் அவனைச் சுத்தி வளைச்சாங்க.",
    "end": "இந்த கேஸ் பத்தி உங்க கருத்தை கமெண்ட்ல சொல்லுங்க. இன்னும் இது மாதிரி கேஸ்களுக்கு, சேனலை சப்ஸ்கிரைப் பண்ணுங்க.",
}
OUT = Path("out")
OUT.mkdir(exist_ok=True)
for i, (mood, text) in enumerate(LINES.items(), 1):
    raw = V.speak(text, OUT / f"{mood}_raw.wav", mood=mood)
    rj = polish(raw, OUT / f"{mood}_rj.wav", preset="male")
    os.system(f'ffmpeg -y -loglevel error -i "{rj}" -b:a 160k "{OUT}/{i:02d}_{mood}_1_my_voice_RJ.mp3"')
    print("made", mood, flush=True)
print("engine use:", V.STATS, flush=True)
try:
    import pipeline as P
    os.environ["GEMINI_VOICE"] = "Charon"
    for i, (mood, text) in enumerate(LINES.items(), 1):
        P.make_voice_gemini(text, str(OUT / f"{i:02d}_{mood}_2_charon.mp3"))
except Exception as e:  # noqa: BLE001
    print("Charon comparison skipped:", e)
for f in OUT.glob("*.wav"):
    f.unlink()
print("done:", sorted(p.name for p in OUT.iterdir()))
