"""Owner's own AI voice (IndicF5 voice clone) - one function for both channels.

speak(text, out_wav) tries the free Hugging Face GPU first (the official ai4bharat/IndicF5 Space, ZeroGPU, using the
HF_TOKEN account's daily free GPU minutes) and falls back to the slow local CPU model when the Space is busy or the
quota is used up. Long text is cut at sentence ends so each GPU call stays short.

Needs: myvoice/ref.wav (decrypted reference clip) and REF_TEXT (its exact words; if empty, Whisper writes them).
"""
import os
import re
import subprocess
import time
from pathlib import Path

import numpy as np
import soundfile as sf

REF = os.environ.get("MYVOICE_REF", "myvoice/ref.wav")
EMO_DIR = Path(os.environ.get("MYVOICE_EMO", "myvoice/emo"))   # optional: one reference clip per mood + texts.json
MOODS = ("hook", "calm", "suspense", "twist", "question", "sad", "success", "end")
SR = 24000
_ref_text = None
_cpu_model = None
_space = None
STATS = {"space": 0, "cpu": 0, "space_seconds": 0.0, "cpu_seconds": 0.0}


def ref_text():
    global _ref_text
    if _ref_text is None:
        t = (os.environ.get("REF_TEXT") or "").strip()
        if not t:
            from faster_whisper import WhisperModel
            wm = WhisperModel("large-v3", device="cpu", compute_type="int8")
            segs, _ = wm.transcribe(REF, language="ta", beam_size=5, vad_filter=False)
            t = " ".join(s.text.strip() for s in segs).strip()
        _ref_text = t
    return _ref_text


def ref_for(mood=None):
    """(clip, exact words) for a mood; the default storytelling clip when the mood has no clip."""
    if mood and (EMO_DIR / f"{mood}.wav").exists() and (EMO_DIR / "texts.json").exists():
        import json
        return str(EMO_DIR / f"{mood}.wav"), json.loads((EMO_DIR / "texts.json").read_text(encoding="utf-8"))[mood]
    return REF, ref_text()


def chunks(text, limit=220):
    """Cut text at sentence ends (. ? ! ।) into pieces of at most ~limit characters."""
    parts = [p.strip() for p in re.split(r"(?<=[.?!।])\s+", text.strip()) if p.strip()]
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + 1 + len(p) > limit:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur} {p}".strip()
    if cur:
        out.append(cur)
    return out


def _read(path):
    a, sr = sf.read(path, dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1)
    if sr != SR:
        tmp = str(path) + ".24k.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), "-ar", str(SR), "-ac", "1", tmp], check=True)
        a, _ = sf.read(tmp, dtype="float32")
    return a


def _via_space(text, ref=None, rtext=None):
    global _space
    ref, rtext = ref or REF, rtext or ref_text()
    from gradio_client import Client, handle_file
    if _space is None:
        name, tok = os.environ.get("MYVOICE_SPACE", "ai4bharat/IndicF5"), os.environ.get("HF_TOKEN")
        try:
            _space = Client(name, token=tok)          # gradio_client 2.x
        except TypeError:
            _space = Client(name, hf_token=tok)       # gradio_client 1.x
    res = _space.predict(text, handle_file(ref), rtext, api_name="/synthesize_speech")
    path = res if isinstance(res, str) else (res.get("path") if isinstance(res, dict) else res[0])
    return _read(path)


def _via_cpu(text, ref=None, rtext=None):
    global _cpu_model
    ref, rtext = ref or REF, rtext or ref_text()
    if _cpu_model is None:
        from transformers import AutoModel
        _cpu_model = AutoModel.from_pretrained("ai4bharat/IndicF5", trust_remote_code=True, token=os.environ.get("HF_TOKEN"))
    a = np.asarray(_cpu_model(text, ref_audio_path=ref, ref_text=rtext))
    if a.dtype == np.int16:
        a = a.astype(np.float32) / 32768.0
    return a


def speak(text, out_wav, gap=0.25, engine=None, mood=None):
    """Write text in the owner's AI voice to out_wav (24 kHz mono). engine: 'space', 'cpu' or None (= space, then cpu).
    mood: one of MOODS to speak with that mood's reference clip (falls back to the default clip)."""
    ref, rtext = ref_for(mood)
    engine = engine or os.environ.get("MYVOICE_ENGINE", "auto")
    pieces, silence = [], np.zeros(int(SR * gap), dtype=np.float32)
    space_ok = engine in ("auto", "space")
    for part in chunks(text):
        a = None
        if space_ok:
            t0 = time.time()
            try:
                a = _via_space(part, ref, rtext)
                STATS["space"] += 1
                STATS["space_seconds"] += time.time() - t0
            except Exception as e:  # noqa: BLE001  (busy Space / GPU quota used up / network)
                print("GPU Space not usable, switching to CPU:", str(e)[:300], flush=True)
                if engine == "space":
                    raise
                space_ok = False
        if a is None:
            t0 = time.time()
            a = _via_cpu(part, ref, rtext)
            STATS["cpu"] += 1
            STATS["cpu_seconds"] += time.time() - t0
        pieces += [a, silence]
    sf.write(out_wav, np.concatenate(pieces[:-1]) if pieces else silence, SR)
    return Path(out_wav)
