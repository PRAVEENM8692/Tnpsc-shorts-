"""Manim animations drawn OVER the story pictures (transparent background, 1280x720, 30 fps).
tools/story/build.py runs this once per animation:

  OV_JSON=anim.json manim -qm --fps 30 -t --format=mov -o tl1.mov --media_dir out/story/work/manim \
      tools/story/overlay_anim.py Overlay

anim.json = one entry of "anims" in the story file plus "steps": [seconds, ...], one per item. Every item appears at the
start of its step and stays, so the animation moves in time with the voice. Kinds: timeline, list, table, route.
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

    # ---- a list that grows, on the right side ----------------------------------------------------------
    def k_list(self):
        items = D["items"]
        box = panel(5.3, 1.5 + 0.95 * len(items), [4.2, 0.2, 0])
        title = T(D.get("title", ""), 30, GOLD, max_w=4.8).move_to(box.get_top() + DOWN * 0.55)
        top = title.get_bottom()[1] - 0.75
        for i, (year, name) in enumerate(items):
            yr = T(year, 36, GOLD)
            nm = T(name, 34, WHITE, max_w=2.9)
            row = VGroup(yr, nm).arrange(RIGHT, buff=0.35).move_to([4.2, top - 0.95 * i, 0])
            row.align_to(box.get_left() + RIGHT * 0.45, LEFT)
            anims = [FadeIn(row, shift=LEFT * 0.4)]
            if i == 0:
                anims = [FadeIn(box), FadeIn(title)] + anims
            self.step(i, *anims)

    # ---- a two-column table that fills row by row, on the left side ----------------------------------
    def k_table(self):
        items = D["items"]
        cx = -3.9
        box = panel(6.1, 2.3 + 0.95 * len(items), [cx, 0.2, 0])
        title = T(D.get("title", ""), 32, GOLD, max_w=5.6).move_to(box.get_top() + DOWN * 0.55)
        h1, h2 = D.get("head", ["", ""])
        head_y = title.get_bottom()[1] - 0.6
        ha = T(h1, 26, "#CFD3FF").move_to([cx - 1.5, head_y, 0])
        hb = T(h2, 26, "#CFD3FF").move_to([cx + 1.6, head_y, 0])
        rule = Line([cx - 2.8, head_y - 0.35, 0], [cx + 2.8, head_y - 0.35, 0], color=GOLD, stroke_width=3)
        for i, (a, b) in enumerate(items):
            ry = head_y - 0.95 * (i + 1)
            ta = T(a, 30, WHITE, max_w=2.9).move_to([cx - 1.5, ry, 0])
            tb = T(b, 30, GOLD, max_w=2.5).move_to([cx + 1.6, ry, 0])
            anims = [FadeIn(ta, shift=RIGHT * 0.3), FadeIn(tb, shift=RIGHT * 0.3)]
            if i == 0:
                anims = [FadeIn(box), FadeIn(title), FadeIn(ha), FadeIn(hb), Create(rule)] + anims
            self.step(i, *anims)

    # ---- a north-to-south route (places placed by latitude / longitude; a diagram, not a map) ---------
    def k_route(self):
        items = D["items"]
        cx = 3.9
        box = panel(6.2, 7.3, [cx, 0, 0])
        title = T(D.get("title", ""), 26, GOLD, max_w=5.7).move_to(box.get_top() + DOWN * 0.45)
        name0, lon0, lat0 = D["start"]
        lats = [lat0] + [it[3] for it in items]
        top, bot = 2.45, -3.1                     # the y range used for the places
        k = (top - bot) / (max(lats) - min(lats))

        def pos(lon, lat):
            return [cx + 0.15 + (lon - 77.5) * 0.2, bot + (lat - min(lats)) * k, 0]

        p_prev = pos(lon0, lat0)
        d0 = Dot(p_prev, radius=0.13, color=WHITE)
        l0 = T(name0, 30, WHITE).next_to(d0, RIGHT, buff=0.2)
        north = T("வடக்கு", 20, "#CFD3FF", weight=NORMAL).move_to(box.get_corner(UL) + RIGHT * 0.8 + DOWN * 1.15)
        south = T("தெற்கு", 20, "#CFD3FF", weight=NORMAL).move_to(box.get_corner(DL) + RIGHT * 0.8 + UP * 0.35)
        for i, (year, name, lon, lat, side) in enumerate(items):
            p = pos(lon, lat)
            seg = Arrow(p_prev, p, buff=0.16, color=RED, stroke_width=7, max_tip_length_to_length_ratio=0.12)
            dot = Dot(p, radius=0.12, color=GOLD)
            lab = VGroup(T(name, 26, WHITE, max_w=2.3), T(year, 26, GOLD)).arrange(DOWN, buff=0.06)
            lab.next_to(dot, LEFT if side == "L" else RIGHT, buff=0.3)
            anims = [GrowArrow(seg), FadeIn(dot, scale=2), FadeIn(lab)]
            if i == 0:
                anims = [FadeIn(box), FadeIn(title), FadeIn(north), FadeIn(south), FadeIn(d0), FadeIn(l0)] + anims
            self.step(i, *anims)
            p_prev = p
