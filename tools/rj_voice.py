"""RJ-style voice polish (free, ffmpeg only) - makes the narration sound like a radio jockey's studio voice.

Chain, in order (what an RJ studio does):
  1. highpass 75 Hz      - cut rumble / low hum
  2. (optional) denoise  - only for recorded mic voice (TTS voice is already clean)
  3. bass boost ~110 Hz  - warmth / 'weight' in the voice
  4. mud cut ~350 Hz     - removes the boxy, 'inside a box' sound
  5. presence ~4 kHz     - clear, forward words
  6. air ~10 kHz         - sparkle / brightness (treble boost)
  7. de-esser            - softens sharp 'ss' sounds after the treble boost
  8. compressor          - soft and loud words sit at the same level (the main RJ 'secret')
  9. loudness normalise  - same loudness every video, limiter stops clipping

Use:
  python tools/rj_voice.py in.mp3 out.wav [--preset male|female|shorts] [--denoise]
  from tools.rj_voice import polish ; polish("voice.mp3", "voice_rj.wav", preset="male")

Also: duck_mix_filter() builds an ffmpeg filter that lowers the BGM automatically while the voice speaks (radio 'ducking').
"""
import argparse
import subprocess
from pathlib import Path

PRESETS = {
    # deep male narration (Gemini Charon): more warmth, a little less low-mid
    "male":   dict(hp=75, bass=3.5, bass_f=110, mud=-3.0, pres=2.5, air=2.0, ess=0.35, lufs=-16),
    # female voice (Kore etc.): less bass, a touch more air
    "female": dict(hp=95, bass=1.5, bass_f=180, mud=-2.0, pres=2.0, air=2.5, ess=0.45, lufs=-16),
    # Shorts on phone speakers: punchier and a bit louder
    "shorts": dict(hp=90, bass=2.0, bass_f=130, mud=-3.0, pres=3.5, air=2.0, ess=0.4, lufs=-14),
}


def chain(preset="male", denoise=False):
    """The ffmpeg -af filter string (loudness step included)."""
    p = PRESETS[preset]
    f = [f"highpass=f={p['hp']}:poles=2"]
    if denoise:
        f.append("afftdn=nf=-28:tn=1")
    f += [
        f"bass=g={p['bass']}:f={p['bass_f']}:w=0.7",
        f"equalizer=f=350:t=q:w=1.2:g={p['mud']}",
        f"equalizer=f=4000:t=q:w=1.0:g={p['pres']}",
        f"treble=g={p['air']}:f=10000:w=0.6",
        f"deesser=i={p['ess']}:m=0.5:f=0.5",
        "acompressor=threshold=-21dB:ratio=3.5:attack=6:release=120:knee=4:makeup=3dB",
        f"loudnorm=I={p['lufs']}:TP=-1.5:LRA=7",
        "alimiter=limit=-1dB:level=false",
        "aresample=44100",
    ]
    return ",".join(f)


def polish(src, dst, preset="male", denoise=False):
    """Write an RJ-polished copy of src to dst. Returns dst (or src unchanged if ffmpeg fails, so a video never breaks)."""
    dst = Path(dst)
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", chain(preset, denoise),
                        "-ac", "1", str(dst)], capture_output=True, text=True)
    if r.returncode != 0 or not dst.exists() or dst.stat().st_size < 1000:
        print("rj_voice: polish failed, using the original voice:", r.stderr[-400:])
        return Path(src)
    return dst


def duck_mix_filter(voice_in="1:a", music_in="2:a", music_vol=0.22, total=None, out="a"):
    """filter_complex text: BGM dips under the voice and comes back up in pauses (radio ducking)."""
    fade = f",afade=t=out:st={max(total - 3, 0):.2f}:d=3" if total else ""
    return (f"[{voice_in}]asplit=2[v][sc];"
            f"[{music_in}]volume={music_vol}{fade}[m];"
            f"[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[md];"
            f"[v][md]amix=inputs=2:duration=first:normalize=0[{out}]")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--preset", default="male", choices=PRESETS)
    ap.add_argument("--denoise", action="store_true")
    a = ap.parse_args()
    print(polish(a.src, a.dst, a.preset, a.denoise))
