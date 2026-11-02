"""Tamil quality layer for the TNPSC Shorts pipeline.

Why this file exists
--------------------
The news arrives in English (sometimes Hindi / Tamil / other languages). Before this file, ONE LLM call had to
understand that news, translate it, write casual Tamil, count words and fill a big JSON, all at once. That is
where wrong names, wrong numbers, bookish Tamil and stray foreign letters came from.

Now the work is split into steps, and every step is checked by plain code, not only by the LLM:

  1. normalize_notes()   any-language news  ->  clean English facts (translate FIRST, then write)
  2. translation_rules() rules + a glossary of exact Tamil spellings (districts, states, institutions ...)
                         that are added to the script prompts
  3. finalize()          after the script is written:
                           - sanitize: remove foreign-script letters / repeated-word loops
                           - review: a second LLM pass (temperature 0.2, may use another model) compares the
                             Tamil with the English facts and fixes mistranslations, grammar and stiff words.
                             A fix is accepted ONLY if numbers are unchanged, length fits the screen,
                             and no foreign letters appear; otherwise the original text is kept
                           - final hard check: stops instead of publishing garbage
  4. digits_to_tamil()   numbers like 2026, 5.5, 1,50,000, rupee amounts -> correct spoken Tamil words, by code
                         (LLMs often get Tamil number words wrong)

Run `python tamil_quality.py` to run the built-in self test (no internet needed).
"""
import json
import os
import re
from collections import Counter

# ----------------------------------------------------------------------------- glossary
# (English spellings that may appear in the news, exact Tamil spelling to use)
GLOSSARY = [
    (["Tamil Nadu"], "தமிழ்நாடு"), (["Chennai"], "சென்னை"), (["Coimbatore"], "கோயம்புத்தூர்"),
    (["Madurai"], "மதுரை"), (["Tiruchirappalli", "Trichy", "Tiruchi"], "திருச்சிராப்பள்ளி"),
    (["Salem"], "சேலம்"), (["Tirunelveli"], "திருநெல்வேலி"), (["Tiruppur", "Tirupur"], "திருப்பூர்"),
    (["Erode"], "ஈரோடு"), (["Vellore"], "வேலூர்"), (["Thoothukudi", "Tuticorin"], "தூத்துக்குடி"),
    (["Thanjavur", "Tanjore"], "தஞ்சாவூர்"), (["Dindigul"], "திண்டுக்கல்"), (["Cuddalore"], "கடலூர்"),
    (["Kancheepuram", "Kanchipuram"], "காஞ்சிபுரம்"), (["Chengalpattu"], "செங்கல்பட்டு"),
    (["Tiruvallur", "Thiruvallur"], "திருவள்ளூர்"), (["Tiruvannamalai"], "திருவண்ணாமலை"),
    (["Villupuram"], "விழுப்புரம்"), (["Kallakurichi"], "கள்ளக்குறிச்சி"), (["Ariyalur"], "அரியலூர்"),
    (["Perambalur"], "பெரம்பலூர்"), (["Karur"], "கரூர்"), (["Namakkal"], "நாமக்கல்"),
    (["Dharmapuri"], "தருமபுரி"), (["Krishnagiri"], "கிருஷ்ணகிரி"), (["Nilgiris"], "நீலகிரி"),
    (["Theni"], "தேனி"), (["Virudhunagar"], "விருதுநகர்"), (["Sivagangai", "Sivaganga"], "சிவகங்கை"),
    (["Ramanathapuram"], "ராமநாதபுரம்"), (["Pudukkottai"], "புதுக்கோட்டை"), (["Tenkasi"], "தென்காசி"),
    (["Kanyakumari"], "கன்னியாகுமரி"), (["Nagapattinam"], "நாகப்பட்டினம்"), (["Tiruvarur"], "திருவாரூர்"),
    (["Mayiladuthurai"], "மயிலாடுதுறை"), (["Ranipet"], "ராணிப்பேட்டை"), (["Tirupathur", "Tirupattur"], "திருப்பத்தூர்"),
    (["Puducherry", "Pondicherry"], "புதுச்சேரி"),
    (["India"], "இந்தியா"), (["Delhi", "New Delhi"], "டெல்லி"), (["Mumbai"], "மும்பை"), (["Kolkata"], "கொல்கத்தா"),
    (["Bengaluru", "Bangalore"], "பெங்களூரு"), (["Hyderabad"], "ஹைதராபாத்"), (["Kerala"], "கேரளா"),
    (["Karnataka"], "கர்நாடகா"), (["Andhra Pradesh"], "ஆந்திரப் பிரதேசம்"), (["Telangana"], "தெலங்கானா"),
    (["Maharashtra"], "மகாராஷ்டிரா"), (["Gujarat"], "குஜராத்"), (["Uttar Pradesh"], "உத்தரப் பிரதேசம்"),
    (["Rajasthan"], "ராஜஸ்தான்"), (["West Bengal"], "மேற்கு வங்காளம்"), (["Bihar"], "பீகார்"),
    (["Odisha"], "ஒடிசா"), (["Assam"], "அசாம்"), (["Punjab"], "பஞ்சாப்"), (["Haryana"], "ஹரியானா"),
    (["Madhya Pradesh"], "மத்தியப் பிரதேசம்"), (["Jammu and Kashmir", "Jammu & Kashmir"], "ஜம்மு காஷ்மீர்"),
    (["Ladakh"], "லடாக்"), (["Sri Lanka"], "இலங்கை"), (["China"], "சீனா"), (["Japan"], "ஜப்பான்"),
    (["Russia"], "ரஷ்யா"), (["United States", "USA", "U.S."], "அமெரிக்கா"), (["Pakistan"], "பாகிஸ்தான்"),
    (["Bangladesh"], "வங்காளதேசம்"), (["Nepal"], "நேபாளம்"), (["Bhutan"], "பூடான்"),
    (["Maldives"], "மாலத்தீவு"), (["Australia"], "ஆஸ்திரேலியா"), (["Germany"], "ஜெர்மனி"),
    (["France"], "பிரான்ஸ்"), (["Singapore"], "சிங்கப்பூர்"), (["United Kingdom", "Britain"], "பிரிட்டன்"),
    (["Supreme Court"], "உச்ச நீதிமன்றம்"), (["High Court"], "உயர் நீதிமன்றம்"), (["Lok Sabha"], "மக்களவை"),
    (["Rajya Sabha"], "மாநிலங்களவை"), (["Parliament"], "நாடாளுமன்றம்"), (["Assembly"], "சட்டமன்றம்"),
    (["Reserve Bank of India", "RBI"], "ரிசர்வ் வங்கி"), (["Chief Minister"], "முதலமைச்சர்"),
    (["Prime Minister"], "பிரதமர்"), (["President"], "குடியரசுத் தலைவர்"), (["Governor"], "ஆளுநர்"),
    (["Finance Minister"], "நிதி அமைச்சர்"), (["Union Budget"], "மத்திய பட்ஜெட்"),
    (["Election Commission"], "தேர்தல் ஆணையம்"), (["ISRO"], "இஸ்ரோ"), (["DRDO"], "டிஆர்டிஓ"),
    (["NITI Aayog"], "நிதி ஆயோக்"), (["TNPSC"], "டிஎன்பிஎஸ்சி"), (["UPSC"], "யுபிஎஸ்சி"),
    (["GDP"], "ஜிடிபி"), (["GST"], "ஜிஎஸ்டி"), (["UPI"], "யுபிஐ"), (["repo rate"], "ரெப்போ வட்டி விகிதம்"),
    (["inflation"], "பணவீக்கம்"), (["scheme"], "திட்டம்"), (["MoU"], "புரிந்துணர்வு ஒப்பந்தம்"),
    (["Gazette"], "அரசிதழ்"), (["Cabinet"], "அமைச்சரவை"), (["Bill"], "மசோதா"),
    (["Tamil Nadu Public Service Commission"], "தமிழ்நாடு அரசுப் பணியாளர் தேர்வாணையம்"),
]

