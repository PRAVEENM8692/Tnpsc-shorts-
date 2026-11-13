"""Manim animations drawn OVER the story pictures (transparent background, 1280x720, 30 fps).
tools/story/build.py runs this once per animation:

  OV_JSON=anim.json manim -qm --fps 30 -t --format=mov -o tl1.mov --media_dir out/story/work/manim \
      tools/story/overlay_anim.py Overlay

anim.json = one entry of "anims" in the story file plus "steps": [seconds, ...], one per item. Every item appears at the
start of its step and stays, so the animation moves in time with the voice. Kinds: timeline, list, table, route.
The timeline keeps its original wide strip along the bottom; list, table and route are small boxes in the top right corner.
Text only (no LaTeX needed)."""
import json
import os

from manim import *

FONT = os.environ.get("OV_FONT", "Noto Sans Tamil")
GOLD, WHITE, INK, RED = "#FFD54A", "#FFFFFF", "#0A0A14", "#FF5A4A"
D = json.load(open(os.environ["OV_JSON"], encoding="utf-8"))
STEPS = [max(float(x), 0.9) for x in D["steps"]]


def T(text, size, color=WHITE, weight=BOLD, max_w=None):
    t = Text(str(text), font=FONT, font_size=size, color=color, weight=weight)
    if max_w and t.width > max_w:
        t.scale_to_fit_width(max_w)
    return t


def panel(w, h, at):
    return RoundedRectangle(corner_radius=0.25, width=w, height=h, stroke_color=GOLD, stroke_width=4,
                            fill_color=INK, fill_opacity=0.8).move_to(at)


PW = 3.9                     # width of the small box
RIGHT_X, TOP_Y = 6.95, 3.85   # the box sits in the top right corner, mostly over the blurred side of the picture


def corner(h, w=PW):
    """The small dark box in the top right corner."""
    return RoundedRectangle(corner_radius=0.2, width=w, height=h, stroke_color=GOLD, stroke_width=3,
                            fill_color=INK, fill_opacity=0.82).move_to([RIGHT_X - w / 2, TOP_Y - h / 2, 0])


class Overlay(Scene):
    def step(self, i, *anims):
        """Plays the reveal of item i, then waits for the rest of its step. The last step ends with a quick fade-out."""
        d = STEPS[i]
        last = i == len(STEPS) - 1
        rt = min(0.8, d * 0.5)
        self.play(*anims, run_time=rt)
        rest = d - rt - (0.3 if last else 0)
        if rest > 0.05:
            self.wait(rest)
        if last:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.3)

    def construct(self):
        getattr(self, "k_" + D["kind"])()

    def head(self, box, text):
        """Title line inside the box; returns (title or None, y of the first row)."""
        if not text:
            return None, box.get_top()[1] - 0.55
        t = T(text, 22, GOLD, max_w=PW - 0.4).move_to([box.get_center()[0], box.get_top()[1] - 0.4, 0])
        return t, box.get_top()[1] - 1.05

    # ---- a line of years along the bottom ------------------------------------------------------------
    def k_timeline(self):
        items = D["items"]
        y = -2.55
        box = panel(13.2, 2.3, [0, y, 0])
        n = len(items)
        xs = [0.0] if n == 1 else [-3.6 + 7.2 * i / (n - 1) for i in range(n)]
        x_prev = -6.0
        for i, (year, label) in enumerate(items):
            seg = Line([x_prev, y, 0], [xs[i], y, 0], color=GOLD, stroke_width=6)
            dot = Dot([xs[i], y, 0], radius=0.14, color=WHITE)
            yr = T(year, 44, GOLD).next_to(dot, UP, buff=0.18)
            lb = T(label, 30, WHITE, max_w=5.6).next_to(dot, DOWN, buff=0.2)
            anims = [Create(seg), FadeIn(dot, scale=2), FadeIn(yr, shift=UP * 0.2), FadeIn(lb, shift=DOWN * 0.2)]
            if i == 0:
                anims.insert(0, FadeIn(box))
            self.step(i, *anims)
            x_prev = xs[i]

    # ---- a list that grows -----------------------------------------------------------------------------
    def k_list(self):
        items = D["items"]
        gap = 0.62
        box = corner((1.25 if D.get("title") else 0.7) + gap * len(items))
        title, y0 = self.head(box, D.get("title"))
        left = box.get_left()[0] + 0.3
        for i, (year, name) in enumerate(items):
            yr = T(year, 26, GOLD)
            nm = T(name, 26, WHITE, max_w=PW - 1.9)
            row = VGroup(yr, nm).arrange(RIGHT, buff=0.25).move_to([0, y0 - gap * i, 0]).align_to([left, 0, 0], LEFT)
            anims = [FadeIn(row, shift=LEFT * 0.3)]
            if i == 0:
                anims = [FadeIn(box)] + ([FadeIn(title)] if title else []) + anims
            self.step(i, *anims)

    # ---- two columns that fill row by row ---------------------------------------------------------------
    def k_table(self):
        items = D["items"]
        gap = 0.62
        box = corner((1.25 if D.get("title") else 0.7) + gap * len(items))
        title, y0 = self.head(box, D.get("title"))
        left, right = box.get_left()[0] + 0.3, box.get_right()[0] - 0.3
        for i, (a, b) in enumerate(items):
            ta = T(a, 24, WHITE, max_w=PW - 2.0).move_to([0, y0 - gap * i, 0]).align_to([left, 0, 0], LEFT)
            tb = T(b, 20, GOLD, max_w=1.3).move_to([0, y0 - gap * i, 0]).align_to([right, 0, 0], RIGHT)
            anims = [FadeIn(ta, shift=RIGHT * 0.2), FadeIn(tb, shift=RIGHT * 0.2)]
            if i == 0:
                anims = [FadeIn(box)] + ([FadeIn(title)] if title else []) + anims
            self.step(i, *anims)

    # ---- a north-to-south route: places one under the other, shifted a little east or west (a diagram, not a map) ----
    def k_route(self):
        items = D["items"]
        gap = 0.72
        box = corner(1.3 + gap * (len(items) + 1))
        title, y0 = self.head(box, D.get("title"))
        left = box.get_left()[0] + 0.45
        name0, lon0, _lat0 = D["start"]
        lons = [lon0] + [it[2] for it in items]

        def px(lon):
            return left + (lon - min(lons)) * 0.09

        p_prev = [px(lon0), y0, 0]
        d0 = Dot(p_prev, radius=0.1, color=WHITE)
        l0 = T(name0, 24, WHITE).next_to(d0, RIGHT, buff=0.22)
        for i, (year, name, lon, _lat, _side) in enumerate(items):
            p = [px(lon), y0 - gap * (i + 1), 0]
            seg = Arrow(p_prev, p, buff=0.13, color=RED, stroke_width=5, max_tip_length_to_length_ratio=0.25)
            dot = Dot(p, radius=0.1, color=GOLD)
            lab = VGroup(T(name, 22, WHITE, max_w=PW - 2.2), T(year, 22, GOLD)).arrange(RIGHT, buff=0.18)
            lab.move_to([0, p[1], 0]).align_to([left + 0.75, 0, 0], LEFT)
            anims = [GrowArrow(seg), FadeIn(dot, scale=2), FadeIn(lab)]
            if i == 0:
                anims = [FadeIn(box)] + ([FadeIn(title)] if title else []) + [FadeIn(d0), FadeIn(l0)] + anims
            self.step(i, *anims)
            p_prev = p
