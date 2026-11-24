"""Animated LIKE / SUBSCRIBE buttons (owner's standing rule, 2026-11-23): they pop in one by one (LIKE first, then SUBSCRIBE) in the
middle of the video and go away, and appear together again at the end. Used for the Long videos (1280x720, burnt in at upload time so the
Shorts can still be cut from the clean file) and for the Shorts (1080x1920, buttons at the bottom)."""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pipeline import ass_time, rrect  # noqa: E402


def make_ass(path, w, h, total, y, scale=1.0, mid=None, end=None, tamil=True, lfrac=0.278, sfrac=0.667):
    """mid = (start, seconds) for the one-by-one pop; end = (start, seconds) for the closing pop. y = centre line of the buttons."""
    font = os.environ.get("SUB_FONT") or "Noto Sans Tamil"
    latin = os.environ.get("SUB_LATIN_FONT") or "DejaVu Sans"
    head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nWrapStyle: 0\n\n[V4+ Styles]\n"
            "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,"
            "ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
            f"Style: Btn,{latin},{int(58 * scale)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n"
            f"Style: Ta,{font},{int(46 * scale)},&H0000D7FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,{max(2, int(4 * scale))},1,5,0,0,0,1\n\n"
            "[Events]\nFormat: Layer,Start,End,Style,MarginL,MarginR,MarginV,Effect,Text\n")
    lw, sw, bh, rad = int(330 * scale), int(470 * scale), int(120 * scale), int(28 * scale)
    lx, sx = int(w * lfrac), int(w * sfrac)
    pop = r"\fscx40\fscy40\t(0,350,\fscx108\fscy108)\t(350,500,\fscx100\fscy100)"
    pulse = r"\t(1800,2200,\fscx108\fscy108)\t(2200,2600,\fscx100\fscy100)"
    out = []

    def button(t0, t1, cx, bw, col, label, extra=""):
        fade = r"\fad(150,250)"
        out.append(f"Dialogue: 1,{ass_time(t0)},{ass_time(t1)},Btn,0,0,0,,{{\\an5\\pos({cx},{y})\\bord0\\shad0{col}{fade}{pop}{extra}\\p1}}{rrect(bw, bh, rad)}{{\\p0}}")
        out.append(f"Dialogue: 2,{ass_time(t0)},{ass_time(t1)},Btn,0,0,0,,{{\\an5\\pos({cx},{y}){fade}{pop}{extra}}}{label}")

    blue, red = r"\1c&HE5881E&", r"\1c&H0000FF&"
    if mid:
        m0, ml = mid
        m1 = min(m0 + ml, total)
        button(m0, m1, lx, lw, blue, "LIKE")                       # LIKE first ...
        button(min(m0 + 1.0, m1 - 0.5), m1, sx, sw, red, "SUBSCRIBE", pulse)   # ... then SUBSCRIBE
    if end:
        e0, el = end
        e1 = min(e0 + el, total)
        button(e0, e1, lx, lw, blue, "LIKE")
        button(e0, e1, sx, sw, red, "SUBSCRIBE", pulse)
        if tamil:
            out.append(f"Dialogue: 2,{ass_time(e0 + 0.3)},{ass_time(e1)},Ta,0,0,0,,{{\\an5\\pos({w // 2},{y + int(95 * scale)})\\fad(250,200)}}லைக் செய்யுங்கள் • சப்ஸ்கிரைப் செய்யுங்கள்")
    Path(path).write_text(head + "\n".join(out) + "\n", encoding="utf-8")


def burn(src, dst, ass):
    subprocess.run(["ffmpeg", "-y", "-i", str(src), "-vf", f"ass={ass}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(dst)], check=True, capture_output=True)


def long_video(src, dst, total):
    """Long video: one-by-one pop at ~42 % of the video (4.5 s), both buttons again over the last 7 s."""
    ass = Path(dst).with_suffix(".ass")
    # bottom corners, so the small picture caption in the middle of the bottom edge stays readable
    make_ass(ass, 1280, 720, total, y=648, scale=0.55, mid=(total * 0.42, 4.5), end=(max(total - 7.5, 1), 7.0), tamil=False, lfrac=0.095, sfrac=0.885)
    burn(src, dst, ass)


def end_card_ass(path, w, h, t0, dur, lines, speech_start, speech_dur, y_text, ys, bw=720, bh=130):
    """Closing card of a Short (owner 2026-11-24): the spoken line is shown on the card and highlighted word by word while it is read
    (karaoke); LIKE, SUBSCRIBE and COMMENT buttons pop in one by one under it. lines = list of lines (each a list of words)."""
    font = os.environ.get("SUB_FONT") or "Noto Sans Tamil"
    latin = os.environ.get("SUB_LATIN_FONT") or "DejaVu Sans"
    head = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nWrapStyle: 2\n\n[V4+ Styles]\n"
            "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,"
            "ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\n"
            f"Style: Btn,{latin},64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n"
            f"Style: Rd,{font},72,&H0000D7FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,6,2,5,0,0,0,1\n\n"
            "[Events]\nFormat: Layer,Start,End,Style,MarginL,MarginR,MarginV,Effect,Text\n")
    out = []
    end = t0 + dur
    words = [wd for ln in lines for wd in ln]
    weight = [max(len(wd), 2) for wd in words]
    cs_total = max(int(speech_dur * 100), len(words))
    cs = [max(1, int(cs_total * x / sum(weight))) for x in weight]
    # the line starts a little before the voice so the first word is not highlighted late
    lead = max(int((speech_start - t0) * 100), 0)
    parts, idx = [], 0
    for ln in lines:
        seg = []
        for wd in ln:
            seg.append(("{\\k%d}" % lead if idx == 0 else "") + ("{\\kf%d}" % cs[idx]) + wd)
            idx += 1
        parts.append(" ".join(seg))
    out.append(f"Dialogue: 3,{ass_time(t0)},{ass_time(end)},Rd,0,0,0,,{{\\an5\\pos({w // 2},{y_text})\\fad(200,0)}}" + "\\N".join(parts))
    cols = [(r"\1c&HE5881E&", "LIKE"), (r"\1c&H0000FF&", "SUBSCRIBE"), (r"\1c&H008CFF&", "COMMENT")]
    pop = r"\fscx40\fscy40\t(0,350,\fscx108\fscy108)\t(350,500,\fscx100\fscy100)"
    for i, ((col, label), y) in enumerate(zip(cols, ys)):
        b0 = t0 + 0.6 + 0.45 * i
        out.append(f"Dialogue: 1,{ass_time(b0)},{ass_time(end)},Btn,0,0,0,,{{\\an5\\pos({w // 2},{y})\\bord0\\shad0{col}\\fad(120,0){pop}\\p1}}{rrect(bw, bh, 34)}{{\\p0}}")
        out.append(f"Dialogue: 2,{ass_time(b0)},{ass_time(end)},Btn,0,0,0,,{{\\an5\\pos({w // 2},{y})\\fad(120,0){pop}}}{label}")
    Path(path).write_text(head + "\n".join(out) + "\n", encoding="utf-8")
