"""Free daily TNPSC current-affairs Tamil Short (runs on GitHub Actions).

news search (Tavily) -> English facts -> Tamil script (Groq/OpenAI-compatible LLM) -> Tamil check (tamil_quality.py) -> Tamil voice (Gemini TTS by default when GEMINI_API_KEY is set, free edge-tts as the fallback)
-> images (Pollinations) or Manim animation (aptitude) -> video + BGM (ffmpeg) -> YouTube upload (Data API)
"""
import asyncio
import datetime as dt
import json
import random
import re
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
    h["facts"] = h.get("facts", [])[-600:]   # every single fact / question already used in a video
    h["done"] = dict(sorted(h.get("done", {}).items())[-3:])      # which slots were published, last 3 days
    h["tries"] = dict(sorted(h.get("tries", {}).items())[-15:])   # failed attempts per slot
    HISTORY.write_text(json.dumps(h, ensure_ascii=False, indent=1), encoding="utf-8")


def avoid_text(h, n=25):
    t = h.get("titles", [])[-n:]
    f = [x[:120] for x in h.get("facts", [])[-40:]]
    if not t and not f:
        return ""
    out = ""
    if f:
        out += ("\n\nThese exact facts / questions were ALREADY told in earlier videos. Do NOT use any of them again, even if a "
                "news site words it differently or it is the same event: pick completely different facts:\n"
                + "\n".join(f"- {x}" for x in f))
    if t:
        out += "\n\nEarlier video titles (do not repeat the same topics):\n" + "\n".join(f"- {x}" for x in t[-10:])
    return out


def fact_lines(s):
    """The individual facts (or the question) this script teaches, as short lines for the no-repeat memory."""
    cards = s.get("cards")
    if cards:
        return [f"{c.get('title', '')}: {c.get('detail', '')}".strip(": ")[:170] for c in cards if isinstance(c, dict)]
    if s.get("screen_question"):
        return [str(s["screen_question"])[:170]]
    return [str(s.get("description") or s.get("title") or "")[:300]]


def find_repeats(s, hist):
    """Facts of the new script that were already told earlier (same event, even if worded differently). [] if none / if the check fails."""
    old = [x[:110] for x in hist.get("facts", [])[-70:]]
    new = fact_lines(s)
    if not old or not new:
        return []
    fast = []
    try:   # no AI needed: same words / same numbers as ANY fact told before (not only the last 70)
        from shorts_helpers import is_repeat
        allold = hist.get("facts", [])
        fast = [x for x in new if is_repeat(x, allold)]
        if fast:
            log(f"{len(fast)} fact(s) match an earlier video by word overlap")
    except Exception as e:
        log(f"word-overlap repeat check skipped: {e}")
    try:
        d = llm_json("Below are FACTS ALREADY USED in earlier videos, then NEW facts for a new video. List the NEW facts "
                     "that tell the same event, announcement, number or question as an old one (even if worded differently or from "
                     "another news site). Be strict about the same event, but a different event on a similar topic is NOT a repeat.\n\n"
                     "OLD:\n" + "\n".join(f"- {x}" for x in old) + "\n\nNEW:\n"
                     + "\n".join(f"{i}. {x}" for i, x in enumerate(new)) + '\n\nReturn JSON: {"repeated": [indexes of the NEW facts that repeat]}',
                     temperature=0.1)
        idx = {int(i) for i in d.get("repeated", []) if str(i).lstrip("-").isdigit() and 0 <= int(i) < len(new)}
        return [x for i, x in enumerate(new) if x in fast or i in idx]
    except (Exception, SystemExit) as e:
        log(f"repeat check skipped: {e}")
        return fast


def no_repeats(s, hist, rewrite, extra):
    """Writes the script again (up to 2 times) while it still contains facts used in earlier videos."""
    for attempt in range(2):
        dup = find_repeats(s, hist)
        if not dup:
            return s
        log(f"{len(dup)} repeated fact(s) found, writing the script again ({attempt + 1}/2): " + " | ".join(x[:50] for x in dup))
        extra[0] += "\n\nYour last draft repeated these old facts, so do NOT use them or the same events:\n" + "\n".join(f"- {x}" for x in dup)
        try:
            s = rewrite()
        except (Exception, SystemExit) as e:
            log(f"rewrite failed ({e}); keeping the previous draft")
            return s
    left = find_repeats(s, hist)
    if left:
        log(f"warning: {len(left)} fact(s) still repeat after rewriting (not enough new news)")
    return s


# ---------------------------------------------------------------- 1. news search
# 7 videos a day: 3 current affairs + 2 aptitude + 2 syllabus lessons (see .github/workflows/daily.yml for the clock times)
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
    6: ("lesson", "Syllabus lesson A", None, None),   # a TNPSC Group 1 / 2 / 4 syllabus topic taught like a class
    7: ("lesson", "Syllabus lesson B", None, None),
}
START_TIMES = {1: 8.0, 2: 10.5, 3: 13.0, 4: 15.5, 5: 18.0, 6: 19.5, 7: 21.0}   # IST hours (same table as plan.py)

# TNPSC Group 1 / 2 / 4 general-studies syllabus: one subject per lesson, topics rotate so nothing repeats for months
SYLLABUS = {
    "Indian Polity": ["President of India: powers and responsibilities", "Governor: powers and responsibilities",
                      "Prime Minister and Council of Ministers", "Parliament: Lok Sabha and Rajya Sabha", "Supreme Court and High Courts",
                      "Fundamental Rights", "Directive Principles and Fundamental Duties", "Preamble of the Constitution",
                      "Central Vigilance Commission (CVC)", "CBI and its powers", "Comptroller and Auditor General (CAG)",
                      "Election Commission of India", "UPSC and TNPSC", "Panchayati Raj system", "District administration: Collector and powers",
                      "State administration: Chief Minister and Secretariat", "Constitutional amendments", "Emergency provisions",
                      "Right to Information Act", "Lokpal and Lokayukta"],
    "Indian History": ["Delhi Sultanate: Slave dynasty", "Khilji and Tughlaq dynasties", "Mughal emperors: Babur and Humayun",
                       "Akbar and his administration", "Shah Jahan and Aurangzeb", "Maratha Empire and Shivaji", "Vijayanagara Empire",
                       "Bhakti and Sufi movements", "Revolt of 1857", "Indian National Congress and moderates", "Gandhian era movements",
                       "Quit India Movement", "Mauryan Empire and Ashoka", "Gupta Empire", "Harappan civilisation"],
    "Tamil Nadu History and Culture": ["Chola kingdom: administration and temples", "Chola kings: Rajaraja I and Rajendra I",
                                       "Pandya kingdom", "Pallava kingdom and Mahabalipuram", "Chera kingdom", "Sangam age and literature",
                                       "Kalabhras and Bhakti period in Tamil Nadu", "Nayaks of Madurai and Thanjavur", "Tamil Nadu freedom fighters",
                                       "Dravidian movement and social reformers", "Tamil Nadu temples and architecture", "Tamil Nadu folk arts and festivals"],
    "Geography": ["Major rivers of India: Himalayan rivers", "Peninsular rivers of India", "Rivers of Tamil Nadu", "Monsoon and climate of India",
                  "Soils of India", "Mountains and plateaus of India", "Tamil Nadu: physical features and districts", "Natural vegetation and forests of India",
                  "Minerals and power resources", "Agriculture and major crops of India", "Ports and transport of India", "Earth: latitudes, longitudes and time"],
    "General Science": ["Newton's laws of motion", "Light: reflection and refraction", "Electricity basics", "Human digestive system",
                        "Vitamins and deficiency diseases", "Blood and circulatory system", "Acids, bases and salts", "Metals and non-metals",
                        "Cell: the unit of life", "Plant nutrition and photosynthesis", "Space technology and ISRO missions", "Diseases and vaccines",
                        "Environment and ecosystem", "Energy sources: renewable and non-renewable"],
    "Indian Economy": ["GDP, GNP and national income", "Inflation and its types", "Reserve Bank of India and monetary policy", "Banking in India",
                       "Budget and fiscal policy", "GST and indirect taxes", "Five Year Plans and NITI Aayog", "Poverty and unemployment",
                       "Tamil Nadu economy and industries", "Agriculture schemes and MSP"],
    "Tamil Nadu Administration and Welfare": ["Tamil Nadu government departments and schemes", "Local bodies in Tamil Nadu", "Tamil Nadu welfare boards",
                                              "Tamil Nadu Public Service Commission", "Tamil Nadu legislative assembly", "Social justice in Tamil Nadu: reservation"],
}