RULES = """Translation rules (VERY IMPORTANT, the facts come from news in different languages):
0. A fact that is ALREADY in clear Tamil must NOT be translated again: reuse its Tamil wording, names and spellings, and only shorten it and make it sound like relaxed spoken Tamil. Only facts in English (or another language) are translated into Tamil.
1. First understand each English fact, then say it in natural spoken Tamil. Never translate word for word.
2. Keep every name, number, date, amount and place EXACTLY as in the notes. Never guess or change them. If a detail is unclear in the notes, leave that fact out.
3. Write person names, scheme names and organisation names the way they SOUND, in Tamil letters, as Tamil newspapers do. Do not invent a new Tamil meaning for an English scheme name.
4. Every sentence must be complete and grammatical Tamil (subject, object and verb agree). Re-read it once before answering.
5. Write Tamil in Tamil script. English words: an everyday English word that Tamil speakers normally use (bank, online, mobile, budget, school) is written in Tamil letters. A name, scheme name, abbreviation (TNPSC, GST, DMK) or technical term with no good Tamil form stays in ENGLISH letters exactly as in the notes. Never invent a Tamil translation for those. Never write Chinese, Hindi, Telugu, Malayalam, Arabic, Russian or any other script.
6. Write numbers, years, amounts and percentages as DIGITS (for example 2026, 5.5, 500 கோடி, 12%). The program converts them into spoken Tamil words, so do NOT spell numbers in Tamil words.
7. Style: everyday SPOKEN Tamil (பேச்சுத் தமிழ்) like a friendly teacher talking to students. NOT literary, formal or poetic Tamil: no bookish or புலமை words, no long Sanskritised compounds. Short, simple sentences."""


APT_RULES = ("Tamil rules: complete, grammatical, natural spoken Tamil sentences (re-read each one once). The numbers in the "
             "spoken parts and in the screen texts must be exactly the same. Write Tamil in Tamil script; everyday English words in Tamil letters; "
             "an abbreviation or term with no good Tamil form stays in English letters. Never use Chinese, Hindi, Telugu, Arabic, Russian or other scripts. Write numbers as DIGITS (the program turns them into "
             "spoken Tamil words).")

def translation_rules(notes=""):
    """The rules above, plus the exact Tamil spelling of every glossary term that appears in the notes."""
    hits = []
    low = notes or ""
    for variants, ta in GLOSSARY:
        for v in variants:
            if re.search(r"(?<![A-Za-z])" + re.escape(v) + r"(?![A-Za-z])", low, re.I):
                hits.append(f"{variants[0]} = {ta}")
                break
    out = RULES
    if hits:
        out += "\n8. Use exactly these Tamil spellings when the term appears:\n" + "\n".join(hits[:45])
    return out


