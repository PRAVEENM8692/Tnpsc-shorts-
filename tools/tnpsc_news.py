"""Watches for new TNPSC news (official site notices + news search) and posts each NEW item once into the Telegram channel.
First run only learns what exists (nothing is posted), so the channel is not flooded with old items.
Switches: DRY_RUN=1 (only print), MAX_POSTS (default 6 per run), SEED_POST=1 (post even on the first run)."""
import json
import os
import re
import sys
import time
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "tnpsc_news_seen.json"
OFFICIAL = ["https://www.tnpsc.gov.in/", "https://www.tnpsc.gov.in/English/Notification.aspx",
            "https://www.tnpsc.gov.in/English/latest_results.aspx"]
KEYS = re.compile(r"notification|result|hall ticket|admit|exam|syllabus|amend|corrigendum|revis|postpon|schedule|tentative|"
                  r"vacanc|recruit|instruction|answer key|counselling|certificate verification|oral test|merit|ranking|cut.?off", re.I)
HEADER = [(re.compile(r"amend|corrigendum|revis|postpon|syllabus|cancel", re.I), "⚠️ TNPSC திருத்தம் / மாற்றம்"),
          (re.compile(r"result|merit|rank|cut.?off|final", re.I), "✅ TNPSC முடிவு"),
          (re.compile(r"hall ticket|admit|exam date|schedule|tentative|answer key", re.I), "🗓️ TNPSC தேர்வு தகவல்"),
          (re.compile(r"notification|vacanc|recruit", re.I), "📢 TNPSC புதிய அறிவிப்பு")]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}


