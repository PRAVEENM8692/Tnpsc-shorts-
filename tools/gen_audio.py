"""Makes the original background music and sound effects in assets/ with plain code (numpy + ffmpeg), so there is
no copyright problem. Run once:  python3 tools/gen_audio.py   (the generated files are committed; pipeline.py
picks one bgm*.mp3 at random for every video and mixes the sfx_*.wav effects at the card / step changes)."""
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "assets"
rng = np.random.default_rng(7)


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.15):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    env = np.ones(n) * s
    env[:a] = np.linspace(0, 1, a, endpoint=False) if a else env[:a]
    if d:
        env[a:a + d] = np.linspace(1, s, min(d, max(n - a, 0)), endpoint=False)[:max(n - a, 0)][:len(env[a:a + d])]
    if r and n > r:
        env[-r:] *= np.linspace(1, 0, r)
    return env


def tone(freq, dur, harm=(1.0, 0.3, 0.1), a=0.01, d=0.1, s=0.7, r=0.15, detune=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = sum(w * np.sin(2 * np.pi * freq * (k + 1) * t * (1 + detune)) for k, w in enumerate(harm))
    return y * adsr(n, a, d, s, r)


def pluck(freq, dur=0.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-6 * t)
         + 0.15 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-9 * t))
    return y * np.exp(-4.5 * t) * np.minimum(t * 400, 1)


