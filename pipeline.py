"""Free daily TNPSC current-affairs Tamil Short (runs on GitHub Actions).

news search (Tavily) -> English facts -> Tamil script (Groq/OpenAI-compatible LLM) -> Tamil check (tamil_quality.py) -> Tamil voice (Gemini TTS by default when GEMINI_API_KEY is set, free edge-tts as the fallback)
-> images (Pollinations) or Manim animation (aptitude) -> video + BGM (ffmpeg) -> YouTube upload (Data API)
"""
import asyncio
import datetime as dt
import json
import random
import os
import subprocess
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

import tamil_quality as tq

IST = ZoneInfo("Asia/Kolkata")
OUT = Path("out")
BGM = Path("assets/bgm.mp3")
W, H = 1080, 1920


def env(name, default=None):
    v = os.environ.get(name) or default  # GitHub passes unset variables as empty text
    if not v:
        sys.exit(f"Missing setting: {name}")
    return v


def log(msg):
    print(f"[{dt.datetime.now(IST):%H:%M:%S}] {msg}", flush=True)


# ---------------------------------------------------------------- 0. memory of past videos
HISTORY = Path("history.json")


def load_history():
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:
        return {"urls": [], "titles": []}


def save_history(h):
    h["urls"] = h["urls"][-400:]
    h["titles"] = h["titles"][-80:]
    h["done"] = dict(sorted(h.get("done", {}).items())[-3:])      # which slots were published, last 3 days
    h["tries"] = dict(sorted(h.get("tries", {}).items())[-15:])   # failed attempts per slot
    HISTORY.write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding="utf-8")


def avoid_text(h, n=25):
    t = h.get("titles", [])[-n:]
    if not t:
        return ""
    return ("\n\nThese topics were ALREADY covered in recent videos. Do NOT repeat them or their facts, "
            "pick different ones:\n" + "\n".join(f"- {x}" for x in t))


# ---------------------------------------------------------------- 1. news search
# 5 videos a day: 3 current affairs + 2 aptitude (see .github/workflows/daily.yml for the clock times)
SLOTS = {
    1: ("news", "Tamil Nadu", ["Tamil Nadu government announcement news", "Tamil Nadu scheme policy news today"],
        "Tamil Nadu government, schemes, places, appointments"),
    2: ("news", "India & economy", ["India national news important today", "India economy RBI budget scheme news"],
        "India national affairs, government decisions, laws, polity, economy, banking"),
    3: ("aptitude", "Aptitude A", None, None),
    4: ("news", "Science, sports & world", ["India science technology ISRO environment news",
                                          "India sports awards international summit news"],
        "science, technology, space, environment, sports, awards, international events"),
    5: ("aptitude", "Aptitude B", None, None),
}
APTITUDE_TOPICS = [
    "Percentage shortcuts", "Ratio and proportion", "Time and work", "Speed, time and distance",
    "Simple interest", "Compound interest shortcut", "Average", "Profit and loss", "HCF and LCM",
    "Ages problems", "Number series", "Square and cube tricks", "Mixtures and alligation",
    "Pipes and cisterns", "Trains problems", "Boats and streams", "Mensuration (area, perimeter)",
    "Divisibility rules", "Simplification (BODMAS tricks)", "Calendar and clock problems",
]





def search_news(queries, used_urls=()):
    key = env("TAVILY_API_KEY")
    seen, items = set(used_urls), []
    for q in queries:
        r = requests.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {key}"},
            json={"query": q, "topic": "news", "days": 3, "max_results": 6},
            timeout=60,
        )
        r.raise_for_status()
        for x in r.json().get("results", []):
            if x["url"] in seen:
                continue
            seen.add(x["url"])
            host = urllib.parse.urlparse(x["url"]).netloc.replace("www.", "")
            items.append({"title": x.get("title", ""), "host": host, "url": x["url"], "text": (x.get("content") or "")[:450]})
    if len(items) < 2:
        sys.exit("Too little news found; stopping instead of inventing facts.")
    notes = "\n".join(f"- {i['title']} ({i['host']}): {i['text']}" for i in items)
    hosts, urls = [], []
    for i in items:
        if i["host"] not in hosts:
            hosts.append(i["host"])
    return notes, hosts[:6], [i["url"] for i in items]


# ---------------------------------------------------------------- 2. Tamil script
_MODEL = {"name": None}


def pick_model(base, headers):
    """Ask the provider which chat models exist today and choose a good one."""
    r = requests.get(base + "/models", headers=headers, timeout=60)
    r.raise_for_status()
    ids = [m["id"] for m in r.json().get("data", []) if m.get("active", True)]
    bad = ("whisper", "guard", "tts", "orpheus", "embed", "safeguard")
    ids = [i for i in ids if not any(b in i.lower() for b in bad)]
    for pref in ("gpt-oss-120b", "llama-3.3-70b", "llama-4-maverick", "llama-4-scout",
                 "qwen", "kimi", "gpt-oss-20b", "llama-3.1-8b"):
        for i in ids:
            if pref in i.lower():
                return i
    if ids:
        return ids[0]
    sys.exit("No usable chat model found on the LLM provider.")