# ----------------------------------------------------------------------------- step 1: facts in English
def normalize_notes(notes, llm, log=print):
    """Raw search notes (any language, maybe cut off) -> a clean list of English facts. Falls back to the
    original notes if anything goes wrong, so the pipeline never stops because of this step."""
    prompt = f"""You are a news desk editor. Below are raw search notes for a TNPSC current-affairs channel. Some may be in Tamil, Hindi or another language, some are cut off in the middle.
Turn them into a clean list of distinct facts.
Rules: use only what the notes say. Keep every name, number, date, amount and place exactly. A note that is ALREADY in clear Tamil stays in Tamil: write its fact in the same Tamil, do NOT translate it into English. A note in English is written as one plain English sentence. A note in Hindi or any other language is translated into plain English. Merge duplicates. Drop opinions, gossip, and any item where it is not clear who did what. If a note is cut off so the fact is unclear, skip it. Mention the date or place only if the notes say it. At most 14 facts.
Return JSON: {{"facts": [{{"fact": "one clear sentence (Tamil if the note was Tamil, otherwise English)", "source": "website name"}}]}}

NOTES:
{notes}"""
    try:
        d = llm(prompt, model=_model(), temperature=0.2)
        facts = [f for f in d.get("facts", []) if isinstance(f, dict) and str(f.get("fact", "")).strip()]
        if len(facts) < 3:
            log("fact clean-up gave too few facts; using the raw notes")
            return notes
        lines = []
        for f in facts[:14]:
            src = str(f.get("source", "")).strip()
            lines.append(f"- {str(f['fact']).strip()}" + (f" ({src})" if src else ""))
        log(f"news clean-up: {len(facts)} facts")
        return "\n".join(lines)
    except (Exception, SystemExit) as e:
        log(f"news clean-up skipped: {e}")
        return notes


def _model():
    """Optional separate model for translation / review: set the repo variable LLM_MODEL_TA."""
    return (os.environ.get("LLM_MODEL_TA") or "").strip() or None


# ----------------------------------------------------------------------------- plain-code Tamil checks
_FOREIGN = re.compile(
    "[ऀ-ॿঀ-৿਀-੿઀-૿଀-୿ఀ-౿ಀ-೿ഀ-ൿ"
    "඀-෿฀-๿֐-׿؀-ۿЀ-ӿ぀-ヿ一-鿿가-힯]")
_TAMIL_LETTER = re.compile("[அ-ஹ]")
_LATIN_WORD = re.compile(r"[A-Za-z]{2,}")
STIFF = ("கணக்கிடுக", "விடையைக் காண்க", "பின்வருமாறு")


def sanitize(text):
    """Remove foreign-script letters and runaway repeated words (LLM glitches). Returns clean text."""
    t = _FOREIGN.sub("", str(text))
    t = t.replace("​", "").replace("﻿", "")
    words, out, run = t.split(), [], 0
    for w in words:
        if out and w == out[-1]:
            run += 1
            if run >= 2:      # the same word 3+ times in a row is a model loop
                continue
        else:
            run = 0
        out.append(w)
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def tamil_ratio(text):
    tam = len(_TAMIL_LETTER.findall(text))
    lat = sum(len(w) for w in _LATIN_WORD.findall(text))
    return tam / (tam + lat) if (tam + lat) else 0.0


def _nums(text):
    return Counter(re.findall(r"\d+(?:[.,]\d+)*", text))


# ----------------------------------------------------------------------------- script fields (per video kind)
def _fields(s, kind):
    """The Tamil fields of a script. kind: cards | script | apt | manim.
    Returns {key: {"text", "cap" (max length that fits the screen), "spoken", "set" (function)}}"""
    F = {}

    def add(key, text, cap, spoken, setter):
        if isinstance(text, str) and text.strip():
            F[key] = {"text": text, "cap": cap, "spoken": spoken, "set": setter}

    def top(k, cap, spoken=False):
        add(k, s.get(k), cap, spoken, lambda v, k=k: s.__setitem__(k, v))

    top("title", 85)
    top("description", 4000)
    if kind in ("script", "apt"):
        top("voiceover", 1500, True)
    if kind == "cards":
        top("headline", 80)
        top("remember", 90)
        top("quiz", 90)
        for i, c in enumerate(s.get("cards") or []):
            add(f"card{i + 1}_title", c.get("title"), 60, False, lambda v, c=c: c.__setitem__("title", v))
            add(f"card{i + 1}_detail", c.get("detail"), 150, False, lambda v, c=c: c.__setitem__("detail", v))
    if kind == "manim":
        top("topic_ta", 40)
        top("screen_question", 60)
        top("screen_answer", 14)
        top("screen_practice", 60)
        steps = s.get("screen_steps") or []
        for i, t in enumerate(steps):
            add(f"screen_step{i + 1}", t, 26, False, lambda v, i=i, steps=steps: steps.__setitem__(i, v))
    if kind in ("cards", "manim"):
        parts = s.get("parts") or []
        for i, (name, t) in enumerate(parts):
            add(f"say_{name}", t, 700, True,
                lambda v, i=i, name=name, parts=parts: parts.__setitem__(i, (name, v)))
    return F


def _sync_voiceover(s, kind):
    if kind in ("cards", "manim") and s.get("parts"):
        s["voiceover"] = " ".join(t for _, t in s["parts"])


def sanitize_script(s, kind):
    for key, f in _fields(s, kind).items():
        clean = sanitize(f["text"])
        if clean != f["text"]:
            f["set"](clean)
    _sync_voiceover(s, kind)