def kick(dur=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def hat(dur=0.05, vol=1.0):
    n = int(dur * SR)
    x = np.diff(rng.standard_normal(n + 1))   # crude high-pass
    return x * np.exp(-np.arange(n) / SR * 70) * vol


def soft_snare(dur=0.18):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (rng.standard_normal(n) * 0.5 + np.sin(2 * np.pi * 190 * t) * 0.5) * np.exp(-t * 22)


def put(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= buf.shape[1]:
        return
    sig = sig[:buf.shape[1] - i] * gain
    buf[0, i:i + len(sig)] += sig * (1 - max(pan, 0))
    buf[1, i:i + len(sig)] += sig * (1 + min(pan, 0))


def reverb(buf, seconds=1.4, wet=0.22):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 3.2)
    ir[0] = 0
    out = np.empty_like(buf)
    L = buf.shape[1] + n
    for c in range(2):
        f = np.fft.rfft(buf[c], L) * np.fft.rfft(ir if c == 0 else ir[::-1], L)
        out[c] = buf[c] + wet * np.fft.irfft(f, L)[:buf.shape[1]] / (np.abs(ir).sum() ** 0.5)
    return out


def to_mp3(buf, path, target_db):
    """Scale so the average loudness matches target_db, fade the ends, save as mp3."""
    peak = np.abs(buf).max()
    buf = buf / (peak or 1) * 0.9
    f = int(0.6 * SR)
    buf[:, :f] *= np.linspace(0, 1, f)
    buf[:, -f:] *= np.linspace(1, 0, f)
    wav = path.with_suffix(".tmp.wav")
    pcm = (np.clip(buf.T, -1, 1) * 32767).astype("<i2")
    import wave
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    # measure the mean volume, then apply the gain that reaches target_db
    p = subprocess.run(["ffmpeg", "-i", str(wav), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    mean = float([l for l in p.stderr.splitlines() if "mean_volume" in l][0].split(":")[1].split("dB")[0])
    gain = target_db - mean
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", f"volume={gain}dB,alimiter=limit=0.95",
                    "-c:a", "libmp3lame", "-b:a", "96k", str(path)], check=True)
    wav.unlink()
    print(path.name, f"{gain:+.1f} dB", f"{path.stat().st_size // 1024} KB")


def song(bpm, bars, chords, style):
    beat = 60.0 / bpm
    total = bars * 4 * beat
    buf = np.zeros((2, int((total + 2.5) * SR)))
    for bar in range(bars):
        root, quality = chords[bar % len(chords)]
        notes = [root + i for i in quality]
        t0 = bar * 4 * beat
        # pad
        for k, m in enumerate(notes):
            put(buf, tone(hz(m), 4 * beat + 0.3, (1, .25, .08), a=.35, d=.3, s=.6, r=.6, detune=.002 * (k - 1)),
                t0, .16 if style != "focus" else .10, pan=(k - 1) * .35)
        # bass
        if style in ("lofi", "bright", "focus"):
            for b in range(4):
                if style == "lofi" and b in (1, 3):
                    continue
                put(buf, tone(hz(root - 24), beat * .9, (1, .2), a=.01, d=.1, s=.6, r=.1), t0 + b * beat, .32)
        # melody / arpeggio
        if style == "calm":
            for i in range(8):
                m = notes[(i * 2) % len(notes)] + (12 if i % 3 else 24)
                put(buf, pluck(hz(m), 1.2), t0 + i * beat * .5, .14, pan=(-.4 if i % 2 else .4))
        elif style == "lofi":
            for i, off in enumerate((0, 1.5, 2, 3.5)):
                m = notes[(i + bar) % len(notes)] + 12
                put(buf, pluck(hz(m), .9), t0 + off * beat + (0.03 if i % 2 else 0), .17, pan=.2)
        elif style == "bright":
            for i in range(8):
                m = notes[[0, 2, 1, 2, 3 if len(notes) > 3 else 0, 2, 1, 2][i]] + 12
                put(buf, pluck(hz(m), .5), t0 + i * beat * .5, .16, pan=(-.3 if i % 2 else .3))
        elif style == "focus":
            for i in range(8):
                m = notes[[0, 1, 2, 1][i % 4]] + 12
                put(buf, tone(hz(m), beat * .4, (1, 0, .33, 0, .2), a=.005, d=.08, s=.3, r=.1), t0 + i * beat * .5, .12, pan=(.4 if i % 2 else -.4))
        # drums
        for b in range(4):
            tb = t0 + b * beat
            if style == "lofi":
                if b in (0, 2):
                    put(buf, kick(), tb + (0.0 if b == 0 else 0.06), .5)
                if b in (1, 3):
                    put(buf, soft_snare(), tb, .22)
                for h in (0, .5):
                    put(buf, hat(vol=.8), tb + h * beat + (.04 if h else 0), .10)
            elif style == "bright":
                if b in (0, 2):
                    put(buf, kick(), tb, .38)
                put(buf, hat(vol=.8), tb + .5 * beat, .09)
                if b in (1, 3):
                    put(buf, soft_snare(), tb, .13)
            elif style == "focus":
                put(buf, kick(.25), tb, .30) if b % 2 == 0 else None
                put(buf, hat(.03, .8), tb, .07)
                put(buf, hat(.03, .8), tb + .5 * beat, .05)
    return reverb(buf[:, :int((total + 2.0) * SR)])


# chord = (root midi, intervals)
MAJ, MIN, MAJ7, MIN7, DOM7 = (0, 4, 7), (0, 3, 7), (0, 4, 7, 11), (0, 3, 7, 10), (0, 4, 7, 10)
TRACKS = {
    "bgm_calm": (76, 32, [(48, MAJ), (45, MIN), (53, MAJ), (43, MAJ)], "calm"),
    "bgm_lofi": (84, 36, [(50, MIN7), (43, DOM7), (48, MAJ7), (45, MIN7)], "lofi"),
    "bgm_bright": (104, 40, [(43, MAJ), (50, MAJ), (52, MIN), (48, MAJ)], "bright"),
    "bgm_focus": (92, 36, [(45, MIN), (53, MAJ), (48, MAJ), (43, MAJ)], "focus"),
}


def sfx():
    import wave

    def save(name, y, gain=0.8):
        y = y / (np.abs(y).max() or 1) * gain
        with wave.open(str(OUT / f"sfx_{name}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
        print("sfx", name)
    # whoosh: filtered noise sweeping up then down
    n = int(.55 * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    k = np.exp(-((t - .22) / .14) ** 2)
    y = np.convolve(noise, np.ones(18) / 18, mode="same") * k
    y += np.convolve(noise, np.ones(60) / 60, mode="same") * k * 1.5
    save("whoosh", y, .55)
    # pop: short soft blip
    n = int(.18 * SR); t = np.arange(n) / SR
    save("pop", np.sin(2 * np.pi * (520 + 380 * np.exp(-t * 30)) * t) * np.exp(-t * 22), .6)
    # ding: two bell partials
    n = int(1.2 * SR); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * 988 * t) + .5 * np.sin(2 * np.pi * 1976 * t) * np.exp(-t * 3) + .3 * np.sin(2 * np.pi * 1480 * t)) * np.exp(-t * 3.2)
    save("ding", y * np.minimum(t * 800, 1), .7)
    # tick: tiny click
    n = int(.06 * SR); t = np.arange(n) / SR
    save("tick", np.sin(2 * np.pi * 1700 * t) * np.exp(-t * 90), .55)
    # confetti-like sparkle for the answer
    n = int(.9 * SR); t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * t) * np.exp(-(t - s) ** 2 * 0 - np.maximum(t - s, 0) * 9) * (t >= s)
            for f, s in ((1318, 0.0), (1568, .07), (2093, .14), (2637, .21)))
    save("sparkle", y, .6)


if __name__ == "__main__":
    p = subprocess.run(["ffmpeg", "-i", str(OUT / "bgm.mp3"), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    ref = float([l for l in p.stderr.splitlines() if "mean_volume" in l][0].split(":")[1].split("dB")[0])
    print("reference loudness of bgm.mp3:", ref)
    which = sys.argv[1:] or list(TRACKS)
    for name in which:
        if name == "sfx":
            continue
        bpm, bars, chords, style = TRACKS[name]
        to_mp3(song(bpm, bars, chords, style), OUT / f"{name}.mp3", ref)
    if not sys.argv[1:] or "sfx" in which:
        sfx()