def llm_json(prompt, model=None, temperature=0.5, effort="low"):
    """model: use this model for this one call (for example LLM_MODEL_TA for translation review).
    temperature: lower = more careful (translation / review use 0.2). effort: 'low' or 'medium' (reasoning models)."""
    base = env("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    headers = {"Authorization": f"Bearer {env('LLM_API_KEY')}"}
    user_model = os.environ.get("LLM_MODEL") or ""
    if not _MODEL["name"]:
        _MODEL["name"] = user_model or "openai/gpt-oss-120b"   # llama-3.3-70b was retired (404); a 404 still auto-picks a current model
    use = {"name": model or _MODEL["name"]}

    def call(json_mode=True):
        payload = {"model": use["name"], "messages": [{"role": "user", "content": prompt}],
                   "temperature": temperature, "max_tokens": 6000 if effort == "low" else 9000}
        if "gpt-oss" in use["name"]:
            payload["reasoning_effort"] = effort  # reasoning models can use up the budget and return nothing
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        return requests.post(base + "/chat/completions", headers=headers, json=payload, timeout=180)

    r = call()
    if r.status_code in (400, 404):
        log(f"LLM error {r.status_code}: {r.text[:300]}")
        if not user_model and not model:  # you did not choose a model, so pick a current one automatically
            _MODEL["name"] = pick_model(base, headers)
            use["name"] = _MODEL["name"]
            log(f"using model: {_MODEL['name']}")
            r = call()
        if r.status_code == 400:
            r = call(json_mode=False)
    for attempt in range(4):
        if r.status_code == 429:  # free-tier rate limit: wait and retry
            log("LLM rate limited; waiting 30s")
            time.sleep(30)
            r = call()
            continue
        if r.status_code == 400:
            log(f"LLM 400 (attempt {attempt + 1}); retrying without JSON mode")
            time.sleep(3)
            r = call(json_mode=False)
            continue
        if not r.ok:
            sys.exit(f"LLM error {r.status_code}: {r.text[:500]}")
        txt = (r.json()["choices"][0]["message"].get("content") or "").strip()
        a, b = txt.find("{"), txt.rfind("}")
        if a >= 0 and b > a:
            try:
                return json.loads(txt[a:b + 1])
            except json.JSONDecodeError:
                pass
        log(f"LLM returned no valid JSON (attempt {attempt + 1}); retrying")
        time.sleep(5)
        r = call()
    sys.exit("LLM kept returning invalid JSON.")


def write_script(notes, today, focus="", part=1, total=1, avoid=""):
    prompt = f"""You write 45-second YouTube Shorts for TNPSC aspirants in simple spoken TAMIL.
Date: {today}.
Use ONLY facts that appear in these news notes. Do not add facts from memory:
{notes}

{tq.translation_rules(notes)}

This is video {part} of {total} today, so cover ONLY this theme: {focus}. Pick the 5 most exam-relevant facts for that theme. Make them EASY TO REMEMBER: a punchy hook
line, one short sentence per fact, ONE memory trick (a catchy word, acronym or rhyme in Tamil), then a quick
question for viewers and a line asking them to follow for daily current affairs.
The voiceover must be 90-115 Tamil words, written exactly as it should be spoken (no emojis, no bullets).

Return JSON with keys:
title (Tamil, under 85 characters),
description (Tamil, 3-5 line recap of the facts),
tags (list of 8 strings, Tamil and English),
voiceover (Tamil),
scenes (list of exactly 5 English prompts, one per fact in the order they are spoken. Each is a vertical
cinematic image that visually relates to THAT fact: places, buildings, objects and symbols, for example
Fort St George Chennai, a laptop with students, a glowing light bulb, a gold ring on silk, Tamil Nadu map
with festival lamps. NO text or letters in the image, NO logos, NO faces, NO real people or politicians).

Language rules for the voiceover (it is read by a Tamil text-to-speech voice): write in Tamil script; everyday English words that Tamil speakers normally use (bank, online, mobile, budget, school) are written in Tamil letters; a name, scheme name, abbreviation or technical term with no good Tamil form stays in English letters exactly as in the news (never invent a Tamil translation for it, the program makes the voice say it correctly); write numbers as digits (the program turns them into spoken Tamil words), no brackets, quotes or hyphens; keep
abbreviations (TNPSC, GST, RBI) in English capital letters; use short sentences of at most
12 words, simple everyday words, a comma wherever a speaker would pause, and avoid very long compound words."""
    hint = ""
    for attempt in range(5):
        d = llm_json(prompt + avoid + hint)
        words = len(d.get("voiceover", "").split())
        lo = 70 if attempt < 3 else 55
        if all(k in d for k in ("title", "description", "tags", "voiceover", "scenes")) \
                and lo <= words <= 150 and len(d["scenes"]) >= 4:
            return d
        log(f"script attempt {attempt + 1} invalid (words={words}); retrying")
        hint = f"\n\nYour previous voiceover had only {words} words. Write at least 95 Tamil words."
    sys.exit("Could not get a valid script from the LLM.")


NEWS_SAY = ("say_hook", "say_f1", "say_f2", "say_f3", "say_f4", "say_f5", "say_tip", "say_outro")


def write_news_cards_script(notes, today, focus="", part=1, total=1, avoid=""):
    """Current-affairs script for the news-card video: the voice is written in PARTS (hook, fact 1-5, memory tip,
    outro) so each card appears exactly when its part starts. Raises (or exits) if the LLM cannot produce it."""
    prompt = f"""You write 45-second YouTube Shorts for TNPSC aspirants in simple spoken TAMIL. Date: {today}.
Use ONLY facts that appear in these news notes. Do not add facts, numbers or dates from memory:
{notes}

{tq.translation_rules(notes)}

This is video {part} of {total} today, so cover ONLY this theme: {focus}. Pick the 5 most exam-relevant facts for that theme.
The video shows ONE CARD per fact while a voice explains it, so every card text must say the SAME fact as its spoken part.

{CASUAL_TAMIL}

Return JSON with these keys:
title (Tamil, under 85 characters),
description (Tamil, 3-5 line recap of the facts),
tags (list of 8 strings, Tamil and English),
headline (Tamil, the hook as one screen headline, at most 60 characters),
cards (list of EXACTLY 5 objects, one per fact in spoken order, each with:
   title (Tamil, the fact's subject, at most 45 characters),
   detail (Tamil, one clear sentence with the key who / what / where, at most 110 characters, digits allowed),
   big (the single most important number, date or amount from the notes, at most 12 characters, for example "2026" or "5.5%", or an empty string if there is none)),
remember (Tamil, ONE catchy memory trick for the 5 facts, at most 60 characters),
quiz (Tamil, a quick question for the viewers about one of the facts, at most 60 characters),
scenes (list of exactly 5 English prompts, one per fact, each a vertical cinematic image that relates to that fact: places, buildings, objects and symbols. NO text or letters in the image, NO logos, NO faces, NO real people or politicians),
and the SPOKEN parts, each one to three short sentences:
say_hook (a punchy hook, about 12 words),
say_f1, say_f2, say_f3, say_f4, say_f5 (the five facts, one short sentence or two each),
say_tip (says the memory trick),
say_outro (asks the quiz question, then asks viewers to follow for daily current affairs).
All the spoken parts together must be 90-115 Tamil words.

Language rules for the spoken parts (they are read by a Tamil text-to-speech voice): write in Tamil script; everyday English words that Tamil speakers normally use (bank, online, mobile, budget, school) are written in Tamil letters; a name, scheme name, abbreviation or technical term with no good Tamil form stays in English letters exactly as in the news (never invent a Tamil translation for it, the program makes the voice say it correctly); write numbers as digits (the program turns them into spoken Tamil words), no brackets, quotes or hyphens; keep
abbreviations (TNPSC, GST, RBI) in English capital letters; use short sentences of at most
12 words, a comma wherever a speaker would pause, and avoid very long compound words."""
    hint = ""
    for attempt in range(5):
        d = llm_json(prompt + avoid + hint)
        parts = [(k[4:], str(d.get(k, "")).strip()) for k in NEWS_SAY]
        words = sum(len(t.split()) for _, t in parts)
        cards = d.get("cards")
        lo = 70 if attempt < 3 else 55
        ok = (all(k in d for k in ("title", "description", "tags", "headline", "remember", "quiz"))
              and all(t for _, t in parts) and isinstance(cards, list) and len(cards) >= 5
              and all(isinstance(c, dict) and str(c.get("title", "")).strip() and str(c.get("detail", "")).strip()
                      for c in cards[:5]) and lo <= words <= 150)
        if not ok:
            log(f"news cards script attempt {attempt + 1} invalid (words={words}); retrying")
            hint = (f"\n\nYour previous answer was invalid: the spoken parts had {words} words in total, or a key / card was "
                    "missing. Fill EVERY key, give exactly 5 cards and write at least 95 Tamil words in the spoken parts.")
            continue
        d["cards"] = [{"title": str(c["title"]).strip()[:60], "detail": str(c["detail"]).strip()[:150],
                       "big": str(c.get("big") or "").strip()[:14]} for c in cards[:5]]
        d["headline"] = str(d["headline"]).strip()[:80]
        d["remember"] = str(d["remember"]).strip()[:90]
        d["quiz"] = str(d["quiz"]).strip()[:90]
        d["parts"] = parts
        d["voiceover"] = " ".join(t for _, t in parts)
        return d
    sys.exit("Could not get a valid news-card script from the LLM.")


def safe_eval(expr):
    import ast
    import operator as op
    ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv, ast.Pow: op.pow,
           ast.USub: op.neg, ast.UAdd: op.pos, ast.Mod: op.mod}

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            l, r = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(r) > 6:
                raise ValueError("power too large")
            return ops[type(n.op)](l, r)
        if isinstance(n, ast.UnaryOp) and type(n.op) in ops:
            return ops[type(n.op)](ev(n.operand))
        raise ValueError("unsupported expression")
    return ev(ast.parse(str(expr), mode="eval"))