def hard_problems(s, kind):
    """Problems that must stop the video (the text would sound or look wrong)."""
    bad = []
    for key, f in _fields(s, kind).items():
        t = f["text"]
        if _FOREIGN.search(t):
            bad.append(f"{key}: foreign letters")
        if f["spoken"] and tamil_ratio(t) < 0.5:
            bad.append(f"{key}: not Tamil enough")
    return bad


def soft_notes(s, kind):
    """Things worth a log line but not worth stopping for."""
    notes = []
    for key, f in _fields(s, kind).items():
        for w in STIFF:
            if w in f["text"]:
                notes.append(f"{key}: bookish word {w}")
        kept = _LATIN_WORD.findall(f["text"])
        if kept:
            notes.append(f"{key}: English kept as is: {', '.join(kept[:6])}")
    return notes


# ----------------------------------------------------------------------------- step 3: review with a second LLM pass
def review_script(s, kind, notes, llm, log=print, only=None, extra=""):
    """Second LLM pass: compare the Tamil with the English facts and fix mistakes. Accepts a fix only when it is safe."""
    F = _fields(s, kind)
    if only:
        F = {k: v for k, v in F.items() if k in only}
    if not F:
        return
    if kind in ("apt", "manim"):
        context = ("This is a maths shortcut lesson, there are no news facts. The numbers and the maths in the Tamil "
                   f"must stay EXACTLY the same (final answer: {s.get('answer')}). Only fix the Tamil language.")
    else:
        context = "ENGLISH FACTS (the only source of truth):\n" + notes
    payload = {k: f["text"] for k, f in F.items()}
    prompt = f"""You are a strict Tamil language editor for a TNPSC exam-preparation channel. A writer produced the Tamil texts below from English facts. Check each text and fix it.

{context}

Fix these problems:
- wrong, mistranslated or unnatural Tamil; wrong or missing grammar endings; sentences that do not make sense
- any name, place, number, date or amount that differs from the English facts (the English facts win)
- a fact that is NOT in the English facts: rewrite that sentence using only facts that are given
- bookish / literary Tamil in the spoken parts (say_* and voiceover): make it simple, friendly spoken Tamil (பேச்சுத் தமிழ்) like a teacher chatting with students
- letters of other scripts (Chinese, Hindi, Telugu ...): not allowed
- English words: an everyday English word that Tamil speakers normally use (online, bank, mobile, budget) must be in Tamil letters (ஆன்லைன், பேங்க்). If a name, scheme name, abbreviation or technical term has no good established Tamil form, KEEP the English exactly as in the English facts; never invent a Tamil translation for it, and put back the English if the writer translated it wrongly
- words that a voice would read badly: very long compound words, rare literary words (use a common everyday word instead)

Maximum length of each text in characters (the screen is that small): {json.dumps({k: f["cap"] for k, f in F.items()})}
{extra}
Rules: keep every number and digit exactly as it is. Keep each text about the same length (never longer than the original by more than 15%). Do not merge, split, add or remove keys. If a text is already correct, return it unchanged.
Return JSON: {{"fields": {{"<same key>": "<corrected Tamil text>", ...}}, "problems": ["short English note for each real problem you fixed"]}}

TEXTS TO CHECK:
{json.dumps(payload, ensure_ascii=False, indent=1)}"""
    d = llm(prompt, model=_model(), temperature=0.2, effort="medium")
    fixed = d.get("fields") or {}
    if not isinstance(fixed, dict):
        return
    changed, rejected = 0, []
    for key, f in F.items():
        new = fixed.get(key)
        if not isinstance(new, str):
            continue
        new = sanitize(new)
        old = f["text"]
        if not new or new == old:
            continue
        if f["cap"] and len(new) > f["cap"]:
            rejected.append(f"{key} (too long for the screen)")
            continue
        english_before = tamil_ratio(old) < 0.5     # an English text turned into Tamil may be a different length
        if not english_before and (len(new) > len(old) * 1.25 + 8 or len(new) < len(old) * 0.5):
            rejected.append(f"{key} (length changed too much)")
            continue
        if _nums(old) and _nums(new) != _nums(old):
            rejected.append(f"{key} (numbers changed)")
            continue
        if tamil_ratio(new) < min(0.4, tamil_ratio(old)):
            rejected.append(f"{key} (almost no Tamil left)")
            continue
        f["set"](new)
        changed += 1
    _sync_voiceover(s, kind)
    probs = d.get("problems") or []
    log(f"Tamil review: {changed} text(s) corrected, {len(rejected)} suggestion(s) refused"
        + (f" ({'; '.join(rejected)})" if rejected else ""))
    for p in probs[:8]:
        log(f"  review note: {str(p)[:160]}")


def finalize(s, kind, notes, llm, log=print):
    """sanitize -> LLM review -> sanitize -> hard check. Returns the script (changed in place).
    Stops (SystemExit) only if the Tamil is still unusable, instead of publishing a bad video."""
    sanitize_script(s, kind)
    try:
        review_script(s, kind, notes, llm, log)
    except (Exception, SystemExit) as e:   # a failed review must never stop the video
        log(f"Tamil review skipped: {e}")
    sanitize_script(s, kind)
    for n in soft_notes(s, kind):
        log(f"  check: {n}")
    bad = hard_problems(s, kind)
    if bad:
        raise SystemExit("Tamil text is not usable, stopping instead of publishing it: " + "; ".join(bad))
    return s