def lesson_topic(slot, hist):
    """The syllabus topic for this lesson slot today: rotates through the subjects, skips topics taught recently."""
    subjects = list(SYLLABUS)
    flat = []
    for i in range(max(len(v) for v in SYLLABUS.values())):
        for sub in subjects:
            if i < len(SYLLABUS[sub]):
                flat.append((sub, SYLLABUS[sub][i]))
    doy = dt.datetime.now(IST).timetuple().tm_yday
    start = (doy * 2 + (slot - 6)) % len(flat)
    taught = set(hist.get("lessons", [])[-len(flat) + 2:])
    for k in range(len(flat)):
        sub, top = flat[(start + k) % len(flat)]
        if top not in taught:
            return sub, top
    return flat[start]


def lesson_notes(subject, topic):
    """Reference notes for a syllabus lesson: Gemini with Google Search (free tier); Tavily search as the fallback."""
    key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    q = (f"TNPSC Group 1 / Group 2 / Group 4 exam topic: '{topic}' (subject: {subject}). Search the web (official sources, NCERT / "
         f"Tamil Nadu textbooks, Government of India or Tamil Nadu sites) and write a precise reference note in English, under 350 words: "
         f"the 8 most exam-relevant facts about this topic with exact names, numbers, years and article / section numbers where they apply, "
         f"in a sensible teaching order, plus 2 facts that exam questions commonly ask. Do not invent anything.")
    if key:
        model = (os.environ.get("GEMINI_TEXT_MODEL") or "").strip() or _gemini_text_model(key) or "gemini-2.5-flash"
        try:
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                              headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                              json={"contents": [{"parts": [{"text": q}]}], "tools": [{"google_search": {}}]}, timeout=150)
            if r.status_code == 200:
                text = " ".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"]).strip()
                if len(text) > 300:
                    log(f"lesson notes from Gemini search ({len(text)} chars)")
                    return "- " + " ".join(text.split())[:3800] + " (Gemini web search)", ["Gemini web search"]
            else:
                log(f"lesson research skipped (Gemini {model} HTTP {r.status_code}): {' '.join(r.text.split())[:200]}")
        except Exception as e:
            log(f"lesson research skipped ({e})")
    try:   # fallback: Tavily general search
        r = requests.post("https://api.tavily.com/search", headers={"Authorization": f"Bearer {env('TAVILY_API_KEY')}"},
                          json={"query": f"{topic} {subject} TNPSC notes", "max_results": 6}, timeout=60)
        r.raise_for_status()
        items = r.json().get("results", [])
        hosts = list(dict.fromkeys(urllib.parse.urlparse(x["url"]).netloc.replace("www.", "") for x in items))
        notes = "\n".join(f"- {x.get('title', '')}: {(x.get('content') or '')[:600]}" for x in items)
        if len(notes) > 400:
            log(f"lesson notes from Tavily search ({len(notes)} chars)")
            return notes, hosts[:4]
    except Exception as e:
        log(f"lesson search failed: {e}")
    sys.exit("Could not collect reliable notes for the lesson; stopping instead of inventing facts.")
NEXT_APT = ""   # tomorrow's aptitude topic, set per run, teased at the end of the aptitude videos

APTITUDE_TOPICS = [
    "Percentage shortcuts", "Ratio and proportion", "Time and work", "Speed, time and distance",
    "Simple interest", "Compound interest shortcut", "Average", "Profit and loss", "HCF and LCM",
    "Ages problems", "Number series", "Square and cube tricks", "Mixtures and alligation",
    "Pipes and cisterns", "Trains problems", "Boats and streams", "Mensuration (area, perimeter)",
    "Divisibility rules", "Simplification (BODMAS tricks)", "Calendar and clock problems",
]





# ---------------------------------------------------------------- 1b. main source: tnpscthervupettagam.com daily PDFs
SITE = "https://www.tnpscthervupettagam.com"
SITE_HEAD = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
# which part of the daily PDF each slot uses (the English PDF is read; the Tamil PDF uses an old font that cannot be copied as text)
SITE_SECTIONS = {
    1: r"tamil\s*nadu",
    2: r"national|india|econom|bank|polity|government",
    4: r"international|world|science|technolog|sport|award|important\s*days|environment|space",
}


def _pdf_text(data):
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "x.pdf"
        f.write_bytes(data)
        try:
            return subprocess.run(["pdftotext", "-layout", str(f), "-"], capture_output=True, text=True, timeout=90).stdout
        except (OSError, subprocess.SubprocessError):
            pass
        try:
            from pypdf import PdfReader
            return "\n".join((pg.extract_text() or "") for pg in PdfReader(str(f)).pages)
        except Exception:
            return ""


def _section(text, pattern):
    """Text of the headed sections whose heading matches pattern (a heading = a short line); "" if none."""
    lines = [l.rstrip() for l in text.splitlines()]
    out, on = [], False
    for l in lines:
        t = l.strip()
        if 2 < len(t) < 45 and not t.endswith((".", ",")) and (t.isupper() or t.istitle() or t.lower().endswith(("news", "affairs", "days"))):
            on = bool(re.search(pattern, t, re.I))
            continue
        if on and t:
            out.append(t)
    return "\n".join(out)


def site_notes(slot, today_dt):
    """Current-affairs notes from the website's latest daily English PDFs; None if the site cannot be read (then Tavily is used)."""
    if (os.environ.get("SITE_SOURCE") or "1").strip() == "0":
        return None
    try:
        links = []
        for back in (0, 1):   # this month's page, and the previous one right at the start of a month
            d = (today_dt.replace(day=1) - dt.timedelta(days=1)).replace(day=1) if back else today_dt
            page = f"{SITE}/downloads-detail/tnpsc-daily-current-affairs-%E2%80%93-{d.strftime('%B').lower()}-{d.year}?cat=tnpsc-daily-current-affairs"
            r = requests.get(os.environ.get("SITE_URL") or page if not back else page, headers=SITE_HEAD, timeout=60)
            if r.status_code != 200:
                continue
            found = re.findall(r'href="([^"]+\.pdf)"', r.text, re.I)
            links = [urllib.parse.urljoin(page, u.replace(" ", "%20")) for u in found if "english" in u.lower()] + links
            if len(links) >= 3:
                break
        links = list(dict.fromkeys(links))[-3:][::-1]   # the 3 newest days, newest first
        if not links:
            log("website: no PDF links found; using news search instead")
            return None
        chunks = []
        for u in links:
            data = requests.get(u, headers=SITE_HEAD, timeout=90).content
            text = _pdf_text(data)
            part = _section(text, SITE_SECTIONS.get(slot, "."))
            if len(part) < 500:
                part = re.sub(r"\n{2,}", "\n", text)   # headings not recognised: use the whole day
            name = urllib.parse.unquote(u.rsplit("/", 1)[-1])
            chunks.append(f"- ({name}): " + re.sub(r"\s+", " ", part)[:2600])
        notes = "\n".join(chunks)
        if len(notes) < 800:
            log("website text too short; using news search instead")
            return None
        log(f"website: read {len(links)} daily PDFs ({len(notes)} characters)")
        return notes, ["tnpscthervupettagam.com"], []
    except Exception as e:
        log(f"website could not be read ({e}); using news search instead")
        return None


def search_news(queries, used_urls=()):
    key = env("TAVILY_API_KEY")
    seen, items = set(used_urls), []
    # normally the last 3 days; if too few NEW stories are left (many videos already made), look back a week
    for days, count in ((3, 6), (7, 10)):
        for q in queries:
            r = requests.post(
                "https://api.tavily.com/search",
                headers={"Authorization": f"Bearer {key}"},
                json={"query": q, "topic": "news", "days": days, "max_results": count},
                timeout=60,
            )
            r.raise_for_status()
            for x in r.json().get("results", []):
                if x["url"] in seen:
                    continue
                seen.add(x["url"])
                host = urllib.parse.urlparse(x["url"]).netloc.replace("www.", "")
                items.append({"title": x.get("title", ""), "host": host, "url": x["url"], "text": (x.get("content") or "")[:450]})
        if len(items) >= 4:
            break
        log(f"only {len(items)} new stories found for the last {days} days; widening the search")
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


