"""
manim_aptitude.py  -  TNPSC Aptitude Short (9:16): question, steps and answer animated in time with the voice.
Text only (no LaTeX needed).

pipeline.py runs this for you. To try it alone:
  APT_JSON=apt.json APT_DURATION=40 APT_DATE="01 Nov 2026" \
  manim -qm --fps 30 -o aptitude.mp4 manim_aptitude.py AptitudeShort

apt.json:
{
  "topic": "சதவீதம்",
  "question": "200-ன் 15% எவ்வளவு?",
  "steps": ["10% = 20", "5% = 10", "15% = 20 + 10"],
  "answer": "30",
  "practice": "300-ன் 15% எவ்வளவு?",            (optional: shown during the last part)
  "cues": {"question": 3.2, "steps": [6.0, 9.5, 13.0], "answer": 16.0, "practice": 24.0}   (optional, seconds)
}

Settings (environment):  APT_JSON, APT_DURATION (video length in seconds), APT_HEADER (1 = draw the TNPSC header
here, 0 = leave the top empty because pipeline.py draws its own), APT_DATE, APT_FONT.
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
# colours: pipeline.py picks a random theme for every video (APT_THEME = JSON); run alone, the navy-gold one is used
try:
    _TH = json.loads(os.environ.get("APT_THEME") or "{}")
except ValueError:
    _TH = {}
BG = _TH.get("bg", "#0B1B3A")
PANEL = _TH.get("panel", "#12306B")
GOLD = _TH.get("gold", "#FFC93C")
WHITE = _TH.get("white", "#FFFFFF")
GREEN = _TH.get("green", "#3DDC84")
CARD = _TH.get("card", "#1B3F8F")
CARD2 = _TH.get("card2", "#16357A")
RAD = float(_TH.get("rad", 1.0))   # how round the corners are (1 = normal)
COUNTDOWN_MIN = 3.4                # show the 3-2-1 countdown only if the question part lasts at least this many seconds

CARD_W = 8.4   # width of the boxes
MAX_W = 8.0    # widest text allowed


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


def T(text, size=40, color=WHITE, weight=NORMAL, max_chars=22, max_w=MAX_W):
    m = Text(wrap(text, max_chars), font=FONT, font_size=size, color=color, weight=weight, line_spacing=0.9)
    if m.width > max_w:
        m.scale_to_fit_width(max_w)
    return m


class AptitudeShort(Scene):
    def construct(self):
        data = json.load(open(os.environ.get("APT_JSON", "apt.json"), encoding="utf-8"))
        total = float(os.environ.get("APT_DURATION", "40"))
        date_txt = os.environ.get("APT_DATE", "")
        header_on = os.environ.get("APT_HEADER", "1") == "1"
        self.camera.background_color = BG

        steps = [str(s) for s in data["steps"]]
        n = len(steps)
        topic = str(data.get("topic", "") or "")
        practice = str(data.get("practice", "") or "")

        # content area: below the header (pipeline.py draws it in the top ~440 px) and above the running captions
        top = 4.5 if header_on else 4.0
        bottom = -2.4
        region_h = top - bottom

        # ---------- header (only when this file is run on its own) ----------
        header = None
        if header_on:
            panel = RoundedRectangle(corner_radius=0.3 * RAD, width=8.4, height=2.6, fill_color=PANEL, fill_opacity=1,
                                     stroke_color=GOLD, stroke_width=3)
            h1 = Text("TNPSC", font_size=54, color=GOLD, weight=BOLD)
            h2 = Text("APTITUDE TRICKS", font_size=36, color=WHITE, weight=BOLD)
            items = [h1, h2]
            if topic:
                items.append(Text(topic, font=FONT, font_size=30, color=WHITE))
            if date_txt:
                items.append(Text(date_txt, font_size=22, color=GOLD))
            VGroup(*items).arrange(DOWN, buff=0.12).move_to(panel)
            header = VGroup(panel, *items).to_edge(UP, buff=0.6)

        # ---------- opening title (while the voice says the hook) ----------
        hook = None
        if topic:
            hook = VGroup(
                Text("கணக்கு ஷார்ட்கட்", font=FONT, font_size=34, color=WHITE),
                T(topic, size=72, color=GOLD, weight=BOLD, max_chars=14),
            ).arrange(DOWN, buff=0.35)
            hook.move_to(np.array([0.0, (top + bottom) / 2, 0.0]))

        # ---------- build everything first, then reveal it piece by piece ----------
        # question card
        q_label = Text("கேள்வி", font=FONT, font_size=24, color=GOLD, weight=BOLD)
        q_text = T(data["question"], size=40, color=WHITE, max_chars=24, max_w=CARD_W - 0.6)
        q_inner = VGroup(q_label, q_text).arrange(DOWN, buff=0.15)
        q_box = RoundedRectangle(corner_radius=0.25 * RAD, width=CARD_W, height=q_inner.height + 0.5,
                                 fill_color=CARD, fill_opacity=1, stroke_width=0)
        q_inner.move_to(q_box)
        q_all = VGroup(q_box, q_inner)

        # quiz layout: four answer chips under the question; the right one lights up green when the answer is announced
        options = [str(o) for o in (data.get("options") or [])][:4]
        correct = int(data.get("correct", 0))
        quiz = len(options) == 4 and 0 <= correct < 4
        chips = []
        if quiz:
            cw = (CARD_W - 0.25) / 2
            for k, o in enumerate(options):
                box = RoundedRectangle(corner_radius=0.2 * RAD, width=cw, height=0.95, fill_color=CARD2, fill_opacity=1,
                                       stroke_color=CARD, stroke_width=2)
                dot = Circle(radius=0.27, fill_color=GOLD, fill_opacity=1, stroke_width=0)
                let = Text("ABCD"[k], font_size=28, color=BG, weight=BOLD).move_to(dot)
                badge = VGroup(dot, let).move_to(box.get_left() + RIGHT * 0.5)
                val = Text(o, font=FONT, font_size=36, color=WHITE, weight=BOLD)
                if val.width > cw - 1.2:
                    val.scale_to_fit_width(cw - 1.2)
                val.next_to(badge, RIGHT, buff=0.25)
                chips.append(VGroup(box, badge, val))
            grid = VGroup(*chips).arrange_in_grid(rows=2, cols=2, buff=(0.25, 0.2))
        else:
            grid = None

        # step cards: [box, badge, text]
        rows = []
        for i, s in enumerate(steps, 1):
            dot = Circle(radius=0.28, fill_color=GOLD, fill_opacity=1, stroke_width=0)
            num = Text(str(i), font_size=30, color=BG, weight=BOLD).move_to(dot)
            badge = VGroup(dot, num)
            txt = T(s, size=34, color=WHITE, max_chars=26, max_w=CARD_W - 1.5)
            box = RoundedRectangle(corner_radius=0.2 * RAD, width=CARD_W, height=max(txt.height + 0.3, 0.85),
                                   fill_color=CARD2, fill_opacity=1, stroke_color=CARD, stroke_width=2)
            badge.move_to(box.get_left() + RIGHT * 0.55)
            txt.next_to(badge, RIGHT, buff=0.3)
            rows.append(VGroup(box, badge, txt))

        # answer banner
        ans_label = Text("விடை", font=FONT, font_size=32, color=BG, weight=BOLD)
        ans_val = Text(str(data["answer"]), font=FONT, font_size=60, color=BG, weight=BOLD)
        ans_inner = VGroup(ans_label, ans_val).arrange(RIGHT, buff=0.45)
        if ans_inner.width > CARD_W - 0.8:
            ans_inner.scale_to_fit_width(CARD_W - 0.8)
        ans_box = RoundedRectangle(corner_radius=0.3 * RAD, width=CARD_W, height=ans_inner.height + 0.5,
                                   fill_color=GREEN, fill_opacity=1, stroke_color=WHITE, stroke_width=4)
        ans_inner.move_to(ans_box)
        ans_group = VGroup(ans_box, ans_inner)

        # stack them (top aligned in the content area; shrink a little if it would be too tall)
        parts = [q_all] + ([grid] if quiz else []) + rows + ([] if quiz else [ans_group])
        layout = VGroup(*parts).arrange(DOWN, buff=0.22)
        if layout.height > region_h:
            layout.scale_to_fit_height(region_h)
        layout.move_to(np.array([0.0, top - layout.height / 2, 0.0]))

        # practice card (shown while the voice gives the practice question)
        practice_group = None
        if practice:
            p_label = Text("உங்க முறை!", font=FONT, font_size=36, color=GOLD, weight=BOLD)
            p_text = T(practice, size=44, color=WHITE, max_chars=22, max_w=CARD_W - 0.8)
            p_inner = VGroup(p_label, p_text).arrange(DOWN, buff=0.3)
            p_box = RoundedRectangle(corner_radius=0.3 * RAD, width=CARD_W, height=p_inner.height + 0.9,
                                     fill_color=CARD, fill_opacity=1, stroke_color=GOLD, stroke_width=4)
            p_inner.move_to(p_box)
            practice_group = VGroup(p_box, p_inner)
            practice_group.move_to(np.array([0.0, top - practice_group.height / 2 - 0.4, 0.0]))

        # ---------- when each part appears (seconds) ----------
        cues = data.get("cues") or {}
        cq, cs, ca, cp = cues.get("question"), cues.get("steps"), cues.get("answer"), cues.get("practice")
        if cq is None or not cs or len(cs) < n or ca is None:
            gap = max((0.8 * total - 1.0) / (n + 1), 0.8)
            cq = 1.0
            cs = [cq + gap * (i + 1) for i in range(n)]
            ca = cq + gap * (n + 1)
            cp = (ca + gap) if practice else None

        def at(sec):
            d = float(sec) - self.renderer.time
            if d > 0.02:
                self.wait(d)

        # ---------- play ----------
        if header is not None:
            self.play(FadeIn(header, shift=DOWN * 0.3), run_time=0.8)
        if hook is not None:
            self.play(FadeIn(hook, shift=UP * 0.2), run_time=0.6)

        at(cq)
        if hook is not None:
            self.play(FadeOut(hook), FadeIn(q_all, shift=UP * 0.3), run_time=0.6)
        else:
            self.play(FadeIn(q_all, shift=UP * 0.3), run_time=0.6)
        if quiz:
            self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips], lag_ratio=0.25), run_time=0.9)

        # 3-2-1 countdown: gives the viewer a moment to think before the first step appears
        if cs[0] - cq >= COUNTDOWN_MIN:
            at(cs[0] - 3.0)
            ring = Circle(radius=0.3, color=GOLD, stroke_width=6, fill_color=BG, fill_opacity=1)
            ring.move_to(q_box.get_corner(UR) + LEFT * 0.55)
            num = Text("3", font_size=34, color=GOLD, weight=BOLD).move_to(ring)
            clock = VGroup(ring, num)
            self.play(FadeIn(clock, scale=0.6), run_time=0.25)
            for k in (2, 1):
                at(cs[0] - k)
                new = Text(str(k), font_size=34, color=GOLD, weight=BOLD).move_to(ring)
                self.play(Transform(num, new), Indicate(ring, color=GOLD, scale_factor=1.18), run_time=0.3)
            at(cs[0] - 0.15)
            self.play(FadeOut(clock), run_time=0.15)

        for row, t in zip(rows, cs):
            at(t)
            self.play(FadeIn(row, shift=RIGHT * 0.4), run_time=0.5)
            self.play(Indicate(row[2], color=GOLD, scale_factor=1.06), run_time=0.4)

        at(ca)
        if quiz:
            win = chips[correct]
            others = [c for k, c in enumerate(chips) if k != correct]
            self.play(win[0].animate.set_fill(GREEN, 1).set_stroke(WHITE, 4), win[2].animate.set_color(BG),
                      *[c.animate.set_opacity(0.3) for c in others], run_time=0.5)
            focus = win
            self.play(Indicate(win, color=GREEN, scale_factor=1.08), run_time=0.4)
        else:
            self.play(GrowFromCenter(ans_group), run_time=0.6)
            focus = ans_group
        self.play(Flash(focus, color=GREEN, flash_radius=2.4, line_length=0.35), run_time=0.5)
        # confetti
        rng = np.random.default_rng(int(total * 100) % 9999)
        colors = [GOLD, GREEN, WHITE, "#FF6B9D", "#5CE1FF"]
        bits = VGroup(*[Square(side_length=float(rng.uniform(0.1, 0.2)), fill_opacity=1, stroke_width=0,
                               fill_color=colors[k % len(colors)]).rotate(float(rng.uniform(0, 3))).move_to(focus.get_center())
                        for k in range(30)])
        self.add(bits)
        self.play(*[b.animate.shift(np.array([float(rng.uniform(-4, 4)), float(rng.uniform(-1.5, 3.2)), 0])).set_opacity(0)
                    for b in bits], run_time=1.2, rate_func=rush_from)
        self.remove(bits)

        if practice_group is not None and cp is not None:
            at(cp)
            gone = [q_all, *rows] + ([grid] if quiz else [ans_group])
            self.play(FadeOut(*gone), FadeIn(practice_group, shift=UP * 0.3), run_time=0.7)

        at(total)
        self.wait(0.3)