# ----------------------------------------------------------------------------- step 4: numbers -> spoken Tamil
_ONES = ["பூஜ்யம்", "ஒன்று", "இரண்டு", "மூன்று", "நான்கு", "ஐந்து", "ஆறு", "ஏழு", "எட்டு", "ஒன்பது", "பத்து",
         "பதினொன்று", "பன்னிரண்டு", "பதிமூன்று", "பதினான்கு", "பதினைந்து", "பதினாறு", "பதினேழு", "பதினெட்டு",
         "பத்தொன்பது"]
_TENS = {2: ("இருபது", "இருபத்து"), 3: ("முப்பது", "முப்பத்து"), 4: ("நாற்பது", "நாற்பத்து"),
         5: ("ஐம்பது", "ஐம்பத்து"), 6: ("அறுபது", "அறுபத்து"), 7: ("எழுபது", "எழுபத்து"),
         8: ("எண்பது", "எண்பத்து"), 9: ("தொண்ணூறு", "தொண்ணூற்று")}
_HUND = {1: ("நூறு", "நூற்று"), 2: ("இருநூறு", "இருநூற்று"), 3: ("முந்நூறு", "முந்நூற்று"),
         4: ("நானூறு", "நானூற்று"), 5: ("ஐநூறு", "ஐநூற்று"), 6: ("அறுநூறு", "அறுநூற்று"),
         7: ("எழுநூறு", "எழுநூற்று"), 8: ("எண்ணூறு", "எண்ணூற்று"), 9: ("தொள்ளாயிரம்", "தொள்ளாயிரத்து")}
_THOU = {2: "இரண்டா", 3: "மூவா", 4: "நாலா", 5: "ஐயா", 6: "ஆறா", 7: "ஏழா", 8: "எட்டா", 9: "ஒன்பதா", 10: "பத்தா"}


def _below_100(n):
    if n < 20:
        return _ONES[n]
    t, u = divmod(n, 10)
    return _TENS[t][0] if u == 0 else _TENS[t][1] + " " + _ONES[u]


def _below_1000(n):
    h, r = divmod(n, 100)
    if h == 0:
        return _below_100(r)
    return _HUND[h][0] if r == 0 else _HUND[h][1] + " " + _below_100(r)


def _thousands(n, more):
    """n thousand (1..99); `more` is True when something follows (ஆயிரத்து ...)."""
    if n == 1:
        return "ஆயிரத்து" if more else "ஆயிரம்"
    if n in _THOU:
        return _THOU[n] + ("யிரத்து" if more else "யிரம்")
    return _below_100(n) + (" ஆயிரத்து" if more else " ஆயிரம்")


def _below_lakh(n):
    th, r = divmod(n, 1000)
    if th == 0:
        return _below_1000(r)
    if r == 0:
        return _thousands(th, False)
    return _thousands(th, True) + " " + _below_1000(r)


def int_to_tamil(n):
    """0 .. 99,99,99,99,999 in spoken Tamil words (Indian lakh / crore system)."""
    if n < 0:
        return "கழித்தல் " + int_to_tamil(-n)
    if n >= 10 ** 14:
        return " ".join(_ONES[int(c)] for c in str(n))
    if n == 0:
        return _ONES[0]
    crore, rest = divmod(n, 10 ** 7)
    lakh, rest = divmod(rest, 10 ** 5)
    out = []
    if crore:
        c = "ஒரு" if crore == 1 else int_to_tamil(crore)
        out.append(c + (" கோடியே" if (lakh or rest) else " கோடி"))
    if lakh:
        l = "ஒரு" if lakh == 1 else _below_100(lakh)
        out.append(l + (" லட்சத்து" if rest else " லட்சம்"))
    if rest:
        out.append(_below_lakh(rest))
    return " ".join(out)


_NUM = re.compile(r"\d+(?:,\d{2,3})*(?:\.\d+)?")
_RUPEE = re.compile(r"(?<![A-Za-z])(?:₹|Rs\.?|INR)\s*(\d+(?:,\d{2,3})*(?:\.\d+)?)(?:\s*(கோடி|லட்சம்|ஆயிரம்))?")


def _num_words(m):
    raw = m.group(0).replace(",", "")
    whole, _, frac = raw.partition(".")
    if len(whole) > 14 or (len(whole) > 1 and whole.startswith("0")):   # ids, phone numbers: digit by digit
        txt = " ".join(_ONES[int(c)] for c in whole)
    else:
        txt = int_to_tamil(int(whole))
    if frac:
        txt += " புள்ளி " + " ".join(_ONES[int(c)] for c in frac)
    s = m.string
    a, b = m.start(), m.end()
    wordy = lambda ch: ch.isalnum() or "஀" <= ch <= "௿"   # letters, digits and Tamil signs
    left = " " if a > 0 and wordy(s[a - 1]) else ""
    right = " " if b < len(s) and wordy(s[b]) else ""
    return left + txt + right


def digits_to_tamil(text):
    """Every number in the text -> spoken Tamil words. Rupee amounts become '<amount> ரூபாய்'.
    Use it only for the VOICE text; captions and cards keep the digits."""
    t = _RUPEE.sub(lambda m: f"{m.group(1)} {m.group(2) or ''} ரூபாய்", str(text))
    t = _NUM.sub(_num_words, t)
    return re.sub(r"[ \t]{2,}", " ", t).strip()