def apt_brief(topic):
    """Optional research step for the aptitude videos: Gemini (free tier) searches the web with Google Search and
    returns a short reference brief (typical TNPSC-style question, the standard shortcut trick, worked example) that
    the script writer then uses as source material. Needs the GEMINI_API_KEY secret; if it is missing, the free limit
    is used up or anything fails, it returns "" and the videos are made exactly as before."""
    key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if not key or (os.environ.get("APT_RESEARCH") or "1").strip() == "0":
        return ""
    model = (os.environ.get("GEMINI_TEXT_MODEL") or "gemini-2.5-flash").strip()
    q = (f"Search the web for TNPSC / Tamil Nadu competitive exam aptitude and mental ability questions on the topic "
         f"'{topic}'. Give a short reference brief in English (under 220 words): (1) one realistic exam-style question "
         f"with small numbers, (2) the standard SHORTCUT trick that saves time versus the long method, in 3 steps, "
         f"(3) the worked answer with the arithmetic, (4) one common mistake students make. Be exact; do not invent facts.")
    try:
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                          headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                          json={"contents": [{"parts": [{"text": q}]}], "tools": [{"google_search": {}}]}, timeout=120)
        if r.status_code != 200:
            log(f"aptitude research skipped (Gemini HTTP {r.status_code}): {r.text[:160]}")
            return ""
        parts = r.json()["candidates"][0]["content"]["parts"]
        text = " ".join(p.get("text", "") for p in parts).strip()
    except Exception as e:
        log(f"aptitude research skipped ({e})")
        return ""
    if len(text) < 80:
        return ""
    log(f"aptitude research brief from Gemini search ({len(text)} chars)")
    return ("\n\nREFERENCE BRIEF found by web search (use it as the source for the question type and the shortcut; "
            "make your own fresh numbers and story, and re-check every calculation yourself):\n" + text[:2200] + "\n")


def write_aptitude_script(topic, today, avoid=""):
    prompt = f"""You write 45-second YouTube Shorts for TNPSC / Tamil Nadu competitive-exam aspirants, in simple
spoken TAMIL. Date: {today}. Topic: {topic}.

Teach ONE solved aptitude question using a SHORTCUT TRICK that saves time compared with the long method.
Use small, easy numbers, and make the question DIFFERENT each day (random story, names of Tamil Nadu places, new numbers; variation code {random.randint(1000, 9999)}). Structure of the voiceover: a punchy hook, the question stated slowly, the shortcut
in 3-4 very short steps with the numbers, the final answer, a one-line memory tip, then a similar practice
question for the viewer and a line asking them to follow for daily TNPSC aptitude tricks.
The voiceover must be 90-115 Tamil words, written exactly as spoken (no emojis, no bullets, no markdown).
The maths MUST be correct.

Return JSON with keys:
title (Tamil, under 85 characters, mention the topic),
description (Tamil, 3-5 lines: the question, the trick, the answer),
tags (list of 8 strings, Tamil and English),
voiceover (Tamil),
check_expr (a plain Python arithmetic expression using only numbers and + - * / ** that evaluates to the final answer),
answer (the final numeric answer as a number),
scenes (list of exactly 5 English prompts for vertical cinematic images that relate to the problem's story or to
studying maths: for example a notebook and pencil on a desk, an old analog clock, coins and a calculator, a
train on a bridge, a balance scale. NO text or letters in the image, NO logos, NO faces, NO real people).

{CASUAL_APT}

Language rules for the voiceover (it is read by a Tamil text-to-speech voice): write in Tamil script; everyday English words that Tamil speakers normally use (bank, online, mobile, budget, school) are written in Tamil letters; a name, scheme name, abbreviation or technical term with no good Tamil form stays in English letters exactly as in the news (never invent a Tamil translation for it, the program makes the voice say it correctly); write numbers as digits (the program turns them into spoken Tamil words), no brackets, quotes or hyphens; keep
abbreviations (TNPSC, GST, RBI) in English capital letters; use short sentences of at most
12 words, simple everyday words, a comma wherever a speaker would pause, and avoid very long compound words."""
    hint = ""
    for attempt in range(6):
        d = llm_json(prompt + avoid + hint)
        words = len(d.get("voiceover", "").split())
        ok = all(k in d for k in ("title", "description", "tags", "voiceover", "scenes", "check_expr", "answer"))
        lo = 70 if attempt < 3 else 55  # accept slightly shorter scripts on later attempts
        if ok and lo <= words <= 150 and len(d["scenes"]) >= 4:
            try:
                got, want = float(safe_eval(d["check_expr"])), float(d["answer"])
                if abs(got - want) <= 1e-6 * max(1.0, abs(want)):
                    return d
                log(f"aptitude attempt {attempt + 1}: maths mismatch ({got} vs {want}); retrying")
                continue
            except Exception as e:
                log(f"aptitude attempt {attempt + 1}: cannot verify maths ({e}); retrying")
                continue
        log(f"aptitude attempt {attempt + 1} invalid (words={words}); retrying")
        hint = (f"\n\nYour previous voiceover had only {words} words. Write MORE: at least 95 Tamil words, "
                "with every step of the trick spoken in full sentences.")
    sys.exit("Could not get a verified aptitude script from the LLM.")


CASUAL_TAMIL = ("Style: speak like a friendly elder brother or sister teacher chatting casually with students: "
                "everyday SPOKEN Tamil (பேச்சுத் தமிழ்), NOT literary, formal or poetic Tamil (no புலவர் style, no bookish words). "
                "Use natural spoken forms such as பண்ணுங்க, பாருங்க, வாங்க, இருக்கு, சொல்றேன், வரும், ரொம்ப ஈசி, சரியா?; "
                "call the viewers நண்பர்களே or நீங்க; Tamil-letter English words such as ஷார்ட்கட், ஈசி, டிரிக் are welcome. "
                "Avoid stiff words like கணக்கிடுக, விடையைக் காண்க, பின்வருமாறு.")
CASUAL_APT = CASUAL_TAMIL + "\n" + tq.APT_RULES

SAY_KEYS = ("say_hook", "say_question", "say_step1", "say_step2", "say_step3", "say_answer", "say_tip", "say_outro")
FALLBACK_SCENES = ["a notebook and pencil on a wooden study desk, warm light", "an old analog clock on a study table",
                   "coins and a calculator on a desk", "a brass balance scale on a table",
                   "a stack of books beside a glowing lamp"]


def write_aptitude_manim_script(topic, today, avoid=""):
    """Aptitude script for the animated (Manim) video: the voice is written in PARTS (hook, question, step 1-3,
    answer, tip, outro) so the screen can change exactly when each part starts."""
    prompt = f"""You write 45-second YouTube Shorts for TNPSC / Tamil Nadu competitive-exam aspirants. Date: {today}. Topic: {topic}.

Teach ONE solved aptitude question using a SHORTCUT TRICK that saves time compared with the long method.
Use small, easy numbers and make the question DIFFERENT each day (random story, names of Tamil Nadu places, new numbers; variation code {random.randint(1000, 9999)}). The maths MUST be correct.
The video shows the question and the 3 steps on the screen while a voice explains them, so the spoken parts and the screen texts must use the SAME numbers.

{CASUAL_APT}

Return JSON with these keys:
title (Tamil, under 85 characters, mention the topic),
description (Tamil, 3-5 lines: the question, the trick, the answer),
tags (list of 8 strings, Tamil and English),
check_expr (a plain Python arithmetic expression using only numbers and + - * / ** that evaluates to the final answer),
answer (the final numeric answer as a number),
topic_ta (the topic name in Tamil, 1 to 3 words),
screen_question (the question as shown on the screen: Tamil with digits and symbols allowed, at most 60 characters),
screen_steps (list of EXACTLY 3 short lines for the screen, the same 3 steps that are spoken, each at most 26 characters, digits and symbols allowed, for example "10% = 20"),
screen_answer (the final answer for the screen, at most 14 characters, it must contain the number, for example "30 ரூபாய்"),
screen_practice (a similar practice question for the viewer, Tamil, at most 60 characters),
and the SPOKEN parts, each one to three short sentences:
say_hook (a punchy hook, about 12 words),
say_question (reads the question slowly),
say_step1, say_step2, say_step3 (the three steps of the shortcut, with the numbers),
say_answer (says the final answer),
say_tip (a one-line memory tip),
say_outro (the practice question for the viewer, then a line asking them to follow for daily TNPSC aptitude tricks).
All the spoken parts together must be 90-115 Tamil words.

Language rules for the spoken parts (they are read by a Tamil text-to-speech voice): write in Tamil script; everyday English words that Tamil speakers normally use (bank, online, mobile, budget, school) are written in Tamil letters; a name, scheme name, abbreviation or technical term with no good Tamil form stays in English letters exactly as in the news (never invent a Tamil translation for it, the program makes the voice say it correctly); write numbers as digits (the program turns them into spoken Tamil words), no brackets, quotes or hyphens; keep
abbreviations (TNPSC, GST, RBI) in English capital letters; use short sentences of at most 12 words, a comma
wherever a speaker would pause, and avoid very long compound words."""
    need = ("title", "description", "tags", "check_expr", "answer", "screen_question", "screen_answer")
    hint = ""
    for attempt in range(6):
        d = llm_json(prompt + avoid + hint)
        parts = [(k[4:], str(d.get(k, "")).strip()) for k in SAY_KEYS]
        words = sum(len(t.split()) for _, t in parts)
        steps = d.get("screen_steps")
        lo = 70 if attempt < 3 else 55
        if not (all(k in d for k in need) and all(t for _, t in parts) and isinstance(steps, list)
                and len(steps) >= 3 and lo <= words <= 150):
            log(f"aptitude (animated) attempt {attempt + 1} invalid (words={words}); retrying")
            hint = (f"\n\nYour previous spoken parts had {words} words in total, or a key was missing. Fill EVERY key and "
                    "write at least 95 Tamil words in the spoken parts.")
            continue
        try:
            got, want = float(safe_eval(d["check_expr"])), float(d["answer"])
        except Exception as e:
            log(f"aptitude (animated) attempt {attempt + 1}: cannot verify maths ({e}); retrying")
            continue
        if abs(got - want) > 1e-6 * max(1.0, abs(want)):
            log(f"aptitude (animated) attempt {attempt + 1}: maths mismatch ({got} vs {want}); retrying")
            continue
        shown = str(d["screen_answer"]).replace(",", "")
        want_txt = str(int(want)) if want == int(want) else str(want)
        if attempt < 4 and want_txt not in shown:
            log(f"aptitude (animated) attempt {attempt + 1}: screen answer does not show {want_txt}; retrying")
            hint = f"\n\nscreen_answer must contain the number {want_txt}."
            continue
        d["parts"] = parts
        d["voiceover"] = " ".join(t for _, t in parts)
        d["screen_steps"] = [str(x) for x in steps[:3]]
        return d
    sys.exit("Could not get a verified animated aptitude script from the LLM.")