def next_model(base, headers, bad):
    """Another chat model of the same provider that has not hit its limit yet (each model has its own free quota); None if there is none."""
    r = requests.get(base + "/models", headers=headers, timeout=60)
    r.raise_for_status()
    ids = [m["id"] for m in r.json().get("data", []) if m.get("active", True)]
    ids = [i for i in ids if not any(b_ in i.lower() for b_ in ("whisper", "guard", "tts", "orpheus", "embed", "safeguard"))]
    for pref in ("gpt-oss-120b", "llama-3.3-70b", "gpt-oss-20b", "llama-4-maverick", "llama-4-scout", "kimi", "qwen", "llama-3.1-8b"):
        for i in ids:
            if pref in i.lower() and i not in bad:
                return i
    return None


def gemini_json(prompt, temperature=0.5):
    """The same job on Gemini (free tier, good Tamil): the back-up when the Groq quota of the day is used up. None if it cannot answer."""
    key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if not key:
        return None
    model = (os.environ.get("GEMINI_TEXT_MODEL") or "").strip() or _gemini_text_model(key) or "gemini-2.5-flash"
    for attempt in range(2):
        try:
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                              headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                              json={"contents": [{"parts": [{"text": prompt}]}],
                                    "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"}}, timeout=180)
            if r.status_code == 429 and attempt == 0:
                time.sleep(20)
                continue
            if r.status_code != 200:
                log(f"Gemini back-up failed: HTTP {r.status_code} {' '.join(r.text.split())[:160]}")
                return None
            txt = "".join(p_.get("text", "") for p_ in r.json()["candidates"][0]["content"]["parts"])
            a, b = txt.find("{"), txt.rfind("}")
            return json.loads(txt[a:b + 1])
        except Exception as e:
            log(f"Gemini back-up failed: {e}")
            return None
    return None


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
                   "temperature": temperature, "max_tokens": 3500 if effort == "low" else 6000}
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
    for attempt in range(8):
        if r.status_code == 413 or (r.status_code == 429 and "tokens per day" in r.text):   # too big for this model / its quota of the day is gone
            d = gemini_json(prompt, temperature)
            if d:
                log("answered by the Gemini back-up")
                return d
        if r.status_code == 429:  # free-tier rate limit
            try:
                wait = float(r.headers.get("retry-after") or 30)
            except ValueError:
                wait = 30.0
            log(f"LLM rate limited ({' '.join(r.text.split())[:200]}); retry-after {wait:.0f}s")
            if attempt >= 4:   # still limited after several waits: let Gemini (good Tamil) answer before any weaker model does
                d = gemini_json(prompt, temperature)
                if d:
                    log("answered by the Gemini back-up")
                    return d
            # only a LONG wait means this model's quota of the day is used up: then switch to another model of the same provider.
            # A short per-minute limit is just waited out (the smaller models write Tamil that fails the Tamil check).
            if wait > 60:
                _MODEL.setdefault("bad", set()).add(use["name"])
                try:
                    nxt = next_model(base, headers, _MODEL["bad"])
                except Exception:
                    nxt = None
                if nxt:
                    log(f"switching the LLM model from {use['name']} to {nxt}")
                    use["name"] = nxt
                    if not model:
                        _MODEL["name"] = nxt
                    r = call()
                    continue
            time.sleep(min(wait, 60) + 1)
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
    sys.exit(f"LLM unavailable: last answer was HTTP {r.status_code} {' '.join(r.text.split())[:200]}" if not r.ok else "LLM kept returning invalid JSON.")


def write_script(notes, today, focus="", part=1, total=1, avoid=""):
    prompt = f"""You write 45-second YouTube Shorts for TNPSC aspirants in simple spoken TAMIL.

Use ONLY facts that appear in these news notes. Do not add facts from memory:
{notes}

{tq.translation_rules(notes)}

This is video {part} of {total} today, so cover ONLY this theme: {focus}. Pick the 5 most exam-relevant facts for that theme. Make them EASY TO REMEMBER: a punchy hook
line, one short sentence per fact, ONE memory trick (a catchy word, acronym or rhyme in Tamil), then a quick
question for viewers and a line asking them to follow for daily current affairs.
The voiceover must be 70-90 Tamil words (a video of 30-40 seconds), written exactly as it should be spoken (no emojis, no bullets). Start with a QUESTION to the viewer, never with a greeting such as நண்பர்களே or வணக்கம்.

Return JSON with keys:
title (Tamil, under 55 characters, the topic first, NO date and NO ellipsis, for example "TNPSC: தமிழ்நாடு அரசு புதிய வயது வரம்பு"),
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
        lo = 60 if attempt < 3 else 45
        if all(k in d for k in ("title", "description", "tags", "voiceover", "scenes")) \
                and lo <= words <= 120 and len(d["scenes"]) >= 4:
            return d
        log(f"script attempt {attempt + 1} invalid (words={words}); retrying")
        hint = f"\n\nYour previous voiceover had only {words} words. Write at least 70 Tamil words."
    sys.exit("Could not get a valid script from the LLM.")


NEWS_SAY = ("say_hook", "say_f1", "say_f2", "say_f3", "say_f4", "say_f5", "say_outro")


def write_news_cards_script(notes, today, focus="", part=1, total=1, avoid="", lesson=False):
    """Current-affairs script for the news-card video: the voice is written in PARTS (hook, fact 1-5, outro) so each card appears exactly when its part starts. Raises (or exits) if the LLM cannot produce it."""
    prompt = f"""You write 45-second YouTube Shorts for TNPSC aspirants in simple spoken TAMIL.
Use ONLY facts that appear in these news notes. Do not add facts, numbers or dates from memory:
{notes}

{tq.translation_rules(notes)}

This is video {part} of {total} today, so cover ONLY this theme: {focus}. Pick the 5 most exam-relevant facts for that theme.
The video shows ONE CARD per fact while a voice explains it, so every card text must say the SAME fact as its spoken part.

{CASUAL_NEWS}