# ----------------------------------------------------------------------------- voice script (AI prepares the text for the voice)
def speech_similarity(intended, heard):
    """0..1 : how much of the intended Tamil sound text a speech recogniser heard back. Only Tamil letters count
    (spaces, punctuation, digits written as words are all normalised), so small spelling noise is forgiven."""
    import difflib

    def norm(t):
        t = digits_to_tamil(str(t))
        return "".join(_TAMIL_ANY.findall(t))
    a, b = norm(intended), norm(heard)
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


_TAMIL_ANY = re.compile("[\u0B80-\u0BFF]")


def voice_prep(s, kind, llm, log=print):
    """A separate AI pass that rewrites the SPOKEN parts so a text-to-speech voice reads them correctly:
    English words and abbreviations in Tamil letters as people say them, proper nouns in the usual Tamil spelling,
    long sentences split, commas where a speaker pauses, rare or very long words replaced by everyday ones.
    The captions and the cards keep the original text; only the voice uses this version (s['voice_parts'] or
    s['voice_text']). A rewrite is accepted only if numbers are identical, the text is still the same message
    (letter similarity) and no foreign letters appear. Otherwise the original text is spoken. Never stops the video."""
    if kind in ("cards", "manim"):
        items = {name: text for name, text in (s.get("parts") or [])}
    else:
        items = {"voiceover": s.get("voiceover", "")}
    items = {k: v for k, v in items.items() if isinstance(v, str) and v.strip()}
    if not items:
        return s
    import difflib
    prompt = f"""You prepare Tamil text for a Tamil text-to-speech voice (an AI voice that reads the text exactly as written). The goal: the voice must pronounce EVERY word correctly and sound like a friendly teacher talking.

Rewrite each text below for the voice:
1. Do NOT change the meaning, the facts, the names or the order. Do not add or remove information. Keep digits as digits, exactly the same numbers (a program reads digits aloud).
2. English words: an everyday English word that Tamil speakers normally say (online, bank, mobile, budget, startup, school) -> write it in Tamil letters the way it is pronounced in Tamil conversation (ஆன்லைன், பேங்க், ஸ்டார்ட்அப்). A name, brand, abbreviation or technical term -> leave it in English letters exactly as it is; do not translate or respell it (the program makes the voice read it correctly).
3. People, places, schemes and organisations: use the usual Tamil newspaper spelling. For sounds that Tamil letters do not have, use Grantha letters where it helps the voice (ஜ, ஷ, ஸ, ஹ, ஃப, க்ஷ), for example ஹைதராபாத், ஃபைனல்.
4. Split any sentence longer than about 12 words into shorter sentences. Put a comma where a speaker would pause. End every sentence with a full stop or a question mark.
5. A very long compound word or a rare literary word that a voice may misread: replace it with a common everyday word of the same meaning.
6. Keep the casual spoken tone (பேச்சுத் தமிழ்). Do not make it formal and do not add greetings.
Use only Tamil letters, digits, commas, full stops and question marks, plus English letters only for the names and terms you were told to leave.

Return JSON: {{"voice": {{"<same key>": "<text for the voice>", ...}}}} with exactly the same keys.

TEXTS:
{json.dumps(items, ensure_ascii=False, indent=1)}"""
    try:
        d = llm(prompt, model=_model(), temperature=0.2, effort="medium")
    except (Exception, SystemExit) as e:
        log(f"voice script step skipped: {e}")
        return s
    got = d.get("voice") if isinstance(d, dict) else None
    if not isinstance(got, dict):
        log("voice script step gave no usable answer; the original text is spoken")
        return s
    final, changed = {}, 0
    for k, old in items.items():
        new = got.get(k)
        ok = isinstance(new, str) and new.strip()
        if ok:
            new = re.sub(r"\s+", " ", sanitize(new)).strip()
            ok = (new != "" and _nums(new) == _nums(old)
                  and not _FOREIGN.search(new) and tamil_ratio(new) >= min(0.6, tamil_ratio(old))
                  and len(_LATIN_WORD.findall(new)) <= len(_LATIN_WORD.findall(old))
                  and 0.75 * len(old) <= len(new) <= 1.6 * len(old) + 10
                  and difflib.SequenceMatcher(None, "".join(_TAMIL_ANY.findall(old)),
                                              "".join(_TAMIL_ANY.findall(new)), autojunk=False).ratio() >= 0.6)
        if ok:
            final[k] = new
            changed += new != old
        else:
            final[k] = old
    log(f"voice script: {changed} of {len(items)} text(s) rewritten for the voice")
    if kind in ("cards", "manim"):
        s["voice_parts"] = [(name, final.get(name, text)) for name, text in s["parts"]]
    else:
        s["voice_text"] = final["voiceover"]
    return s


