"""
manim_aptitude.py  -  TNPSC Aptitude Short (9:16) visual layer, Text-only (no LaTeX needed)

Run:
  APT_JSON=apt.json APT_DURATION=40 APT_DATE="01 Nov 2026" \
  manim -qm --fps 30 -o aptitude.mp4 manim_aptitude.py AptitudeShort

apt.json example:
{
  "topic": "சதவீதம்",
  "question": "200-ன் 15% எவ்வளவு?",
  "steps": [
    "10% = 20",
    "5% = 10 (10%-ன் பாதி)",
    "15% = 20 + 10"
  ],
  "answer": "30"
}
"""
import json
import os

from manim import *

# ---- 9:16 Shorts frame -------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16

FONT = os.environ.get("APT_FONT", "Noto Sans Tamil")
BG = "#0B1B3A"
PANEL = "#12306B"
GOLD = "#FFC93C"
WHITE = "#FFFFFF"
GREEN = "#3DDC84"
CARD = "#1B3F8F"

MAX_W = 8.0  # usable width inside the 9-unit frame


def wrap(text, max_chars=22):
    """Simple word wrap so long Tamil lines don't run off screen."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def T(text, size=40, color=WHITE, weight=NORMAL, max_chars=22):
    m = Text(wrap(text, max_chars), font=FONT, font_size=size, color=color, weight=weight, line_spacing=0.9)
    if m.width > MAX_W:
        m.scale_to_fit_width(MAX_W)
    return m


class AptitudeShort(Scene):
    def construct(self):
        data = json.load(open(os.environ.get("APT_JSON", "apt.json"), encoding="utf-8"))
        total = float(os.environ.get("APT_DURATION", "40"))
        date_txt = os.environ.get("APT_DATE", "")

        self.camera.background_color = BG
        steps = data["steps"]
        n = len(steps)

        # ---------- header panel (fixed at top) ----------
        panel = RoundedRectangle(corner_radius=0.3, width=8.4, height=2.6, fill_color=PANEL, fill_opacity=1, stroke_color=GOLD, stroke_width=3)
        h1 = Text("TNPSC", font_size=54, color=GOLD, weight=BOLD)
        h2 = Text("APTITUDE TRICKS", font_size=36, color=WHITE, weight=BOLD)
        h3 = Text(data.get("topic", "கணக்கு குறுக்குவழி"), font=FONT, font_size=30, color=WHITE)
        header_items = [h1, h2, h3]
        if date_txt:
            header_items.append(Text(date_txt, font_size=22, color=GOLD))
        VGroup(*header_items).arrange(DOWN, buff=0.12).move_to(panel)
        header = VGroup(panel, *header_items).to_edge(UP, buff=0.6)

        # ---------- time budget ----------
        # fixed animation time: header 0.8 + question 1.2 + steps n*1.0 + answer 1.2
        fixed = 0.8 + 1.2 + n * 1.0 + 1.2
        slack = max(0.0, total - fixed)
        pause = slack / (n + 2)  # hold after question, each step, and answer

        # ---------- header in ----------
        self.play(FadeIn(header, shift=DOWN * 0.3), run_time=0.8)

        # ---------- question ----------
        q_label = Text("கேள்வி", font=FONT, font_size=30, color=GOLD, weight=BOLD)
        q_text = T(data["question"], size=46, color=WHITE, max_chars=20)
        q_box = RoundedRectangle(corner_radius=0.25, width=8.4, height=q_text.height + 1.3, fill_color=CARD, fill_opacity=1, stroke_width=0)
        q_group = VGroup(q_label, q_text).arrange(DOWN, buff=0.25).move_to(q_box)
        q_all = VGroup(q_box, q_group).next_to(header, DOWN, buff=0.5)
        self.play(FadeIn(q_all, shift=UP * 0.3), run_time=1.2)
        self.wait(pause)

        # ---------- steps ----------
        prev = q_all
        step_mobs = []
        for i, s in enumerate(steps, 1):
            num = Text(str(i), font_size=34, color=BG, weight=BOLD)
            dot = Circle(radius=0.32, fill_color=GOLD, fill_opacity=1, stroke_width=0)
            num.move_to(dot)
            txt = T(s, size=38, color=WHITE, max_chars=24)
            row = VGroup(VGroup(dot, num), txt).arrange(RIGHT, buff=0.35)
            row.scale_to_fit_width(min(row.width, MAX_W))
            row.next_to(prev, DOWN, buff=0.55).align_to(q_all, LEFT).shift(RIGHT * 0.2)
            self.play(FadeIn(row, shift=RIGHT * 0.4), run_time=0.6)
            self.play(Indicate(txt, color=GOLD, scale_factor=1.08), run_time=0.4)
            self.wait(pause)
            step_mobs.append(row)
            prev = row

        # ---------- answer ----------
        ans_label = Text("விடை", font=FONT, font_size=34, color=BG, weight=BOLD)
        ans_val = Text(str(data["answer"]), font_size=84, color=GREEN, weight=BOLD)
        if ans_val.width > 7:
            ans_val.scale_to_fit_width(7)
        ans_inner = VGroup(ans_label, ans_val).arrange(DOWN, buff=0.15)
        ans_box = RoundedRectangle(corner_radius=0.3, width=6, height=ans_inner.height + 0.9, fill_color=WHITE, fill_opacity=1, stroke_color=GREEN, stroke_width=6)
        ans_inner.move_to(ans_box)
        ans_group = VGroup(ans_box, ans_inner)
        ans_group.next_to(prev, DOWN, buff=0.7)
        # keep inside the frame (leave room at bottom for Like/Subscribe overlay)
        floor = -config.frame_height / 2 + 2.2
        if ans_group.get_bottom()[1] < floor:
            ans_group.shift(UP * (floor - ans_group.get_bottom()[1]))
        self.play(GrowFromCenter(ans_group), run_time=0.7)
        self.play(Flash(ans_group, color=GREEN, flash_radius=2.6, line_length=0.4), run_time=0.5)
        self.wait(max(pause, 0.5))