# ---------------------------------------------------------------- 3. voice
PRONOUNCE = {   # written form -> how it should be SPOKEN (captions keep the original). Extend in pronounce.json
    "TNPSC": "டிஎன்பிஎஸ்சி", "GST": "ஜிஎஸ்டி", "RBI": "ஆர்பிஐ", "ISRO": "இஸ்ரோ", "UPSC": "யுபிஎஸ்சி",
    "GDP": "ஜிடிபி", "NITI": "நிதி", "AI": "ஏஐ", "UPI": "யுபிஐ", "IPL": "ஐபிஎல்", "BCCI": "பிசிசிஐ",
    "PM": "பிரதமர்", "CM": "முதலமைச்சர்", "MLA": "எம்எல்ஏ", "MP": "எம்பி", "IAS": "ஐஏஎஸ்", "IPS": "ஐபிஎஸ்",
    "NEET": "நீட்", "JEE": "ஜேஇஇ", "UGC": "யுஜிசி", "ICC": "ஐசிசி", "FIFA": "ஃபிஃபா", "WHO": "உலக சுகாதார அமைப்பு",
    "UN": "ஐநா சபை", "UNESCO": "யுனெஸ்கோ", "NASA": "நாசா", "WTO": "டபிள்யூடிஓ", "IMF": "ஐஎம்எஃப்", "SEBI": "செபி",
    "NABARD": "நபார்டு", "EPFO": "இபிஎஃப்ஓ", "ATM": "ஏடிஎம்", "PAN": "பான்", "IIT": "ஐஐடி", "AIIMS": "எய்ம்ஸ்",
    "CBI": "சிபிஐ", "NIA": "என்ஐஏ", "DRDO": "டிஆர்டிஓ", "COVID": "கோவிட்", "FY": "நிதியாண்டு",
    "km": "கிலோமீட்டர்", "kg": "கிலோகிராம்", "cm": "சென்டிமீட்டர்", "MW": "மெகாவாட்", "GW": "ஜிகாவாட்",
    "%": " சதவீதம்", "₹": "ரூபாய் ", "&": " மற்றும் ",
}