# ----------------------------------------------------------------------------- voice: everyday English words
COMMON_ENGLISH = {
    "online": "ஆன்லைன்", "offline": "ஆஃப்லைன்", "bank": "பேங்க்", "mobile": "மொபைல்", "phone": "போன்",
    "budget": "பட்ஜெட்", "school": "ஸ்கூல்", "college": "காலேஜ்", "police": "போலீஸ்", "bus": "பஸ்",
    "train": "டிரெயின்", "metro": "மெட்ரோ", "digital": "டிஜிட்டல்", "internet": "இன்டர்நெட்", "startup": "ஸ்டார்ட்அப்",
    "software": "சாஃப்ட்வேர்", "app": "ஆப்", "ticket": "டிக்கெட்", "card": "கார்டு", "loan": "லோன்", "tax": "டாக்ஸ்",
    "court": "கோர்ட்", "hospital": "ஹாஸ்பிடல்", "doctor": "டாக்டர்", "engineer": "இன்ஜினியர்", "project": "புராஜெக்ட்",
    "plan": "பிளான்", "list": "லிஸ்ட்", "result": "ரிசல்ட்", "exam": "எக்ஸாம்", "video": "வீடியோ",
    "shortcut": "ஷார்ட்கட்", "trick": "டிரிக்", "easy": "ஈசி", "update": "அப்டேட்", "report": "ரிப்போர்ட்",
    "office": "ஆபீஸ்", "cash": "கேஷ்", "rate": "ரேட்", "fund": "ஃபண்ட்", "market": "மார்க்கெட்", "share": "ஷேர்",
    "profit": "பிராஃபிட்", "airport": "ஏர்போர்ட்", "station": "ஸ்டேஷன்", "highway": "ஹைவே", "petrol": "பெட்ரோல்",
    "diesel": "டீசல்", "electric": "எலெக்ட்ரிக்", "vehicle": "வெஹிகிள்", "solar": "சோலார்", "power": "பவர்",
    "award": "அவார்டு", "medal": "மெடல்", "final": "ஃபைனல்", "match": "மேட்ச்", "team": "டீம்", "cricket": "கிரிக்கெட்",
    "hockey": "ஹாக்கி", "football": "ஃபுட்பால்", "summit": "சமிட்", "launch": "லாஞ்ச்", "satellite": "சாட்டிலைட்",
}
_ENGLISH_WORD = re.compile(r"(?<![A-Za-z])[A-Za-z]{2,}(?![A-Za-z])")


def common_english_to_tamil(text):
    """Everyday English words that Tamil speakers use (bank, online, budget ...) -> Tamil letters, so the voice says
    them fluently. A plural -s becomes கள். Other English words (names, brands, terms) are left exactly as they are."""
    def one(m):
        w = m.group(0).lower()
        if w in COMMON_ENGLISH:
            return COMMON_ENGLISH[w]
        if w.endswith("s") and w[:-1] in COMMON_ENGLISH:
            return COMMON_ENGLISH[w[:-1]] + "கள்"
        return m.group(0)
    return _ENGLISH_WORD.sub(one, text)


# ----------------------------------------------------------------------------- voice: unknown acronyms
_LETTER_NAMES = {"A": "ஏ", "B": "பி", "C": "சி", "D": "டி", "E": "இ", "F": "எஃப்", "G": "ஜி", "H": "ஏச்", "I": "ஐ",
                 "J": "ஜே", "K": "கே", "L": "எல்", "M": "எம்", "N": "என்", "O": "ஓ", "P": "பி", "Q": "கியூ",
                 "R": "ஆர்", "S": "எஸ்", "T": "டி", "U": "யு", "V": "வி", "W": "டபிள்யூ", "X": "எக்ஸ்",
                 "Y": "வை", "Z": "செட்"}
_ACRONYM = re.compile(r"(?<![A-Za-z])[A-Z]{2,6}(?![A-Za-z])")


def spell_acronyms(text):
    """Any CAPITAL-letter abbreviation that is still in the voice text (for example SDG, NCERT) is written the way
    Tamil speakers say it letter by letter (எஸ்டிஜி), so the voice does not guess or read it as English."""
    return _ACRONYM.sub(lambda m: "".join(_LETTER_NAMES[c] for c in m.group(0)), text)