def log(m):
    print(m, flush=True)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self._href, self._txt = [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href, self._txt = dict(attrs).get("href"), []

    def handle_data(self, data):
        if self._href is not None:
            self._txt.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.out.append((" ".join("".join(self._txt).split()), self._href))
            self._href = None


def official():
    found = []
    for page in OFFICIAL:
        try:
            r = requests.get(page, headers=UA, timeout=40)
            if not r.ok:
                log(f"official page {page}: HTTP {r.status_code} (skipped)")
                continue
            p = Links()
            p.feed(r.content.decode("utf-8", errors="replace"))   # the site is UTF-8; r.text guessed the wrong coding (garbled Tamil)
            n = 0
            for text, href in p.out:
                if len(text) >= 22 and href and not href.lower().startswith(("javascript", "mailto", "#")) and KEYS.search(text):
                    found.append((text, urllib.parse.urljoin(page, href.strip()), "tnpsc.gov.in"))
                    n += 1
            log(f"official page {page}: {n} notice-like links")
        except Exception as e:
            log(f"official page {page} not reachable ({str(e)[:90]}), skipped")
    return found


def news():
    key = (os.environ.get("TAVILY_API_KEY") or "").strip()
    if not key or key == "unused":
        return []
    try:
        r = requests.post("https://api.tavily.com/search", headers={"Authorization": f"Bearer {key}"},
                          json={"query": "TNPSC notification OR result OR exam date OR syllabus amendment OR hall ticket",
                                "topic": "news", "days": 2, "max_results": 10}, timeout=60)
        r.raise_for_status()
        out = []
        for x in r.json().get("results", []):
            blob = f"{x.get('title', '')} {x.get('content', '')}"
            if re.search(r"tnpsc|tamil nadu public service commission", blob, re.I) and re.search(
                    r"tnpsc|tamil nadu public service commission", x.get("title", "") + x.get("url", ""), re.I):
                host = urllib.parse.urlparse(x["url"]).netloc.replace("www.", "")
                out.append((" ".join(x.get("title", "").split()), x["url"], host))
        log(f"news search: {len(out)} TNPSC items")
        return out
    except Exception as e:
        log(f"news search failed ({str(e)[:100]})")
        return []


# Only IMPORTANT items go to the Telegram channel: new notifications, results, hall tickets, exam dates / schedule changes,
# syllabus / scheme changes, amendments, corrigenda, answer keys, certificate verification / counselling lists.
IMPORTANT = re.compile(r"(new|change of|changed|revised) date|date of (the )?(written )?exam|press release|notification|recruitment 20\d\d|result|hall ticket|admit card|exam(ination)? date|time ?table|schedule|"
                       r"postpone|reschedul|re-?exam|syllabus|scheme of exam|amend|corrigendum|addendum|supplement|"
                       r"answer key|certificate verification|counselling|cut.?off|final selection|rank list|vacancies (increased|announced)", re.I)
UNIMPORTANT = re.compile(r"instruction|guideline|requisition|question paper|previous year|memo\b|faq|service rules|"
                         r"how to|mock test|study material|admission|apply online guide|list of ", re.I)


def important(title):
    return bool(IMPORTANT.search(title or "")) and not UNIMPORTANT.search(title or "")


def header(title):
    for rx, h in HEADER:
        if rx.search(title):
            return h
    return "📰 TNPSC செய்தி"


def tokens(title):
    """Words of a headline without the site name at the end ('... - The Hindu'), for spotting the same story on another site."""
    t = re.split(r"\s[-|–—]\s", title or "")[0].lower()
    return {w for w in re.findall(r"[a-z0-9\u0b80-\u0bff]+", t) if len(w) > 2 and w not in ("the", "for", "and", "tnpsc", "with", "from", "will", "has", "have")}


def same_story(a, b):
    if len(a) < 3 or len(b) < 3:
        return False
    inter = len(a & b)
    return inter / len(a | b) >= 0.6 or (inter >= 4 and inter / min(len(a), len(b)) >= 0.85)


def norm(u):
    """The identity of a link: host + path + the query without tracking parts (memo / google-news links differ ONLY by their query)."""
    p = urllib.parse.urlparse(u)
    q = "&".join(sorted(x for x in p.query.split("&") if x and not x.lower().startswith(("utm_", "fbclid", "gclid", "ref="))))
    return (p.netloc.replace("www.", "") + p.path).rstrip("/").lower() + ("?" + q if q else "")


def main():
    dry = (os.environ.get("DRY_RUN") or "0") == "1"
    limit = int(os.environ.get("MAX_POSTS") or 6)
    first = not STATE.exists()
    state = json.loads(STATE.read_text()) if not first else {}
    if isinstance(state, list):   # an older file with only the links
        state = {"urls": state, "titles": []}
    seen, seen_titles = state.get("urls", []), [set(x) for x in state.get("titles", [])]
    items, keys, run_titles = [], set(), []
    for t, u, h in official() + news():
        k, tk = norm(u), tokens(t)
        if k in keys or any(same_story(tk, x) for x in run_titles):   # the same story twice in this run (two sites)
            continue
        keys.add(k)
        run_titles.append(tk)
        items.append((t, u, h, k))
    # a story already posted before (even from another site, with another link) is never posted again
    new = [i for i in items if i[3] not in seen and not any(same_story(tokens(i[0]), x) for x in seen_titles)]
    for i in items:   # the old, already-known ones: remember their headlines too
        if i not in new and i[3] not in seen:
            seen.append(i[3])
    log(f"{len(items)} items found, {len(new)} new" + (" (first run: learning only)" if first and (os.environ.get('SEED_POST') != '1') else ""))
    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    post = not dry and token and chat and (not first or os.environ.get("SEED_POST") == "1")
    done = 0
    for t, u, h, k in new:
        if not important(t):   # minor items are only remembered (never posted, never looked at again)
            if dry:
                log(f"(dry run) skipped, not important: {t[:80]}")
            seen.append(k)
            seen_titles.append(tokens(t))
            continue
        if post and done < limit:
            msg = (f"{header(t)}\n\n{t}\n\n🔗 {u}\n🌐 {h}\n\n📺 தினமும் TNPSC Shorts: YouTube-ல் SUBSCRIBE செய்யுங்கள்.\n#TNPSC #Group4 #Group2 #Group1")
            r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat, "text": msg[:4000]}, timeout=60)
            if r.status_code == 429:
                time.sleep(float((r.json().get("parameters") or {}).get("retry_after", 20)) + 1)
                r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat, "text": msg[:4000]}, timeout=60)
            if not r.ok:
                log(f"Telegram FAILED ({r.status_code}): {' '.join(r.text.split())[:140]}")
                continue   # not marked as seen: it is tried again next time
            done += 1
            time.sleep(3.2)
        elif post and done >= limit:
            continue   # over the limit for this run: stays "new" for the next run
        elif dry:
            log(f"(dry run) would post: {header(t)} | {t[:80]} | {u[:80]}")
            continue
        seen.append(k)
        seen_titles.append(tokens(t))
    if not dry:
        STATE.write_text(json.dumps({"urls": seen[-1500:], "titles": [sorted(x) for x in seen_titles[-1500:]]}))
    log(f"posted: {done}")


if __name__ == "__main__":
    main()