Return JSON with these keys:
title (Tamil, under 55 characters, the topic first, NO date and NO ellipsis, for example "TNPSC: தமிழ்நாடு அரசு புதிய வயது வரம்பு"),
description (Tamil, 3-5 line recap of the facts),
tags (list of 8 strings, Tamil and English),
headline (Tamil, shown BIG in the very first second: a real QUESTION to the viewer that ends with a question mark ?, at most 60 characters, for example "இந்த கேள்வி Group 4-ல் வந்தது! உங்களுக்கு தெரியுமா?" or "குத்புதீன் ஐபக் எப்படி இறந்தார் தெரியுமா?". It must NOT be a statement, a plain title, an announcement or a greeting, and it must not contain a date),
cards (list of EXACTLY 5 objects, one per fact in spoken order, each with:
   title (Tamil, the fact's subject, at most 45 characters),
   detail (Tamil, one clear sentence with the key who / what / where, at most 110 characters, digits allowed),
   big (the single most important number, date or amount from the notes, at most 12 characters, for example "2026" or "5.5%", or an empty string if there is none)),
quiz (Tamil, a quick question for the viewers about one of the facts, at most 60 characters),
scenes (list of exactly 5 English prompts, one per fact, each a vertical cinematic image that relates to that fact: places, buildings, objects and symbols. NO text or letters in the image, NO logos, NO faces, NO real people or politicians),
and the SPOKEN parts, each one to three short sentences:
say_hook (the headline question spoken in about 10 words; NEVER start with a greeting such as நண்பர்களே or வணக்கம்),
say_f1, say_f2, say_f3, say_f4, say_f5 (the five facts, one short sentence or two each),
say_outro (asks the quiz question, then asks viewers to follow for daily current affairs).
All the spoken parts together must be 70-90 Tamil words (the video must be 30-45 seconds). Keep every fact to ONE short sentence.

Language rules for the spoken parts (they are read by a Tamil text-to-speech voice): write in Tamil script; everyday English words that Tamil speakers normally use (bank, online, mobile, budget, school) are written in Tamil letters; a name, scheme name, abbreviation or technical term with no good Tamil form stays in English letters exactly as in the news (never invent a Tamil translation for it, the program makes the voice say it correctly); write numbers as digits (the program turns them into spoken Tamil words), no brackets, quotes or hyphens; keep
abbreviations (TNPSC, GST, RBI) in English capital letters; use short sentences of at most
12 words, a comma wherever a speaker would pause, and avoid very long compound words."""
    if lesson:   # a syllabus lesson, not news: same card layout, teaching wording
        for old, new in (("Use ONLY facts that appear in these news notes", "Use ONLY facts that appear in these reference notes"),
                         ("This is video {part} of {total} today, so cover ONLY this theme: {focus}. Pick the 5 most exam-relevant facts for that theme.".format(part=part, total=total, focus=focus),
                          f"This is a CLASS on one TNPSC Group 1 / 2 / 4 syllabus topic: {focus}. Teach the 5 most exam-relevant points of this topic in a logical teaching order, "
                          "from the basic idea to the facts the exam asks (names, numbers, years, article numbers). Each card is one teaching point."),
                         ("follow for daily current affairs", "follow for daily TNPSC lessons")):
            assert old in prompt, old[:40]
            prompt = prompt.replace(old, new)
        prompt += ("\n\nLANGUAGE OF A LESSON (very important): the reference notes are in English, but you TEACH IN TAMIL. Every spoken part must be "
                   "full Tamil sentences with at least 80% Tamil words. Explain every idea in Tamil. Write English subject words in Tamil letters "
                   "(கலெக்டர், ஹரப்பா நாகரிகம், பிரசிடென்ட், கவர்னர், பார்லிமென்ட், ஆர்ட்டிகிள் 74). Keep Latin letters only for official abbreviations "
                   "(CVC, CBI, CAG, GST, RBI) and use digits for numbers and years. Never leave a whole sentence in English.")
    hint = ""
    for attempt in range(5):
        d = llm_json(prompt + avoid + hint)
        parts = [(k[4:], str(d.get(k, "")).strip()) for k in NEWS_SAY]
        words = sum(len(t.split()) for _, t in parts)
        cards = d.get("cards")
        lo = 60 if attempt < 3 else 45
        ok = (all(k in d for k in ("title", "description", "tags", "headline", "quiz"))
              and ("?" in str(d.get("headline", "")) or "？" in str(d.get("headline", "")))
              and all(t for _, t in parts) and isinstance(cards, list) and len(cards) >= 5
              and all(isinstance(c, dict) and str(c.get("title", "")).strip() and str(c.get("detail", "")).strip()
                      for c in cards[:5]) and lo <= words <= 120)
        if not ok:
            log(f"news cards script attempt {attempt + 1} invalid (words={words}); retrying")
            hint = (f"\n\nYour previous answer was invalid: the spoken parts had {words} words in total, or a key / card was "
                    "missing, or the headline was not a question with a ? at the end. Fill EVERY key, give exactly 5 cards, "
                    "write at least 70 Tamil words in the spoken parts and make the headline a real question ending with ?.")
            continue
        d["cards"] = [{"title": str(c["title"]).strip()[:60], "detail": str(c["detail"]).strip()[:150],
                       "big": str(c.get("big") or "").strip()[:14]} for c in cards[:5]]
        d["headline"] = str(d["headline"]).strip()[:80]
        d["quiz"] = str(d["quiz"]).strip()[:90]
        d["chip"] = "பாடம்" if lesson else ""
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
    t = str(expr).replace("×", "*").replace("÷", "/").replace("^", "**").replace("−", "-").replace("–", "-").replace("₹", "").replace(",", "")
    t = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", t)     # 20% -> (20/100)
    t = re.sub(r"(?<=\d)\s*[xX]\s*(?=\d)", "*", t)           # 5 x 4 -> 5*4
    return ev(ast.parse(t.strip(), mode="eval"))


def _gemini_text_model(key):
    """The newest Gemini 'flash' text model this key can use (Google retires old model names, so the name is looked up
    instead of being hard-coded). Returns "" if the list cannot be read."""
    try:
        r = requests.get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200",
                         headers={"x-goog-api-key": key}, timeout=30)
        best = None
        for m in r.json().get("models", []):
            name = m.get("name", "").split("/")[-1]
            if ("flash" not in name or "generateContent" not in m.get("supportedGenerationMethods", [])
                    or any(w in name for w in ("tts", "image", "live", "audio", "lite", "preview", "exp", "latest", "thinking"))):
                continue
            nums = tuple(int(x) for x in re.findall(r"\d+", name)[:2])
            if best is None or nums > best[0]:
                best = (nums, name)
        return best[1] if best else ""
    except Exception:
        return ""


def apt_brief(topic):
    """Optional research step for the aptitude videos: Gemini (free tier) searches the web with Google Search and
    returns a short reference brief (typical TNPSC-style question, the standard shortcut trick, worked example) that
    the script writer then uses as source material. Needs the GEMINI_API_KEY secret; if it is missing, the free limit
    is used up or anything fails, it returns "" and the videos are made exactly as before."""
    key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    if not key or (os.environ.get("APT_RESEARCH") or "1").strip() == "0":
        return ""
    model = (os.environ.get("GEMINI_TEXT_MODEL") or "").strip() or _gemini_text_model(key) or "gemini-2.5-flash"
    q = (f"Search the web for TNPSC / Tamil Nadu competitive exam aptitude and mental ability questions on the topic "
         f"'{topic}'. Give a short reference brief in English (under 220 words): (1) one realistic exam-style question "
         f"with small numbers, (2) the standard SHORTCUT trick that saves time versus the long method, in 3 steps, "
         f"(3) the worked answer with the arithmetic, (4) one common mistake students make. Be exact; do not invent facts.")
    try:
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                          headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                          json={"contents": [{"parts": [{"text": q}]}], "tools": [{"google_search": {}}]}, timeout=120)
        if r.status_code != 200:
            log(f"aptitude research skipped (Gemini {model} HTTP {r.status_code}): {' '.join(r.text.split())[:300]}")
            return ""
        log(f"aptitude research with Gemini model {model}")
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
spoken TAMIL. Topic: {topic}.

Teach ONE solved aptitude question using a SHORTCUT TRICK that saves time compared with the long method.
Use small, easy numbers, and make the question DIFFERENT each day (random story, names of Tamil Nadu places, new numbers; variation code {random.randint(1000, 9999)}). Structure of the voiceover: a punchy hook, the question stated slowly followed by a request to write the answer in the comments before the solution, the shortcut
in 3-4 very short steps with the numbers, the final answer, a one-line memory tip, then a similar practice
question for the viewer, tomorrow's topic ({NEXT_APT or 'another new shortcut'}) and a line asking them to follow for daily TNPSC aptitude tricks.
The voiceover must be 90-115 Tamil words, written exactly as spoken (no emojis, no bullets, no markdown).
The maths MUST be correct.

Return JSON with keys:
title (Tamil, under 60 characters, mention the topic, NO date),
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
TEACH_APT = ("Teaching method (like a good school teacher): open with a small challenge or a question the viewer wants to answer; "
             "give the idea behind the shortcut in ONE plain sentence (why it works, not just a formula); use a simple everyday Tamil Nadu "
             "example; in every step say what you do AND why, in a few words; warn about the one mistake most students make; "
             "before the answer say a short pause line like 'நீங்களே யோசிங்க' so the viewer tries first; end with a one-line tip to remember. "
             "Keep every spoken part within its sentence limit.")
TEACH_NEWS = ("Teaching method (like a good school teacher): for each fact say WHAT happened in plain words, then add a few words on WHY "
              "it matters or how TNPSC may ask it (for example 'தேர்வில் இதை கேட்பாங்க'); group related facts so they are easy to remember; "
              "a number, a name or a place is repeated once so it sticks. Keep every spoken part within its sentence limit.")
CASUAL_APT = CASUAL_TAMIL + "\n" + TEACH_APT + "\n" + tq.APT_RULES
TAMIL_ONLY = ("LANGUAGE (very important): the source notes are in English, but you speak TAMIL. Every spoken part must be full Tamil sentences "
              "with at least 80% Tamil words: explain everything in Tamil and write English words in Tamil letters (கவர்னர், பார்லிமென்ட், பட்ஜெட், "
              "ஏற்றுமதி). Keep Latin letters only for official abbreviations (RBI, GDP, ISRO, GST) and use digits for numbers. Never leave a whole "
              "sentence in English.")
CASUAL_NEWS = CASUAL_TAMIL + "\n" + TEACH_NEWS + "\n" + TAMIL_ONLY

SAY_KEYS = ("say_hook", "say_question", "say_step1", "say_step2", "say_step3", "say_answer", "say_tip", "say_outro")
FALLBACK_SCENES = ["a notebook and pencil on a wooden study desk, warm light", "an old analog clock on a study table",
                   "coins and a calculator on a desk", "a brass balance scale on a table",
                   "a stack of books beside a glowing lamp"]


def write_aptitude_manim_script(topic, today, avoid=""):
    """Aptitude script for the animated (Manim) video: the voice is written in PARTS (hook, question, step 1-3,
    answer, tip, outro) so the screen can change exactly when each part starts."""
    prompt = f"""You write 45-second YouTube Shorts for TNPSC / Tamil Nadu competitive-exam aspirants. Topic: {topic}.

Teach ONE solved aptitude question using a SHORTCUT TRICK that saves time compared with the long method.
Use small, easy numbers and make the question DIFFERENT each day (random story, names of Tamil Nadu places, new numbers; variation code {random.randint(1000, 9999)}). The maths MUST be correct.
The video shows the question and the 3 steps on the screen while a voice explains them, so the spoken parts and the screen texts must use the SAME numbers.

{CASUAL_APT}

Return JSON with these keys:
title (Tamil, under 60 characters, mention the topic, NO date),
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
say_question (reads the question slowly, then asks viewers to pause and write their answer in the comments before the solution, for example "பதிலை கமெண்ட்ல சொல்லுங்க, அப்புறம் தீர்வு பார்க்கலாம்"),
say_step1, say_step2, say_step3 (the three steps of the shortcut, with the numbers),
say_answer (says the final answer),
say_tip (a one-line memory tip),
say_outro (the practice question for the viewer, then "நாளைக்கு {NEXT_APT or 'இன்னொரு புதிய ஷார்ட்கட்'} பத்தி பார்க்கலாம்" as tomorrow's topic in Tamil, then a line asking them to follow for daily TNPSC aptitude tricks).
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
_VOICE = {"name": None, "kind": "news", "part": None}

# how Gemini should speak each part of a video (the style is a hint, the words are read exactly as written)
PART_STYLE = {
    "hook": "energetic and curious, a punchy hook that makes people stop scrolling",
    "outro": "warm and inviting, asking the viewers a question and encouraging them to follow",
    "question": "clear and curious, slightly slower, like reading out a puzzle",
    "step1": "clear, patient and confident, like explaining a trick step by step",
    "step2": "clear, patient and confident, like explaining a trick step by step",
    "step3": "clear, patient and confident, like explaining a trick step by step",
    "answer": "triumphant and happy, announcing the answer",
    "tip": "friendly and encouraging, a handy memory tip",
}


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


# ElevenLabs is switched OFF on purpose (decision 2026-11-08). The code below stays so it can be switched on again later:
# set ELEVEN_ON to True (and pass the ELEVENLABS_API_KEY secret to the step in daily.yml). The secret itself is kept in GitHub.
ELEVEN_ON = False


def tts_engine():
    """Gemini TTS is the DEFAULT voice when the GEMINI_API_KEY secret exists; the free edge-tts (Microsoft Edge neural
    Tamil voices, no key) takes over automatically if Gemini fails or its free limit is used up, and is used for
    every video when there is no key. To force the free voice only, set TTS_ENGINE=edge."""
    e = (os.environ.get("TTS_ENGINE") or "").strip().lower()
    if e == "edge":
        return "edge"
    if ELEVEN_ON and (e == "eleven" or eleven_slot()):
        return "eleven"
    return "gemini" if (os.environ.get("GEMINI_API_KEY") or "").strip() else "edge"


def eleven_slot():
    """True when THIS slot should speak with the user's own cloned voice (ElevenLabs). Needs the ELEVENLABS_API_KEY secret.
    ELEVEN_SLOTS (repo variable, default "1") says which slots; "all" = every slot; "" or "none" = off."""
    if not (os.environ.get("ELEVENLABS_API_KEY") or "").strip():
        return False
    slots = (os.environ.get("ELEVEN_SLOTS") if os.environ.get("ELEVEN_SLOTS") is not None else "1").strip().lower() or "1"
    if slots in ("none", "off", "0"):
        return False
    cur = (os.environ.get("SLOT") or "").strip().lower()
    return slots == "all" or cur in [x.strip() for x in slots.split(",")]


def make_voice_eleven(text, path):
    """Voice from ElevenLabs (the user's own cloned voice). Raises when it cannot get audio, so the caller falls back to
    Gemini / edge-tts. Settings: ELEVENLABS_API_KEY (secret), ELEVEN_VOICE_ID (default: Pravoh_Chennai), ELEVEN_MODEL
    (default eleven_multilingual_v2, which speaks Tamil), ELEVEN_SPEED (default 0.97)."""
    key = (os.environ.get("ELEVENLABS_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("ELEVENLABS_API_KEY secret is not set in GitHub (Settings > Secrets and variables > Actions)")
    voice = (os.environ.get("ELEVEN_VOICE_ID") or "").strip() or "jJvhckyxe1g087sAsDtb"
    model = (os.environ.get("ELEVEN_MODEL") or "").strip() or "eleven_multilingual_v2"
    try:
        speed = float(os.environ.get("ELEVEN_SPEED") or 0.97)
    except ValueError:
        speed = 0.97
    body = {"text": tts_text(text), "model_id": model, "language_code": "ta",
            "voice_settings": {"stability": 0.45, "similarity_boost": 0.85, "style": 0.15, "use_speaker_boost": True, "speed": speed}}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"
    last = "no answer"
    for n in range(3):
        try:
            r = requests.post(url, headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"},
                              json=body, timeout=180)
        except requests.RequestException as e:
            last = str(e)
            time.sleep(5)
            continue
        if r.status_code == 400 and "language_code" in body:   # some models do not take language_code: retry without it
            body.pop("language_code")
            continue
        if r.status_code == 429 and "concurrent" in r.text.lower():
            time.sleep(8 * (n + 1))
            last = "429 too many parallel requests"
            continue
        if r.status_code in (401, 402, 403, 429):   # bad key / credits used up / blocked: waiting will not help
            raise RuntimeError(f"ElevenLabs refused ({r.status_code}): {' '.join(r.text.split())[:200]}")
        if r.status_code >= 500:
            last = f"server error {r.status_code}"
            time.sleep(6)
            continue
        if not r.ok:
            raise RuntimeError(f"ElevenLabs error {r.status_code}: {' '.join(r.text.split())[:200]}")
        if len(r.content) < 2000:
            last = "the answer had no audio"
            continue
        Path(path).write_bytes(r.content)
        return []
    raise RuntimeError("ElevenLabs TTS failed: " + last)


def _engine_chain(engine):
    """The chosen engine first, then the others that can take over (always ending with free edge-tts)."""
    chain = [engine]
    if engine == "eleven" and (os.environ.get("GEMINI_API_KEY") or "").strip():
        chain.append("gemini")
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
    base_style = os.environ.get("GEMINI_STYLE") or ("friendly, casual and clear, like a young teacher chatting with "
                                                      "students, not too fast")
    part = PART_STYLE.get(_VOICE.get("part") or "")
    style = f"{base_style}; for this part: {part}" if part else base_style
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
    if engine == "eleven":
        return make_voice_eleven(text, path)
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
    if engine in ("edge", "eleven"):   # edge-tts is deterministic; ElevenLabs costs credits per take, so no second take
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
    _VOICE["part"] = None
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
        _VOICE["part"] = name
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
    title = rf"{{\fs125{gold}}}TNPSC"
    if head2:
        title += rf"\N{{\fs62{white}}}{head2}"
    if head3:
        title += rf"\N{{\fn{font}\fs54{white}}}{head3}"
    if date_text:
        title += rf"\N{{\fn{latin}\fs50{gold}}}{date_text}"
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


MANIM_THEMES = [   # dark colour sets for the animated aptitude video; one is picked at random per video
    dict(bg="#0B1B3A", panel="#12306B", card="#1B3F8F", card2="#16357A", gold="#FFC93C", green="#3DDC84", rad=1.0),
    dict(bg="#06261C", panel="#0E5C42", card="#137A57", card2="#0E5C42", gold="#7CF0B0", green="#FFD866", rad=1.6),
    dict(bg="#2A0A12", panel="#5A1224", card="#7A162C", card2="#5A1224", gold="#FFC45A", green="#7BE0C3", rad=0.6),
    dict(bg="#150A33", panel="#2E1B6B", card="#462296", card2="#2E1B6B", gold="#5CE1FF", green="#FF8AD8", rad=1.2),
    dict(bg="#062A2E", panel="#0C5560", card="#0F6E7C", card2="#0C5560", gold="#FF9F5C", green="#B6F36B", rad=1.0),
    dict(bg="#1A1A1F", panel="#2A2A33", card="#3A3A46", card2="#2A2A33", gold="#C6F135", green="#5CE1FF", rad=0.8),
]


def make_options(answer):
    """Four A-D options for a quiz layout when the answer contains a number; returns (options, correct_index) or (None, 0)."""
    import re
    m = re.search(r"\d+(?:\.\d+)?", str(answer))
    if not m or len(re.findall(r"\d+(?:\.\d+)?", str(answer))) > 1:   # only a short, single-number answer
        return None, 0
    if False:
        return None, 0
    txt = m.group(0)
    val = float(txt)
    dec = len(txt.split(".")[1]) if "." in txt else 0
    step = max(1.0, round(abs(val) * 0.1)) if dec == 0 else 0.5
    cands = []
    for d in (step, -step, 2 * step, -2 * step, 3 * step, 10 ** len(txt.split(".")[0]) / 10):
        v = val + d
        if v > 0 and v != val and v not in cands:
            cands.append(v)
    wrong = random.sample(cands[:5], 3)
    fmt = (lambda v: f"{v:.{dec}f}")
    vals = wrong + [val]
    random.shuffle(vals)
    pre, post = str(answer)[:m.start()].strip(), str(answer)[m.end():].strip(" .")
    if len(pre) + len(post) > 10:
        return None, 0
    join = lambda v: pre + fmt(v) + (post if post.startswith("%") else (" " + post if post else ""))
    return [join(v) for v in vals], vals.index(val)


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
    opts, correct = make_options(s["screen_answer"]) if random.random() < 0.5 else (None, 0)
    if opts:
        data["options"], data["correct"] = opts, correct
        log("quiz layout: four options")
    theme = random.choice(MANIM_THEMES)
    jpath = (workdir / "apt.json").resolve()
    jpath.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    media = (workdir / "manim_media").resolve()
    e = dict(os.environ, APT_JSON=str(jpath), APT_DURATION=f"{total:.2f}", APT_DATE="", APT_HEADER="0",
             APT_THEME=json.dumps(theme))
    scene_file = str(Path(__file__).with_name("manim_aptitude.py"))
    cmd = [sys.executable, "-m", "manim", "-qm", "--fps", "30", "--media_dir", str(media), "-o", "apt.mp4",
           scene_file, "AptitudeShort"]
    p = subprocess.run(cmd, env=e, capture_output=True, text=True, timeout=900)
    found = sorted(media.rglob("apt.mp4"))
    if p.returncode or not found:
        raise RuntimeError("manim failed: " + (p.stderr or p.stdout)[-800:])
    return found[0]


def pick_bgm():
    """A random background track from assets/ (bgm.mp3 and the generated bgm_*.mp3); None if there is none."""
    tracks = sorted(Path("assets").glob("bgm*.mp3"))
    if not tracks:
        return None
    t = random.choice(tracks)
    log(f"background music for this video: {t.name}")
    return t


SFX_RATE = 44100


def _read_wav(path):
    import wave
    from array import array
    with wave.open(str(path), "rb") as w:
        a = array("h")
        a.frombytes(w.readframes(w.getnframes()))
    return a


def make_sfx(events, total, path):
    """Mixes little sound effects (whoosh / pop / tick / ding / sparkle from assets/sfx_*.wav) at the given seconds
    into one silent-elsewhere wav as long as the video. events: [(second, name, gain)]. Returns the path or None."""
    import wave
    from array import array
    n = int((total + 1) * SFX_RATE)
    mix = array("i", bytes(4 * n))
    cache, used = {}, 0
    for at, name, gain in events:
        f = Path("assets") / f"sfx_{name}.wav"
        if not f.exists() or at < 0:
            continue
        clip = cache.setdefault(name, _read_wav(f))
        i0 = int(at * SFX_RATE)
        for k in range(min(len(clip), n - i0)):
            mix[i0 + k] += int(clip[k] * gain)
        used += 1
    if not used:
        return None
    out = array("h", (max(-32767, min(32767, v)) for v in mix))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SFX_RATE); w.writeframes(out.tobytes())
    return path


def cards_sfx(starts):
    """Sound effects for the news-card video: a whoosh when each card slides in, a ding on the last card."""
    ev = []
    for name, t in starts.items():
        ev.append((max(t - 0.1, 0.0), "ding" if name == "outro" else "whoosh", 0.55 if name == "outro" else 0.6))
    return ev


def manim_sfx(starts):
    """Sound effects for the animated aptitude video: whoosh for the question, pop for every step, a tick for each
    second of the 3-2-1 countdown, a ding + sparkle for the answer."""
    q = max(starts["question"] - 0.1, 0.0)
    s1 = max(starts["step1"] - 0.1, 0.0)
    ev = [(q, "whoosh", 0.6)]
    if s1 - q >= COUNTDOWN_MIN:
        ev += [(s1 - k, "tick", 0.5) for k in (3, 2, 1)]
    for i in (1, 2, 3):
        ev.append((max(starts[f"step{i}"] - 0.1, 0.0), "pop", 0.6))
    a = max(starts["answer"] - 0.1, 0.0)
    ev += [(a, "ding", 0.55), (a + 0.1, "sparkle", 0.4)]
    ev.append((max(starts["outro"] - 0.1, 0.0), "whoosh", 0.55))
    return ev


COUNTDOWN_MIN = 3.4   # the 3-2-1 countdown on the question card is shown only if the question part lasts this long (seconds)


# Voice clean-up for clearer speech: cut low rumble, even out loud and soft words, same loudness for every voice
VOICE_CLEAN = ("highpass=f=70,acompressor=threshold=0.1:ratio=3:attack=5:release=80:makeup=2,"
               "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=44100")


def build_video(images, voice, out, workdir, bgm=None, subs=None, base_video=None, sfx=None):
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

    bgm = bgm or pick_bgm()
    cmd = ["ffmpeg", "-y", "-i", str(joined), "-i", str(voice)]
    n = 2
    if bgm and Path(bgm).exists():
        cmd += ["-stream_loop", "-1", "-i", str(bgm)]
        n += 1
        # the music is a little louder in the gaps and ducks (sidechain) while the voice speaks
        parts = [f"[1:a]{VOICE_CLEAN},apad=pad_dur=1,asplit=2[va][vs]",
                 "[2:a]volume=0.17,afade=t=in:d=1.5[b]",
                 "[b][vs]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[bd]"]
        mix_in, k = "[va][bd]", 2
        if sfx:
            cmd += ["-i", str(sfx)]
            parts.append(f"[{n}:a]volume=0.8[sx]")
            n += 1
            mix_in, k = "[va][bd][sx]", 3
        # amix divides by the number of inputs: 1.8 for two inputs, 2.7 for three keeps the voice level the same
        parts.append(f"{mix_in}amix=inputs={k}:duration=first:dropout_transition=0[m]")
        parts.append(f"[m]volume={0.9 * k:.2f},afade=t=out:st={total - 1.5:.2f}:d=1.5[a]")
        afilter = ";".join(parts)
    else:
        log("WARNING: no assets/bgm*.mp3 found, publishing without BGM")
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
class UploadLimit(Exception):
    """YouTube refused the upload because the channel reached its upload limit (it resets by itself later)."""


def upload(video, title, description, tags, thumb=None):
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
    try:
        while resp is None:
            _, resp = req.next_chunk()
    except Exception as e:
        if "uploadLimitExceeded" in str(e):
            raise UploadLimit(str(e)[:200]) from e
        raise
    log(f"uploaded: https://youtube.com/watch?v={resp['id']} (privacy: {body['status']['privacyStatus']})")
    if thumb:
        try:
            import seo_meta
            if seo_meta.set_thumbnail(yt, resp["id"], thumb):
                log("custom thumbnail set")
        except Exception as e:
            log(f"thumbnail skipped: {e}")
    return resp["id"]


# ---------------------------------------------------------------- 6b. playlists (each video goes into the playlist of its subject)
SUBJECT_TA = {   # syllabus subject -> Tamil name shown in the video header
    "Indian Polity": "இந்திய அரசியலமைப்பு", "Indian History": "இந்திய வரலாறு",
    "Tamil Nadu History and Culture": "தமிழக வரலாறு & பண்பாடு", "Geography": "புவியியல்",
    "General Science": "பொது அறிவியல்", "Indian Economy": "இந்தியப் பொருளாதாரம்",
    "Tamil Nadu Administration and Welfare": "தமிழக நிர்வாகம் & நலத்திட்டங்கள்",
}

SUBJECT_PLAYLISTS = {   # syllabus subject -> playlist title
    "Indian Polity": "பாடம் - இந்திய அரசியலமைப்பு (Polity)",
    "Indian History": "பாடம் - இந்திய வரலாறு (History)",
    "Tamil Nadu History and Culture": "பாடம் - தமிழ்நாடு வரலாறு & பண்பாடு",
    "Geography": "பாடம் - புவியியல் (Geography)",
    "General Science": "பாடம் - அறிவியல் (General Science)",
    "Indian Economy": "பாடம் - இந்தியப் பொருளாதாரம் (Economy)",
    "Tamil Nadu Administration and Welfare": "பாடம் - தமிழ்நாடு நிர்வாகம் & நலத்திட்டங்கள்",
}
NEWS_PLAYLISTS = {1: "நடப்பு நிகழ்வுகள் - தமிழ்நாடு", 2: "நடப்பு நிகழ்வுகள் - இந்தியா & பொருளாதாரம்",
                  4: "நடப்பு நிகழ்வுகள் - உலகம், அறிவியல், விளையாட்டு"}


def playlists_for(kind, slot, focus, topic):
    """Names of the playlists this video belongs to: its own subject first, then the 'all videos of this kind' one."""
    if kind == "lesson":
        subject = (focus or "").split(":")[0].strip()
        return [SUBJECT_PLAYLISTS.get(subject, "பாடம் - பொது அறிவு (General Studies)"), "TNPSC Group 1, 2, 4 - அனைத்து பாடங்கள்"]
    if kind == "news":
        return [NEWS_PLAYLISTS.get(slot, "நடப்பு நிகழ்வுகள்"), "தினசரி நடப்பு நிகழ்வுகள் (All Current Affairs)"]
    return [f"Aptitude - {topic}" if topic else "Aptitude", "Aptitude Shortcuts - அனைத்தும்"]


def playlist_create(yt, name):
    """Creates a playlist; YouTube limits how fast playlists may be created (429 RATE_LIMIT_EXCEEDED), so wait and try again."""
    from googleapiclient.errors import HttpError
    for wait in (30, 60, 90, 0):
        try:
            return yt.playlists().insert(part="snippet,status", body={
                "snippet": {"title": name[:150], "description": "TNPSC Group 1, 2, 4 - தமிழில் தினசரி Shorts", "defaultLanguage": "ta"},
                "status": {"privacyStatus": "public"}}).execute()["id"]
        except HttpError as e:
            if e.resp.status in (409, 429, 500, 503) and wait:
                log(f"playlist creation limited by YouTube; waiting {wait}s")
                time.sleep(wait)
                continue
            raise


def playlist_insert(yt, playlist_id, video_id):
    """playlistItems.insert with retries: YouTube answers 409 'operation was aborted' (or 5xx) now and then, especially right after
    a playlist was created."""
    from googleapiclient.errors import HttpError
    for wait in (3, 6, 12, 20, 0):
        try:
            return yt.playlistItems().insert(part="snippet", body={"snippet": {
                "playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute()
        except HttpError as e:
            if e.resp.status in (409, 500, 502, 503, 504) and wait:
                time.sleep(wait)
                continue
            raise


def telegram_post(video_path, video_id, title, hook=""):
    """Shares the finished video (the file itself plus the YouTube link) in the user's own Telegram channel.
    Needs the secrets TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (@channelusername or the numeric id). Never stops the run."""
    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat:
        return False
    try:
        import seo_meta
        link = f"https://youtube.com/shorts/{video_id}"
        head = seo_meta._cut(seo_meta.clean(title).replace("#Shorts", "").strip(), 120)
        q = seo_meta._cut(seo_meta.clean(hook), 160)
        cap = f"{head}\n\n" + (f"❓ {q}\n\n" if q else "") + (
            f"▶️ YouTube-ல் பாருங்கள்: {link}\n💬 உங்கள் பதிலை YouTube கமெண்ட்டில் சொல்லுங்கள்!\n"
            "🔔 தினமும் TNPSC Shorts-க்கு SUBSCRIBE செய்யுங்கள்.\n\n#TNPSC #Group4 #Group2 #Group1")
        base = f"https://api.telegram.org/bot{token}"
        r = None
        if Path(video_path).stat().st_size < 48 * 1024 * 1024:
            with open(video_path, "rb") as f:
                r = requests.post(base + "/sendVideo", data={"chat_id": chat, "caption": cap[:1000], "supports_streaming": "true"},
                                  files={"video": f}, timeout=180)
        if r is None or not r.ok:
            r = requests.post(base + "/sendMessage", data={"chat_id": chat, "text": cap[:4000]}, timeout=60)
        if r.ok:
            log("shared in the Telegram channel")
            return True
        log(f"TELEGRAM SKIPPED ({r.status_code}): {' '.join(r.text.split())[:160]}")
    except Exception as e:
        log(f"TELEGRAM SKIPPED ({str(e)[:160]})")
    return False


def post_question_comment(video_id, text):
    """Posts the viewers' question as the first comment of the video (this starts the comment section). YouTube's API cannot
    pin a comment: pin it yourself in YouTube Studio. Never stops the run; set YT_COMMENT=0 to switch it off."""
    if (os.environ.get("YT_COMMENT") or "1") == "0" or not text:
        return False
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    try:
        creds = Credentials(None, refresh_token=env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
                            client_id=env("YT_CLIENT_ID"), client_secret=env("YT_CLIENT_SECRET"))   # no scope list: use what was granted
        yt = build("youtube", "v3", credentials=creds)
        body = {"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {"textOriginal": text[:900]}}}}
        yt.commentThreads().insert(part="snippet", body=body).execute()
        log("question comment posted")
        return True
    except HttpError as e:
        from shorts_helpers import yt_error
        why = yt_error(e)
        if "insufficient" in why.lower() or e.resp.status in (401, 403):
            log(f"COMMENT SKIPPED: YouTube refused ({why}). If the reason says insufficientPermissions the token lacks the "
                "force-ssl permission (make a new refresh token); a private video or disabled comments can also cause it. "
                "Set YT_COMMENT=0 to switch the comment off.")
        else:
            log(f"comment step failed ({why}); the video itself is uploaded")
    except Exception as e:
        log(f"comment step failed ({str(e)[:200]}); the video itself is uploaded")
    return False


def add_to_playlists(video_id, names):
    """Puts the uploaded video into the playlists (created when missing). Never stops the run: if the YouTube login was only
    allowed to upload, it says what to do and the video simply stays without a playlist."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    try:
        creds = Credentials(None, refresh_token=env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
                            client_id=env("YT_CLIENT_ID"), client_secret=env("YT_CLIENT_SECRET"))   # no scope list: use what was granted
        yt = build("youtube", "v3", credentials=creds)
        mine, token = {}, None
        while True:
            r = yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=token).execute()
            mine.update({it["snippet"]["title"]: it["id"] for it in r.get("items", [])})
            token = r.get("nextPageToken")
            if not token:
                break
        for name in names:
            pid = mine.get(name)
            if not pid:
                pid = playlist_create(yt, name)
                log(f"playlist created: {name}")
            playlist_insert(yt, pid, video_id)
            log(f"added to playlist: {name}")
    except HttpError as e:
        if "insufficient" in str(e).lower() or e.resp.status in (401, 403):
            log("PLAYLIST SKIPPED: the YouTube login only has upload permission. Run get_youtube_token.py once more "
                "(it now asks for playlist permission too) and replace the YT_REFRESH_TOKEN secret.")
        else:
            log(f"playlist step failed ({str(e)[:200]}); the video itself is uploaded")
    except Exception as e:
        log(f"playlist step failed ({str(e)[:200]}); the video itself is uploaded")


# ---------------------------------------------------------------- main
def make_one(slot, today, stamp, upload_it, hist):
    kind, name, queries, focus = SLOTS[slot]
    tag = f"{stamp}-s{slot}"
    work = OUT / f"work-{tag}"
    work.mkdir(parents=True, exist_ok=True)
    hosts, urls = [], []   # urls only gets filled by news slots; aptitude slots have none
    manim_mode = False
    cards_mode = False

    lesson_topic_name = ""
    if kind in ("news", "lesson"):
        if kind == "lesson":
            subject, lesson_topic_name = lesson_topic(slot, hist)
            focus = f"{subject}: {lesson_topic_name}"
            log(f"[slot {slot}] {name}: {focus}")
            notes, hosts = lesson_notes(subject, lesson_topic_name)
            urls = []
        else:
            log(f"[slot {slot}] {name}: searching news")
            got = site_notes(slot, dt.datetime.now(IST))   # main source: the website's daily PDFs; Tavily search is the fallback
            notes, hosts, urls = got if got else search_news(queries, hist.get("urls", []))
        (OUT / f"notes-{tag}.txt").write_text(notes, encoding="utf-8")
        # step 1 of the Tamil quality layer: any-language news -> clean English facts, THEN write Tamil from them
        log(f"[slot {slot}] cleaning the news into English facts")
        notes = tq.normalize_notes(notes, llm_json, log)
        (OUT / f"facts-{tag}.txt").write_text(notes, encoding="utf-8")
        log(f"[slot {slot}] writing Tamil script")
        # news slots use the HTML news-card video (set repo variable CARDS_SLOTS=none to switch it off, default 1,2,4)
        card_slots = [x.strip() for x in (os.environ.get("CARDS_SLOTS") or "1,2,4,6,7").split(",")]
        s = None
        extra = [""]   # facts a draft repeated, added to the instructions of the next draft
        if str(slot) in card_slots or (kind == "lesson" and "none" not in card_slots):   # lessons always use the card layout
            try:
                s = write_news_cards_script(notes, today, focus, slot, 5, avoid_text(hist) + extra[0], lesson=(kind == "lesson"))
                cards_mode = True
            except (Exception, SystemExit) as e:
                log(f"[slot {slot}] news-card script failed, using the normal script: {e}")
        if s is None:
            s = write_script(notes, today, focus, slot, 5, avoid_text(hist) + extra[0])
        if cards_mode:
            rewrite = lambda: write_news_cards_script(notes, today, focus, slot, 5, avoid_text(hist) + extra[0], lesson=(kind == "lesson"))
        else:
            rewrite = lambda: write_script(notes, today, focus, slot, 5, avoid_text(hist) + extra[0])
        s = no_repeats(s, hist, rewrite, extra)
        if kind == "lesson":
            head2, head3, hashtags = "", "பாடம் - " + SUBJECT_TA.get(focus.split(":")[0], "பொது அறிவு"), "#TNPSC #Group1 #Group2 #Group4 #Shorts"
            pre, post = "Topic: " + focus, "AI-assisted lesson. Verify facts with standard textbooks and official sources."
        else:
            head2, head3, hashtags = "CURRENT AFFAIRS", "நடப்பு நிகழ்வுகள்", "#TNPSC #CurrentAffairs #Shorts"
            pre, post = "Sources: " + ", ".join(hosts), "AI-assisted video. Verify facts with official sources."
    else:
        doy = dt.datetime.now(IST).timetuple().tm_yday
        topic = APTITUDE_TOPICS[(doy * 2 + (0 if slot == 3 else 1)) % len(APTITUDE_TOPICS)]
        global NEXT_APT
        NEXT_APT = APTITUDE_TOPICS[((doy + 1) * 2 + (0 if slot == 3 else 1)) % len(APTITUDE_TOPICS)]
        log(f"[slot {slot}] aptitude topic: {topic} (tomorrow: {NEXT_APT})")
        # which aptitude slots use the animated Manim video (default: slots 3 and 5; set repo variable MANIM_SLOTS=5 for one only)
        manim_slots = [x.strip() for x in (os.environ.get("MANIM_SLOTS") or "3,5").split(",")]
        manim_mode = str(slot) in manim_slots
        avoid_apt = avoid_text(hist, 12) + apt_brief(topic)
        extra = [""]
        if manim_mode:
            rewrite = lambda: write_aptitude_manim_script(topic, today, avoid_apt + extra[0])
        else:
            rewrite = lambda: write_aptitude_script(topic, today, avoid_apt + extra[0])
        s = no_repeats(rewrite(), hist, rewrite, extra)
        head2, head3, hashtags = "APTITUDE TRICKS", "கணிதம் - குறுக்கு வழி", "#TNPSC #Aptitude #MathsTricks #Shorts"
        pre, post = "Topic: " + topic, "AI-assisted video. Practise the method on your own."
    # step 3 of the Tamil quality layer: remove foreign letters, review the Tamil against the English facts, hard check
    (OUT / f"script-{tag}-draft.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    tq_kind = ("cards" if cards_mode else "script") if kind in ("news", "lesson") else ("manim" if manim_mode else "apt")
    log(f"[slot {slot}] checking the Tamil")
    for attempt in range(3):   # the Tamil was unusable: write the whole script again (up to 2 times) before giving up
        try:
            s = tq.finalize(s, tq_kind, notes if kind in ("news", "lesson") else "", llm_json, log)
            break
        except SystemExit as e:
            if attempt == 2:
                raise
            log(f"[slot {slot}] {e}; writing the script again ({attempt + 1}/2)")
            if not manim_mode:   # (the animated aptitude script has its own fixed wording)
                extra[0] += ("\n\nYour last draft was rejected because these spoken parts were not in Tamil: " + str(e)[-200:]
                             + ". Write EVERY spoken part (say_hook, say_f1 ... say_outro) as full Tamil sentences; English terms in Tamil letters.")
            s = rewrite()
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
    write_ass(s["voiceover"], vdur, subs, date_text="", head2=head2, head3=head3,
              spans=speech_spans(voice), total_seconds=vdur + 1.0,
              cta_y=1570 if base else 1000, cta_tamil=base is None, cap_margin=390 if base else 430,
              captions=base is None)   # cards / animation already show the text: no running subtitles
    sfx = None
    try:   # little sound effects at the card / step changes (never worth stopping the video for)
        if starts and base is not None:
            sfx = make_sfx(manim_sfx(starts) if manim_mode else cards_sfx(starts), vdur + 1.0, work / "sfx.wav")
    except Exception as e:
        log(f"[slot {slot}] sound effects skipped: {e}")
    secs = build_video(imgs, voice, final, work, subs=subs, base_video=base, sfx=sfx)
    log(f"[slot {slot}] video ready ({secs:.0f}s): {final}")

    if upload_it:
        try:   # title, description (hook + key points + comment / subscribe call), tags: see seo_meta.py
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import seo_meta
            yt_title, desc, yt_tags = seo_meta.new_video_meta(kind, s, focus=focus if kind == "lesson" else "",
                                                              topic=topic if kind == "aptitude" else "", pre=pre, post=post)
        except Exception as e:
            log(f"[slot {slot}] description builder failed, using the plain text: {e}")
            yt_title, desc, yt_tags = f"{s['title']} #Shorts", s["description"] + f"\n\n{pre}\n{post}\n{hashtags}", [str(t) for t in s["tags"]]
        thumb = None
        if (os.environ.get("YT_THUMBNAIL") or "1") != "0":
            try:
                import seo_meta
                thumb = seo_meta.make_thumbnail(s.get("headline") or s.get("screen_question") or s["title"], kind, work / "thumb.jpg")
            except Exception as e:
                log(f"[slot {slot}] thumbnail not made: {e}")
        try:
            vid = upload(final, yt_title, desc, yt_tags, thumb)
            if vid and (os.environ.get("YT_PLAYLISTS") or "1") != "0":
                add_to_playlists(vid, playlists_for(kind, slot, focus, topic if kind == "aptitude" else ""))
            if vid:
                ask = s.get("headline") or s.get("screen_question") or s.get("quiz") or ""
                post_question_comment(vid, ((s.get("quiz") or s.get("screen_question") or ask) + "\n\nஉங்கள் பதிலை கமெண்ட்டில் சொல்லுங்கள் 👇").strip())
                telegram_post(final, vid, yt_title, ask)
        except UploadLimit as e:
            # not a failure of the video: keep the file (it is in the run's output), do not count a try, and pause the
            # automatic runs for a few hours instead of building the same video again and again
            until = dt.datetime.now(IST) + dt.timedelta(hours=6)
            hist["upload_blocked"] = until.isoformat()
            log(f"[slot {slot}] YouTube upload limit reached ({e}); the finished video is kept in the run output. "
                f"Automatic runs pause until {until:%H:%M} IST.")
            save_history(hist)
            return "limit"
    else:
        log("UPLOAD=false, skipping YouTube upload")

    if upload_it:
        hist.setdefault("done", {}).setdefault(stamp, []).append(slot)
    if upload_it:   # a test run (UPLOAD=false) must not use up the news for the real videos
        hist.setdefault("urls", []).extend(urls)
        hist.setdefault("titles", []).append(f"{name}: {s['title']}")
        hist.setdefault("facts", []).extend(fact_lines(s))
        if lesson_topic_name:
            hist.setdefault("lessons", []).append(lesson_topic_name)
            hist["lessons"] = hist["lessons"][-200:]
        save_history(hist)


def pick_slots():
    v = (os.environ.get("SLOT") or "").strip().lower()
    if v == "all":
        return list(SLOTS)
    if v.isdigit() and int(v) in SLOTS:
        return [int(v)]
    # no slot given: choose by the IST clock (8, 10:30, 13, 15:30, 18)
    h = dt.datetime.now(IST).hour + dt.datetime.now(IST).minute / 60
    return [min(START_TIMES, key=lambda k: abs(START_TIMES[k] - h))]


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
            if make_one(slot, today, stamp, upload_it, hist) == "limit":
                break   # no point building the other videos while YouTube refuses uploads
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