# ----------------------------------------------------------------------------- self test
def _selftest():
    cases = {
        0: "பூஜ்யம்", 5: "ஐந்து", 11: "பதினொன்று", 12: "பன்னிரண்டு", 19: "பத்தொன்பது", 20: "இருபது",
        21: "இருபத்து ஒன்று", 99: "தொண்ணூற்று ஒன்பது", 100: "நூறு", 101: "நூற்று ஒன்று",
        250: "இருநூற்று ஐம்பது", 900: "தொள்ளாயிரம்", 999: "தொள்ளாயிரத்து தொண்ணூற்று ஒன்பது",
        1000: "ஆயிரம்", 1001: "ஆயிரத்து ஒன்று", 1999: "ஆயிரத்து தொள்ளாயிரத்து தொண்ணூற்று ஒன்பது",
        2026: "இரண்டாயிரத்து இருபத்து ஆறு", 3000: "மூவாயிரம்", 15000: "பதினைந்து ஆயிரம்",
        100000: "ஒரு லட்சம்", 150000: "ஒரு லட்சத்து ஐம்பது ஆயிரம்", 10000000: "ஒரு கோடி",
        250000000: "இருபத்து ஐந்து கோடி", 25000000: "இரண்டு கோடியே ஐம்பது லட்சம்", 10000001: "ஒரு கோடியே ஒன்று",
    }
    for n, want in cases.items():
        got = int_to_tamil(n)
        assert got == want, f"{n}: got '{got}', want '{want}'"
    assert digits_to_tamil("5.5% வளர்ச்சி") == "ஐந்து புள்ளி ஐந்து% வளர்ச்சி", digits_to_tamil("5.5% வளர்ச்சி")
    assert digits_to_tamil("₹500 கோடி திட்டம்") == "ஐநூறு கோடி ரூபாய் திட்டம்", digits_to_tamil("₹500 கோடி திட்டம்")
    assert digits_to_tamil("1,50,000 பேர்") == "ஒரு லட்சத்து ஐம்பது ஆயிரம் பேர்", digits_to_tamil("1,50,000 பேர்")
    assert digits_to_tamil("2026, ஜனவரி 5") == "இரண்டாயிரத்து இருபத்து ஆறு, ஜனவரி ஐந்து", digits_to_tamil("2026, ஜனவரி 5")
    assert sanitize("வணக்கம் 你好 நண்பர்களே नमस्ते") == "வணக்கம் நண்பர்களே"
    assert sanitize("சரி சரி சரி சரி போங்க") == "சரி சரி போங்க"
    assert tamil_ratio("ஜிஎஸ்டி வரி GST") > 0.6
    assert spell_acronyms("SDG இலக்கு, NCERT புத்தகம், train") == "எஸ்டிஜி இலக்கு, என்சிஇஆர்டி புத்தகம், train"
    g = translation_rules("Chennai and Trichy and RBI repo rate")
    assert "சென்னை" in g and "திருச்சிராப்பள்ளி" in g and "ரிசர்வ் வங்கி" in g and "ரெப்போ" in g
    assert speech_similarity("இன்று 5 செய்திகள்", "இன்று ஐந்து செய்திகள்.") > 0.95
    assert speech_similarity("இன்று ஐந்து செய்திகள்", "zzz") == 0.0
    assert 0.3 < speech_similarity("சென்னை மெட்ரோ இரண்டாம் கட்டம்", "மெட்ரோ கட்டம் வந்தது") < 0.9
    sp = {"parts": [("hook", "நண்பர்களே இது ஸ்டார்ட்அப் பற்றிய 5 செய்திகள்"), ("f1", "ஆர்பிஐ 5.5 சதவீதம் வட்டி வச்சிருக்கு")],
          "voiceover": "x"}
    good = {"voice": {"hook": "நண்பர்களே, இது ஸ்டார்ட்அப் பற்றிய 5 செய்திகள்.", "f1": "ஆர்பிஐ, 6 சதவீதம் வட்டி வச்சிருக்கு."}}
    out = voice_prep(sp, "cards", lambda *a, **k: good, lambda *a: None)
    assert dict(out["voice_parts"])["hook"].endswith("செய்திகள்.")
    assert dict(out["voice_parts"])["f1"] == "ஆர்பிஐ 5.5 சதவீதம் வட்டி வச்சிருக்கு"   # numbers changed -> refused, original kept
    # English card title -> Tamil of a different length is accepted by the review; an English display text no longer stops the video
    sx = {"title": "டிஎன்பிஎஸ்சி தகவல்", "description": "விளக்கம் இது", "headline": "முக்கியம்",
          "remember": "ஒரு டிரிக்", "quiz": "சொல்லுங்க",
          "cards": [{"title": "Dearness Allowance", "detail": "அகவிலைப்படி உயர்வு", "big": ""}],
          "parts": [("hook", "நண்பர்களே இன்னைக்கு செய்தி")], "voiceover": "நண்பர்களே இன்னைக்கு செய்தி"}
    fixed = {"fields": {"card1_title": "அகவிலைப்படி உயர்வு அறிவிப்பு"}, "problems": []}
    out = finalize(sx, "cards", "- DA hike", lambda *a, **k: fixed, lambda *a: None)
    assert out["cards"][0]["title"] == "அகவிலைப்படி உயர்வு அறிவிப்பு", out["cards"][0]["title"]
    sx["cards"][0]["title"] = "Dearness Allowance"
    out = finalize(sx, "cards", "- DA hike", lambda *a, **k: {"fields": {}}, lambda *a: None)   # reviewer cannot fix it: video continues
    assert out["cards"][0]["title"] == "Dearness Allowance"
    assert common_english_to_tamil("online bank, Banks and Reliance Jio, budget") == "ஆன்லைன் பேங்க், பேங்க்கள் and Reliance Jio, பட்ஜெட்", common_english_to_tamil("online bank, Banks and Reliance Jio, budget")
    # an untranslatable English name stays English; a voice rewrite that keeps names but converts everyday words is accepted
    sv = {"parts": [("hook", "Reliance Jio ஆன்லைன் தகவல் இது, 5 புதிய அறிவிப்பு")], "voiceover": "x"}
    ok = {"voice": {"hook": "Reliance Jio, ஆன்லைன் தகவல் இது, 5 புதிய அறிவிப்பு."}}
    assert dict(voice_prep(sv, "cards", lambda *a, **k: ok, lambda *a: None)["voice_parts"])["hook"].startswith("Reliance Jio")
    sk = {"title": "டிஎன்பிஎஸ்சி தகவல்", "description": "விளக்கம் இது", "headline": "DMK GST அறிவிப்பு",
          "remember": "ஒரு டிரிக்", "quiz": "சொல்லுங்க", "cards": [{"title": "Reliance Jio திட்டம்", "detail": "விவரம் இது", "big": ""}],
          "parts": [("hook", "நண்பர்களே Reliance Jio பற்றி இன்னைக்கு பாருங்க")], "voiceover": "நண்பர்களே Reliance Jio பற்றி இன்னைக்கு பாருங்க"}
    out = finalize(sk, "cards", "- Reliance Jio plan", lambda *a, **k: {"fields": {}}, lambda *a: None)
    assert out["cards"][0]["title"] == "Reliance Jio திட்டம்" and out["headline"] == "DMK GST அறிவிப்பு"   # English kept, video continues
    print("tamil_quality self test: all OK")


if __name__ == "__main__":
    _selftest()