def tts_text(text):
    """Cleans the script so the Tamil voice reads it smoothly (no spelled-out symbols, no odd pauses)."""
    import re
    table = dict(PRONOUNCE)
    try:
        table.update(json.loads(Path("pronounce.json").read_text(encoding="utf-8")))
    except Exception:
        pass
    t = text.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    t = tq.digits_to_tamil(t)   # 2026 -> இரண்டாயிரத்து இருபத்து ஆறு (done by code, LLMs get this wrong)
    for k in sorted(table, key=len, reverse=True):
        if re.fullmatch(r"[A-Za-z0-9. ]+", k):   # English abbreviations: whole words only (AI must not change TRAIN)
            t = re.sub(r"(?<![A-Za-z])" + re.escape(k) + r"(?![A-Za-z])", lambda m, v=table[k]: v, t)
        else:
            t = t.replace(k, table[k])
    t = tq.common_english_to_tamil(t)             # bank, online, budget ... in Tamil letters; names stay English
    t = tq.spell_acronyms(t)                      # unknown CAPITAL abbreviations are read letter by letter in Tamil
    t = re.sub(r"[\"'“”‘’()\[\]{}*_#`~|<>]", " ", t)
    t = re.sub(r"\s*[-–—/]\s*", ", ", t)          # hyphens and slashes made the voice stumble
    t = re.sub(r"\s*[;:…]+\s*", ", ", t)          # these confuse the voice; a comma gives a natural pause
    t = re.sub(r"\s*!+", ".", t)
    t = re.sub(r"\.(?=\S)", ". ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if t and t[-1] not in ".?":                    # every text ends with a full stop so the voice lands the last word
        t += "."
    return t


def make_voice_edge(text, path):
    """Free edge-tts voice. Returns timing segments (start_s, dur_s, text)."""
    import edge_tts

    segs = []
    spoken = tts_text(text)
    rate = os.environ.get("TTS_RATE") or "-6%"   # a little slower = clearer Tamil

    async def go():
        voice = os.environ.get("TTS_VOICE") or ("ta-IN-PallaviNeural" if _is_female(_cur_voice()) else "ta-IN-ValluvarNeural")
        try:
            comm = edge_tts.Communicate(spoken, voice, rate=rate, boundary="WordBoundary")
        except TypeError:  # older edge-tts versions
            comm = edge_tts.Communicate(spoken, voice, rate=rate)
        with open(path, "wb") as f:
            async for ch in comm.stream():
                if ch["type"] == "audio":
                    f.write(ch["data"])
                elif ch["type"] in ("WordBoundary", "SentenceBoundary"):
                    segs.append((ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"]))

    asyncio.run(go())
    return segs


# ---- Gemini TTS (Google AI Studio key). Used when GEMINI_API_KEY is set; edge-tts stays as the free fallback ----
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


FEMALE_VOICES = {"kore", "zephyr", "leda", "aoede", "sulafat", "callirrhoe", "autonoe", "despina", "erinome",
                 "laomedeia", "achernar", "gacrux", "pulcherrima", "vindemiatrix"}
_VOICE = {"name": None, "kind": "news"}


def _is_female(name):
    return (name or "").strip().lower() in FEMALE_VOICES


def _cur_voice():
    return _VOICE["name"] or "Charon"


# Gemini voices that suit each kind of video (man and woman mixed). The voice is chosen at random from the matching list,
# so news sounds clear and serious while aptitude lessons sound friendly and upbeat. The free edge-tts fallback follows
# the same man/woman choice. Set the repo variable VOICES (comma separated names) to override the list.
VOICE_POOLS = {
    "news": ["Charon", "Orus", "Rasalgethi", "Sadaltager", "Iapetus", "Kore", "Erinome"],      # informative / firm / clear
    "aptitude": ["Puck", "Achird", "Zubenelgenubi", "Sadachbia", "Laomedeia", "Aoede", "Zephyr", "Leda"],  # friendly / upbeat / lively
}


def pick_voice():
    """One voice per video, chosen at random from the list that suits the content (see VOICE_POOLS).
    The same voice is kept for every part of the video."""
    custom = [v.strip() for v in (os.environ.get("VOICES") or "").split(",") if v.strip()]
    pool = custom or VOICE_POOLS.get(_VOICE.get("kind") or "news") or VOICE_POOLS["news"]
    _VOICE["name"] = random.choice(pool)
    log(f"voice for this {_VOICE.get('kind') or 'news'} video: {_VOICE['name']}")
    return _VOICE["name"]


def tts_engine():
    """Gemini TTS is the DEFAULT voice when the GEMINI_API_KEY secret exists; the free edge-tts (Microsoft Edge neural
    Tamil voices, no key) takes over automatically if Gemini fails or its free limit is used up, and is used for
    every video when there is no key. To force the free voice only, set TTS_ENGINE=edge."""
    e = (os.environ.get("TTS_ENGINE") or "").strip().lower()
    if e == "edge":
        return "edge"
    return "gemini" if (os.environ.get("GEMINI_API_KEY") or "").strip() else "edge"


def _engine_chain(engine):
    """The chosen engine first, then the others that can take over (always ending with free edge-tts)."""
    chain = [engine]
    if "edge" not in chain:
        chain.append("edge")
    return chain


def _audio_to_mp3(raw, path, rate=24000):
    """Gemini sends WAV (with a header) or raw 16-bit mono PCM; ffmpeg turns either one into an mp3."""
    tmp = Path(str(path) + ".raw")
    tmp.write_bytes(raw)
    src = ["-i", str(tmp)] if raw[:4] == b"RIFF" else ["-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", str(tmp)]
    p = subprocess.run(["ffmpeg", "-y"] + src + ["-c:a", "libmp3lame", "-b:a", "96k", str(path)],
                       capture_output=True, text=True)
    tmp.unlink(missing_ok=True)
    if p.returncode:
        raise RuntimeError("ffmpeg could not read the Gemini audio: " + p.stderr[-300:])


def make_voice_gemini(text, path):
    """Voice from Gemini TTS. Raises when it cannot get audio, so the caller can fall back to edge-tts.
    Settings: GEMINI_API_KEY, GEMINI_TTS_MODEL (default gemini-3.8-flash-tts), GEMINI_VOICE (default Kore),
    GEMINI_STYLE (how it should sound)."""
    import base64
    import re
    key = os.environ.get("GEMINI_API_KEY")
    if not key:   # raise (not exit) so the run falls back to the free edge-tts voice instead of stopping
        raise RuntimeError("GEMINI_API_KEY secret is not set in GitHub (Settings > Secrets and variables > Actions)")
    model = os.environ.get("GEMINI_TTS_MODEL") or "gemini-3.8-flash-tts"
    voice = (os.environ.get("GEMINI_VOICE") or "").strip() or _cur_voice()   # Charon (man) or Kore (woman), random per video
    style = os.environ.get("GEMINI_STYLE") or ("friendly, casual and clear, like a young teacher chatting with "
                                                "students, not too fast")
    spoken = tts_text(text)
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}

    # 1) current "interactions" API: the style goes in speech_metadata, the text is read word for word
    body_i = {
        "model": model,
        "input": [{"type": "user_input", "content": [{"type": "text", "text": spoken, "annotations": [
            {"type": "speech_metadata", "style": style}]}]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voice}]},
    }

    def pick_i(js):
        found = [c["data"] for st in js.get("steps", []) for c in (st.get("content") or [])
                 if c.get("type") == "audio" and c.get("data")]
        return (found[-1], "") if found else None

    # 2) older generateContent API (no style control, so the Tamil text itself carries the casual tone)
    body_g = {
        "contents": [{"parts": [{"text": spoken}]}],
        "generationConfig": {"responseModalities": ["AUDIO"],
                             "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}},
    }

    def pick_g(js):
        for cand in js.get("candidates", []):
            for pt in (cand.get("content") or {}).get("parts", []):
                inl = pt.get("inlineData") or pt.get("inline_data") or {}
                if inl.get("data"):
                    return inl["data"], inl.get("mimeType") or inl.get("mime_type") or ""
        return None

    tries = [("interactions", f"{GEMINI_BASE}/interactions", body_i, pick_i),
             ("generateContent", f"{GEMINI_BASE}/models/{model}:generateContent", body_g, pick_g)]
    last = "no answer"
    for name, url, body, pick in tries:
        for n in range(3):
            try:
                r = requests.post(url, headers=headers, json=body, timeout=180)
            except requests.RequestException as e:
                last = f"{name}: {e}"
                time.sleep(5)
                continue
            if r.status_code == 429:
                last = f"{name}: 429 quota/rate limit: {r.text[:200]}"
                if "PerDay" in r.text or "per_day" in r.text:
                    raise RuntimeError(last)   # today's free quota is used up; waiting will not help
                time.sleep(25 * (n + 1))
                continue
            if r.status_code >= 500:
                last = f"{name}: server error {r.status_code}"
                time.sleep(8)
                continue
            if not r.ok:
                last = f"{name}: {r.status_code} {r.text[:250]}"
                break   # wrong request for this API: try the other one
            got = pick(r.json())
            if not got:
                last = f"{name}: the answer had no audio"   # the model sometimes answers without audio: retry
                time.sleep(3)
                continue
            m = re.search(r"rate=(\d+)", got[1] or "")
            _audio_to_mp3(base64.b64decode(got[0]), path, int(m.group(1)) if m else 24000)
            return []
    raise RuntimeError("Gemini TTS failed: " + last)


def speak(text, path, engine):
    """One voice file with exactly the chosen engine (raises on failure)."""
    if engine == "gemini":
        return make_voice_gemini(text, path)
    return make_voice_edge(text, path)


_HEAR = {"off": False}


def hear_score(text, path):
    """Listen-back check: the finished audio is transcribed by Whisper (Groq, same LLM_API_KEY) and compared with the text
    it was supposed to say. Returns 0..1, or None when the check is unavailable. It never raises.
    Switches: VOICE_VERIFY=0 turns it off, WHISPER_MODEL (default whisper-large-v3)."""
    if _HEAR["off"] or (os.environ.get("VOICE_VERIFY") or "1").strip() == "0":
        return None
    key = os.environ.get("LLM_API_KEY")
    base = (os.environ.get("LLM_BASE_URL") or "https://api.groq.com/openai/v1").rstrip("/")
    if not key:
        return None
    try:
        with open(path, "rb") as f:
            r = requests.post(base + "/audio/transcriptions", headers={"Authorization": f"Bearer {key}"},
                              data={"model": os.environ.get("WHISPER_MODEL") or "whisper-large-v3", "language": "ta",
                                    "response_format": "json", "temperature": "0"},
                              files={"file": (Path(path).name, f, "audio/mpeg")}, timeout=120)
        if not r.ok:
            log(f"voice check unavailable ({r.status_code}): {r.text[:160]}")
            _HEAR["off"] = True   # do not waste time on every part when the service says no
            return None
        score = tq.speech_similarity(tts_text(text), r.json().get("text") or "")
        log(f"voice check: heard back {score:.2f} of the text")
        return score
    except Exception as e:
        log(f"voice check skipped: {e}")
        return None


def speak_checked(text, path, engine):
    """speak() plus the listen-back check: if the audio clearly does not match the text (score below VOICE_MIN,
    default 0.45), the same text is spoken once more and the better take is kept. edge-tts is deterministic, so no retry."""
    res = speak(text, path, engine)
    if engine == "edge":
        return res
    score = hear_score(text, path)
    try:
        need = float(os.environ.get("VOICE_MIN") or 0.45)
    except ValueError:
        need = 0.45
    if score is None or score >= need:
        return res
    log(f"voice check: low score {score:.2f} (below {need}); speaking this text once more")
    alt = Path(str(path) + ".b.mp3")
    try:
        speak(text, alt, engine)
        score2 = hear_score(text, alt)
        if score2 is not None and score2 > score:
            alt.replace(path)
            log(f"voice check: the second take is better ({score2:.2f}), kept")
        else:
            alt.unlink(missing_ok=True)
    except Exception as e:
        log(f"second take failed, keeping the first: {e}")
        alt.unlink(missing_ok=True)
    return res


def make_voice(text, path):
    """One voiceover file: the chosen engine, then the next one in the chain (Gemini -> edge-tts)."""
    chain = _engine_chain(tts_engine())
    pick_voice()   # a new random voice for every video
    for i, engine in enumerate(chain):
        try:
            return speak_checked(text, path, engine)
        except Exception as e:
            if i == len(chain) - 1:
                raise
            log(f"{engine} voice failed, trying {chain[i + 1]} instead: {e}")


def make_voice_parts(parts, path, workdir, gap=0.3):
    """Speaks each part separately and joins them, so the screen can change exactly when a part starts.
    Returns {part name: start second}. If an engine fails, ALL parts are redone with the next engine in the chain
    (Gemini -> edge-tts), so one video always has one voice."""
    chain = _engine_chain(tts_engine())
    pick_voice()   # a new random voice for every video
    for i, engine in enumerate(chain):
        try:
            return _voice_parts(parts, path, workdir, gap, engine)
        except Exception as e:
            if i == len(chain) - 1:
                raise
            log(f"{engine} voice failed ({e}); redoing every part with {chain[i + 1]} so the voice stays the same")


def _voice_parts(parts, path, workdir, gap, engine):
    files, starts, t = [], {}, 0.0
    for i, (name, text) in enumerate(parts):
        p = workdir / f"part_{name}.mp3"
        if i and engine == "gemini":
            time.sleep(2)   # be gentle with the per-minute limit
        speak_checked(text, p, engine)
        starts[name] = t
        t += duration(p) + gap
        files.append(p)
    cmd = ["ffmpeg", "-y"]
    for p in files:
        cmd += ["-i", str(p)]
    chain = "".join(f"[{i}:a]apad=pad_dur={gap}[a{i}];" for i in range(len(files)))
    chain += "".join(f"[a{i}]" for i in range(len(files))) + f"concat=n={len(files)}:v=0:a=1[a]"
    cmd += ["-filter_complex", chain, "-map", "[a]", "-c:a", "libmp3lame", "-b:a", "96k", str(path)]
    run(cmd)
    return starts


def speech_spans(path):
    """Finds when the voice is really speaking (between pauses) so captions follow the audio, not a guess."""
    import re
    total = duration(path)
    p = subprocess.run(["ffmpeg", "-i", str(path), "-af", "silencedetect=noise=-32dB:d=0.12", "-f", "null", "-"],
                       capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", p.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", p.stderr)]
    spans, cur = [], 0.0
    for i, st in enumerate(starts):
        st = max(st, 0.0)
        if st - cur > 0.05:
            spans.append((cur, st))
        cur = ends[i] if i < len(ends) else total
    if total - cur > 0.05:
        spans.append((cur, total))
    return spans or [(0.0, total)]


# ---------------------------------------------------------------- 4. images
def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        sys.exit(f"ffmpeg failed: {p.stderr[-800:]}")


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return float(out.strip())


def fallback_image(path, color):
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s={W}x{H}", "-frames:v", "1", str(path)])


_LAST_GOOD = {"path": None}


def fetch_image(prompt, path, seed):
    style = ". Cinematic, soft warm light, vertical composition, no text, no watermark"
    for attempt in range(5):
        # smaller size is faster and more reliable on the free service; ffmpeg scales it up
        url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt + style)
               + f"?width=720&height=1280&nologo=true&seed={seed + attempt}")
        try:
            r = requests.get(url, timeout=120)
            if r.ok and r.headers.get("content-type", "").startswith("image") and len(r.content) > 10_000:
                path.write_bytes(r.content)
                _LAST_GOOD["path"] = path
                return
        except requests.RequestException:
            pass
        time.sleep(10 * (attempt + 1))
    prev = _LAST_GOOD["path"]
    if prev and Path(prev).exists():
        log(f"image failed for '{prompt[:40]}', reusing previous image")
        path.write_bytes(Path(prev).read_bytes())
        return
    log(f"image failed for '{prompt[:40]}', using plain background")
    fallback_image(path, ["0x14213d", "0x1b4332", "0x3d2c5a"][seed % 3])


