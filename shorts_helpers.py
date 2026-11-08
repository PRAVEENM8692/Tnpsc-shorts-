"""Small helpers for the TNPSC Shorts pipeline (no dependency on pipeline.py).

clean_title(title)        -> short title, no date, never cut mid-word with "..."
FactStore(path)           -> fact-level duplicate check (not just link/title)
"""
import json
import os
import re

TAMIL_MONTHS = (
    "ஜனவரி|பிப்ரவரி|மார்ச்|ஏப்ரல்|மே|ஜூன்|ஜூலை|ஆகஸ்ட்|செப்டம்பர்|அக்டோபர்|நவம்பர்|டிசம்பர்"
)
EN_MONTHS = (
    "jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|"
    "aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)

_DATE_PATTERNS = [
    # "02 நவம்பர்", "2 நவம்பர் 2026", "நவம்பர் 2", "நவம்பர் 02, 2026"
    re.compile(rf"\b\d{{1,2}}\s*(?:{TAMIL_MONTHS})(?![\u0B80-\u0BFF])(?:\s*\d{{4}})?"),
    re.compile(rf"(?<![\u0B80-\u0BFF])(?:{TAMIL_MONTHS})\s*\d{{1,2}}(?:\s*,?\s*\d{{4}})?"),
    re.compile(rf"\b\d{{1,2}}\s*(?:{EN_MONTHS})\b(?:\s*\d{{4}})?", re.I),
    re.compile(rf"\b(?:{EN_MONTHS})\s*\d{{1,2}}\b(?:\s*,?\s*\d{{4}})?", re.I),
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
]


def clean_title(title, max_len=60):
    """Remove dates and dangling separators, cut at a word boundary, no '...'."""
    t = title or ""
    for p in _DATE_PATTERNS:
        t = p.sub("", t)
    t = t.replace("…", " ").replace("...", " ")
    t = re.sub(r"\s*[–—-]\s*$", "", t.strip())
    t = re.sub(r"\s*[–—-]\s*[–—-]\s*", " – ", t)
    t = re.sub(r"\s+", " ", t).strip(" -–—:|,")
    if len(t) > max_len:
        cut = t[:max_len]
        if " " in cut:
            cut = cut.rsplit(" ", 1)[0]
        t = cut.strip(" -–—:|,")
    return t


def _tokens(text):
    text = (text or "").lower()
    text = re.sub(r"[^\w஀-௿\s]", " ", text)
    return {w for w in text.split() if len(w) > 1}


def _numbers(text):
    return set(re.findall(r"\d+(?:\.\d+)?", text or ""))


def is_repeat(fact, old_facts, threshold=0.6):
    """True when `fact` tells the same thing as any text in `old_facts` (word overlap, or same numbers + half the words)."""
    new_t, new_n = _tokens(fact), _numbers(fact)
    if not new_t:
        return False
    for old in old_facts:
        old_t = _tokens(old)
        if not old_t:
            continue
        inter = len(new_t & old_t)
        if inter / len(new_t | old_t) >= threshold:
            return True
        if new_n and new_n == _numbers(old) and inter / min(len(new_t), len(old_t)) >= 0.5:
            return True
    return False


class FactStore:
    """Remembers every fact already told in any video.

    A new fact counts as a repeat when its word overlap with a stored fact is
    high (Jaccard >= threshold), or when it shares the same numbers AND at
    least half of its words with a stored fact.
    """

    def __init__(self, path="facts.json", threshold=0.6, keep=600):
        self.path = path
        self.threshold = threshold
        self.keep = keep
        self.facts = []
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    self.facts = json.load(f)
            except Exception:  # noqa: BLE001
                self.facts = []

    def is_duplicate(self, fact):
        return is_repeat(fact, self.facts, self.threshold)

    def remember(self, fact):
        self.facts.append(fact)
        self.facts = self.facts[-self.keep:]

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.facts, f, ensure_ascii=False, indent=0)


def yt_error(e, n=380):
    """A readable one-line reason for a YouTube API error: HTTP status, the reason code and YouTube's own message
    (the plain str(e) is cut short and hides which of several causes it really is)."""
    try:
        status = getattr(getattr(e, "resp", None), "status", "?")
        data = json.loads((getattr(e, "content", b"") or b"{}").decode("utf-8", "ignore"))
        err = data.get("error", {})
        first = (err.get("errors") or [{}])[0]
        if not err:
            return " ".join(str(e).split())[:n]
        return f"HTTP {status} | reason={first.get('reason', err.get('status', '?'))} | {err.get('message', '')}"[:n]
    except Exception:
        return " ".join(str(e).split())[:n]