def fetch_images(scenes, work, stamp, slot):
    """The (up to 5) background pictures, two at a time: faster than one by one, and still gentle with the free service."""
    scenes = list(scenes or FALLBACK_SCENES)[:5]
    paths = [work / f"img{i}.png" for i in range(len(scenes))]
    seeds = [(int(stamp) % 1000) * 10 + slot * 7 + i for i in range(len(scenes))]
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(fetch_image, scenes, paths, seeds))
    return paths


# ---------------------------------------------------------------- 5. video
def make_clip(img, seconds, out, zoom_in):
    frames = int(seconds * 30) + 1
    z = "min(zoom+0.0007,1.25)" if zoom_in else "if(eq(on,1),1.25,max(zoom-0.0007,1.0))"
    vf = (f"crop=iw:ih*0.93:0:0,scale=1620:2880:force_original_aspect_ratio=increase,crop=1620:2880,"
          f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=30,"
          f"eq=brightness=-0.12:saturation=1.05,format=yuv420p")  # slightly darker so text stands out
    run(["ffmpeg", "-y", "-i", str(img), "-vf", vf, "-t", f"{seconds:.2f}", "-r", "30",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", str(out)])


def tamil_chunks(text, max_words=4):
    """Split the voiceover into short on-screen phrases (sentence ends first, then every few words)."""
    import re
    chunks = []
    for sent in re.split(r"(?<=[.!?।—])\s+|\n+", text.strip()):
        words = [w for w in sent.replace("{", "").replace("}", "").replace("\\", "").split() if w]
        for i in range(0, len(words), max_words):
            chunks.append(words[i:i + max_words])
    return [c for c in chunks if c]


def ass_time(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def rrect(w, h, r):
    """ASS vector path of a rounded rectangle."""
    return (f"m {r} 0 l {w - r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h - r} b {w} {h} {w} {h} {w - r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h - r} l 0 {r} b 0 0 0 0 {r} 0")


def timeline(weights, spans, start=0.1):
    """Maps each caption chunk to (t0, t1) on the real speech, skipping the pauses between sentences."""
    spans = [(max(a, start), b) for a, b in spans if b > max(a, start)] or spans
    speech = sum(b - a for a, b in spans)
    total_w = max(sum(weights), 1)
    out, acc = [], 0.0

    def at(x):  # position x seconds into the speech-only timeline -> absolute time
        for a, b in spans:
            if x <= b - a:
                return a + x
            x -= b - a
        return spans[-1][1]

    for w in weights:
        t0, t1 = at(acc / total_w * speech), at((acc + w) / total_w * speech)
        out.append((t0, max(t1, t0 + 0.2)))
        acc += w
    return out


def write_ass(text, speech_seconds, path, start=0.15, date_text="", head2="CURRENT AFFAIRS",
              head3="நடப்பு நிகழ்வுகள்", spans=None, total_seconds=None, cta_y=1000, cta_tamil=True, cap_margin=430,
              captions=True):
    """Header (TNPSC + title + date), running Tamil captions that follow the real speech, and a
    LIKE / SUBSCRIBE call-to-action that pops up near the end."""
    font = os.environ.get("SUB_FONT") or "Noto Sans Tamil"
    latin = os.environ.get("SUB_LATIN_FONT") or "DejaVu Sans"
    chunks = tamil_chunks(text)
    weights = [sum(len(w) for w in c) for c in chunks]
    spans = spans or [(start, speech_seconds)]
    times = timeline(weights, spans, start)
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,"
        "Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,"
        "MarginV,Encoding\n"
        f"Style: Run,{font},78,&H0000D7FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,5,2,2,70,70,{cap_margin},1\n"
        f"Style: Head,{latin},60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,3,1,8,40,40,100,1\n"
        f"Style: Btn,{latin},58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n"
        f"Style: BtnTa,{font},50,&H0000D7FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,4,1,5,0,0,0,1\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,MarginL,MarginR,MarginV,Effect,Text\n"
    )
    total = total_seconds or (speech_seconds + 1.2)
    gold = r"\c&H3CC8FF&"
    white = r"\c&HFFFFFF&"
    title = (rf"{{\fs125{gold}}}TNPSC\N{{\fs62{white}}}{head2}\N"
             rf"{{\fn{font}\fs54{white}}}{head3}\N"
             rf"{{\fn{latin}\fs50{gold}}}{date_text}")
    lines = [f"Dialogue: 0,{ass_time(0)},{ass_time(total)},Head,0,0,0,,{title}"]
    for c, wt, (t0, t1) in (zip(chunks, weights, times) if captions else []):   # captions=False: no running subtitles
        dur = t1 - t0
        ks, used = [], 0
        for w in c:
            k = int(round(dur * 100 * len(w) / max(wt, 1)))
            ks.append(k)
            used += k
        ks[-1] += int(round(dur * 100)) - used
        body = "".join(f"{{\\kf{max(k, 1)}}}{w} " for k, w in zip(ks, c)).strip()
        lines.append(f"Dialogue: 0,{ass_time(t0)},{ass_time(t1 + 0.05)},Run,0,0,0,,{{\\fad(100,60)}}{body}")

    # LIKE / SUBSCRIBE call-to-action for the last 6.5 seconds
    c0, c1 = max(total - 6.5, 1.0), total
    pop = r"\fscx55\fscy55\t(0,350,\fscx100\fscy100)"
    pulse = r"\t(2200,2600,\fscx108\fscy108)\t(2600,3000,\fscx100\fscy100)\t(3600,4000,\fscx108\fscy108)\t(4000,4400,\fscx100\fscy100)"
    y = cta_y
    for cx, w, col, label, extra in ((300, 330, r"\1c&HE5881E&", "LIKE", ""), (720, 470, r"\1c&H0000FF&", "SUBSCRIBE", pulse)):
        lines.append(f"Dialogue: 1,{ass_time(c0)},{ass_time(c1)},Btn,0,0,0,,"
                     f"{{\\an5\\pos({cx},{y})\\bord0\\shad0{col}\\fad(200,200){pop}{extra}\\p1}}{rrect(w, 120, 28)}{{\\p0}}")
        lines.append(f"Dialogue: 2,{ass_time(c0)},{ass_time(c1)},Btn,0,0,0,,"
                     f"{{\\an5\\pos({cx},{y})\\fad(200,200){pop}{extra}}}{label}")
    if cta_tamil:
        lines.append(f"Dialogue: 2,{ass_time(c0 + 0.3)},{ass_time(c1)},BtnTa,0,0,0,,"
                     f"{{\\an5\\pos(540,{y + 115})\\fad(250,200)}}லைக் செய்யுங்கள் • சப்ஸ்கிரைப் செய்யுங்கள்")
    Path(path).write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def make_logo(src, dst, size=170):
    """Turns assets/logo.png (your channel icon) into a round watermark."""
    from PIL import Image, ImageDraw
    im = Image.open(src).convert("RGBA")
    side = min(im.size)
    im = im.crop(((im.width - side) // 2, (im.height - side) // 2,
                  (im.width + side) // 2, (im.height + side) // 2)).resize((size, size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    im.putalpha(mask)
    im.save(dst)


LOGO = Path("assets/logo.png")


def render_manim(s, starts, total, workdir, today):
    """Renders the animated question / steps / answer scene (manim_aptitude.py) and returns the mp4 path."""
    data = {
        "topic": s.get("topic_ta", ""),
        "question": s["screen_question"],
        "steps": s["screen_steps"],
        "answer": s["screen_answer"],
        "practice": s.get("screen_practice", ""),
        "cues": {
            "question": max(starts["question"] - 0.1, 0.0),
            "steps": [max(starts[f"step{i}"] - 0.1, 0.0) for i in (1, 2, 3)],
            "answer": max(starts["answer"] - 0.1, 0.0),
            "practice": max(starts["outro"] - 0.1, 0.0),
        },
    }
    jpath = (workdir / "apt.json").resolve()
    jpath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    media = (workdir / "manim_media").resolve()
    e = dict(os.environ, APT_JSON=str(jpath), APT_DURATION=f"{total:.2f}", APT_DATE=today, APT_HEADER="0")
    scene_file = str(Path(__file__).with_name("manim_aptitude.py"))
    cmd = [sys.executable, "-m", "manim", "-qm", "--fps", "30", "--media_dir", str(media), "-o", "apt.mp4",
           scene_file, "AptitudeShort"]
    p = subprocess.run(cmd, env=e, capture_output=True, text=True, timeout=900)
    found = sorted(media.rglob("apt.mp4"))
    if p.returncode or not found:
        raise RuntimeError("manim failed: " + (p.stderr or p.stdout)[-800:])
    return found[0]


# Voice clean-up for clearer speech: cut low rumble, even out loud and soft words, same loudness for every voice
VOICE_CLEAN = ("highpass=f=70,acompressor=threshold=0.1:ratio=3:attack=5:release=80:makeup=2,"
               "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=44100")


def build_video(images, voice, out, workdir, bgm=BGM, subs=None, base_video=None):
    total = duration(voice) + 1.0
    if base_video:
        joined = Path(base_video)   # a ready-made picture track (the Manim animation)
    else:
        per = total / len(images)
        clips = []
        for i, img in enumerate(images):
            c = workdir / f"clip{i}.mp4"
            make_clip(img, per + 0.1, c, zoom_in=(i % 2 == 0))
            clips.append(c)
        lst = workdir / "list.txt"
        lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
        joined = workdir / "joined.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])

    cmd = ["ffmpeg", "-y", "-i", str(joined), "-i", str(voice)]
    n = 2
    if Path(bgm).exists():
        cmd += ["-stream_loop", "-1", "-i", str(bgm)]
        n += 1
        afilter = (f"[1:a]{VOICE_CLEAN},apad=pad_dur=1[va];[2:a]volume=0.10,afade=t=in:d=1.5[b];"
                   f"[va][b]amix=inputs=2:duration=first:dropout_transition=0[m];"
                   f"[m]volume=1.8,afade=t=out:st={total - 1.5:.2f}:d=1.5[a]")
    else:
        log("WARNING: assets/bgm.mp3 not found, publishing without BGM")
        afilter = f"[1:a]{VOICE_CLEAN},apad=pad_dur=1[a]"
    base = "null"
    if subs:
        # dark panel behind the title block, then title, running Tamil text and LIKE/SUBSCRIBE from the .ass file
        base = f"drawbox=x=0:y=70:w=iw:h=370:color=black@0.55:t=fill,ass={Path(subs).resolve()}"
    if LOGO.exists():
        logo = workdir / "logo_round.png"
        make_logo(LOGO, logo)
        cmd += ["-loop", "1", "-framerate", "30", "-i", str(logo)]
        vfilter = (f"[0:v]{base}[bv];[{n}:v]format=rgba,colorchannelmixer=aa=0.92[lg];"
                   f"[bv][lg]overlay=40:95:shortest=1[v]")
    else:
        log("no assets/logo.png: publishing without the channel watermark")
        vfilter = f"[0:v]{base}[v]"
    cmd += ["-filter_complex", vfilter + ";" + afilter, "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    run(cmd)
    return total


# ---------------------------------------------------------------- 6. YouTube upload
def upload(video, title, description, tags):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials(
        None,
        refresh_token=env("YT_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=env("YT_CLIENT_ID"),
        client_secret=env("YT_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    yt = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {"title": title[:100], "description": description[:4800], "tags": tags[:15],
                    "categoryId": "27", "defaultLanguage": "ta"},
        "status": {"privacyStatus": env("YT_PRIVACY", "private"), "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": True},
    }
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    log(f"uploaded: https://youtube.com/watch?v={resp['id']} (privacy: {body['status']['privacyStatus']})")


# ---------------------------------------------------------------- main
def make_one(slot, today, stamp, upload_it, hist):
    kind, name, queries, focus = SLOTS[slot]
    tag = f"{stamp}-s{slot}"
    work = OUT / f"work-{tag}"
    work.mkdir(parents=True, exist_ok=True)
    hosts, urls = [], []   # urls only gets filled by news slots; aptitude slots have none
    manim_mode = False
    cards_mode = False

    if kind == "news":
        log(f"[slot {slot}] {name}: searching news")
        notes, hosts, urls = search_news(queries, hist.get("urls", []))
        (OUT / f"notes-{tag}.txt").write_text(notes, encoding="utf-8")
        # step 1 of the Tamil quality layer: any-language news -> clean English facts, THEN write Tamil from them
        log(f"[slot {slot}] cleaning the news into English facts")
        notes = tq.normalize_notes(notes, llm_json, log)
        (OUT / f"facts-{tag}.txt").write_text(notes, encoding="utf-8")
        log(f"[slot {slot}] writing Tamil script")
        # news slots use the HTML news-card video (set repo variable CARDS_SLOTS=none to switch it off, default 1,2,4)
        card_slots = [x.strip() for x in (os.environ.get("CARDS_SLOTS") or "1,2,4").split(",")]
        s = None
        if str(slot) in card_slots:
            try:
                s = write_news_cards_script(notes, today, focus, slot, 5, avoid_text(hist))
                cards_mode = True
            except (Exception, SystemExit) as e:
                log(f"[slot {slot}] news-card script failed, using the normal script: {e}")
        if s is None:
            s = write_script(notes, today, focus, slot, 5, avoid_text(hist))
        head2, head3, hashtags = "CURRENT AFFAIRS", "நடப்பு நிகழ்வுகள்", "#TNPSC #CurrentAffairs #Shorts"
        pre, post = "Sources: " + ", ".join(hosts), "AI-assisted video. Verify facts with official sources."
    else:
        doy = dt.datetime.now(IST).timetuple().tm_yday
        topic = APTITUDE_TOPICS[(doy * 2 + (0 if slot == 3 else 1)) % len(APTITUDE_TOPICS)]
        log(f"[slot {slot}] aptitude topic: {topic}")
        # which aptitude slots use the animated Manim video (default: slot 5 only; set repo variable MANIM_SLOTS=3,5 for both)
        manim_slots = [x.strip() for x in (os.environ.get("MANIM_SLOTS") or "5").split(",")]
        manim_mode = str(slot) in manim_slots
        avoid_apt = avoid_text(hist, 12) + apt_brief(topic)
        if manim_mode:
            s = write_aptitude_manim_script(topic, today, avoid_apt)
        else:
            s = write_aptitude_script(topic, today, avoid_apt)
        head2, head3, hashtags = "APTITUDE TRICKS", "கணிதம் - குறுக்கு வழி", "#TNPSC #Aptitude #MathsTricks #Shorts"
        pre, post = "Topic: " + topic, "AI-assisted video. Practise the method on your own."
    # step 3 of the Tamil quality layer: remove foreign letters, review the Tamil against the English facts, hard check
    (OUT / f"script-{tag}-draft.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    tq_kind = ("cards" if cards_mode else "script") if kind == "news" else ("manim" if manim_mode else "apt")
    log(f"[slot {slot}] checking the Tamil")
    s = tq.finalize(s, tq_kind, notes if kind == "news" else "", llm_json, log)
    log(f"[slot {slot}] preparing the text for the voice")
    s = tq.voice_prep(s, tq_kind, llm_json, log)   # AI rewrite for pronunciation; captions keep the original text
    (OUT / f"script-{tag}.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")

    voice = work / "voice.mp3"
    starts = None
    _VOICE["kind"] = "news" if kind == "news" else "aptitude"   # the voice is picked to suit the content
    if manim_mode or cards_mode:
        starts = make_voice_parts(s.get("voice_parts") or s["parts"], voice, work)   # each part spoken separately -> exact timing
    else:
        make_voice(s.get("voice_text") or s["voiceover"], voice)
    vdur = duration(voice)

    base = None
    if manim_mode:
        try:
            log(f"[slot {slot}] rendering the Manim animation")
            base = render_manim(s, starts, vdur + 1.0, work, today)
        except Exception as e:
            log(f"[slot {slot}] Manim failed, using AI images instead: {e}")

    imgs = []
    if cards_mode:
        try:
            log(f"[slot {slot}] fetching background pictures and drawing the news cards")
            imgs = fetch_images(s.get("scenes"), work, stamp, slot)
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import cards_news
            base = cards_news.render_cards_video(s, starts, vdur + 1.0, work, today, imgs)
        except Exception as e:
            log(f"[slot {slot}] news cards failed, using the normal picture video instead: {e}")
            base = None
    if base is None and not imgs:
        imgs = fetch_images(s.get("scenes"), work, stamp, slot)

    final = OUT / f"tnpsc-{tag}.mp4"
    subs = work / "captions.ass"
    # with the animation, the LIKE / SUBSCRIBE buttons go below the captions so they do not cover the answer
    write_ass(s["voiceover"], vdur, subs, date_text=today, head2=head2, head3=head3,
              spans=speech_spans(voice), total_seconds=vdur + 1.0,
              cta_y=1570 if base else 1000, cta_tamil=base is None, cap_margin=390 if base else 430,
              captions=base is None)   # cards / animation already show the text: no running subtitles
    secs = build_video(imgs, voice, final, work, subs=subs, base_video=base)
    log(f"[slot {slot}] video ready ({secs:.0f}s): {final}")

    if upload_it:
        desc = s["description"] + f"\n\n{pre}\n{post}\n{hashtags}"
        upload(final, f"{s['title']} #Shorts", desc, [str(t) for t in s["tags"]])
    else:
        log("UPLOAD=false, skipping YouTube upload")

    if upload_it:
        hist.setdefault("done", {}).setdefault(stamp, []).append(slot)
    hist.setdefault("urls", []).extend(urls)
    hist.setdefault("titles", []).append(f"{name}: {s['title']}")
    save_history(hist)


def pick_slots():
    v = (os.environ.get("SLOT") or "").strip().lower()
    if v == "all":
        return list(SLOTS)
    if v.isdigit() and int(v) in SLOTS:
        return [int(v)]
    # no slot given: choose by the IST clock (8, 10:30, 13, 15:30, 18)
    h = dt.datetime.now(IST).hour + dt.datetime.now(IST).minute / 60
    starts = {1: 8.0, 2: 10.5, 3: 13.0, 4: 15.5, 5: 18.0}
    return [min(starts, key=lambda k: abs(starts[k] - h))]


def main():
    OUT.mkdir(exist_ok=True)
    now = dt.datetime.now(IST)
    today, stamp = now.strftime("%d %B %Y"), now.strftime("%Y%m%d")
    upload_it = env("UPLOAD", "true").lower() == "true"
    slots = pick_slots()
    hist = load_history()
    log(f"slots to build: {slots}")

    done, failed = 0, []
    for slot in slots:
        try:
            make_one(slot, today, stamp, upload_it, hist)
            done += 1
            time.sleep(20)  # ease free-tier rate limits
        except BaseException as e:  # with SLOT=all, one bad video does not cancel the rest
            if isinstance(e, KeyboardInterrupt):
                raise
            failed.append(slot)
            log(f"slot {slot} FAILED: {e!r}")
            if upload_it:
                k = f"{stamp}-{slot}"
                hist.setdefault("tries", {})[k] = hist.get("tries", {}).get(k, 0) + 1
                save_history(hist)
    log(f"finished: {done}/{len(slots)} videos; failed: {failed or 'none'}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
