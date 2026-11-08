"""Titles, descriptions, tags and thumbnails made to bring views, comments and subscribers.

No AI call is needed here (the free LLM quota is tight): everything is built from the script that was already written.
Used for new uploads (pipeline.py) and for the old videos (tools/revamp_videos.py).
"""
import re

MARK = "━━━━━━━━━━━━━━━━━━"      # every revamped description contains this line (so a video is never changed twice)

# letters of other scripts (Chinese, Japanese, Korean, Arabic, Cyrillic, Devanagari ...) sometimes slip out of the AI model
FOREIGN = re.compile("[Ѐ-ӿ֐-ۿऀ-ॿ฀-๿ᄀ-ᇿ⺀-⿿　-ヿ㄀-鿿"
                     "가-힯豈-﫿＀-￯]")
ICON = {"news": "📰", "lesson": "📚", "aptitude": "🧮"}
TAGS_BASE = ["TNPSC", "TNPSC Group 4", "TNPSC Group 2", "TNPSC Group 1", "TNPSC in Tamil", "Tamil Shorts"]
TAGS_KIND = {"news": ["TNPSC current affairs", "current affairs Tamil", "daily current affairs"],
             "lesson": ["TNPSC syllabus", "TNPSC study material", "TNPSC general studies"],
             "aptitude": ["TNPSC aptitude", "maths shortcuts Tamil", "aptitude tricks"]}
HASHTAGS = {"news": "#TNPSC #CurrentAffairs #Group4", "lesson": "#TNPSC #Group4 #Group2",
            "aptitude": "#TNPSC #Aptitude #MathsTricks"}
CTA_LINE = {"news": "❓ ", "lesson": "❓ ", "aptitude": "❓ "}


def tg_link():
    """https://t.me/<channel> from the TELEGRAM_CHAT_ID secret when it is an @channelusername, else ''."""
    import os
    chat = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    return f"https://t.me/{chat[1:]}" if chat.startswith("@") and len(chat) > 3 else ""


def tg_line():
    link = tg_link()
    return f"📲 Telegram channel (வீடியோ + TNPSC அறிவிப்புகள்): {link}" if link else ""


def clean(text):
    """Removes letters of foreign scripts (e.g. '45秒' -> '45') and tidies the spaces."""
    t = FOREIGN.sub("", str(text or ""))
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\s+\n", "\n", t).strip()


def _cut(text, n):
    text = " ".join(text.split())
    if len(text) <= n:
        return text
    cut = text[:n].rsplit(" ", 1)[0]
    return (cut if len(cut) > n * 0.6 else text[:n]).rstrip(" ,.-:") + "…"


def make_title(raw, kind):
    """A short title with a picture at the front (under 100 characters with ' #Shorts')."""
    t = clean(raw)
    t = re.sub(r"#\w+", "", t)
    t = re.sub(r"^[^\w஀-௿]+", "", t)       # an old emoji / mark at the front
    t = re.sub(r"(?:\s+(?:TNPSC|aptitude|\d+))+\s*$", "", t, flags=re.I).strip() or t   # leftover tail such as 'TNPSC aptitude 45'
    t = _cut(t, 62).rstrip(" |–—-:,")
    return f"{ICON.get(kind, '📰')} {t} #Shorts"


def make_tags(tags, kind, topic=""):
    out, seen, size = [], set(), 0
    for x in [clean(t) for t in (tags or [])] + ([topic] if topic else []) + TAGS_KIND.get(kind, []) + TAGS_BASE:
        x = x.strip().lstrip("#")
        if not x or x.lower() in seen or len(x) > 40:
            continue
        if size + len(x) + 1 > 420 or len(out) >= 15:
            break
        seen.add(x.lower())
        out.append(x)
        size += len(x) + 1
    return out


def make_description(kind, hook, points, question="", pre="", post="", topic="", extra_tags=()):
    """hook: the first line (this is what YouTube shows in the feed); points: up to 3 short key facts."""
    hook = _cut(clean(hook), 95)
    lines = [f"{hook} 👇", ""]
    pts = [_cut(clean(p), 140) for p in (points or []) if clean(p)][:3]
    if pts:
        lines.append("✅ இந்த வீடியோவில்:")
        lines += [f"• {p}" for p in pts]
        lines.append("")
    q = _cut(clean(question), 120)
    lines.append("💬 " + (f"{q} உங்கள் பதிலை கமெண்ட்டில் சொல்லுங்கள்!" if q else "உங்கள் பதிலை / சந்தேகத்தை கமெண்ட்டில் சொல்லுங்கள், நான் படிக்கிறேன்!"))
    lines += ["🔔 தினமும் TNPSC Group 1, 2, 4 தயாரிப்புக்கு SUBSCRIBE செய்து Bell 🔔 அழுத்துங்கள்.",
              "📤 உங்கள் TNPSC நண்பர்களுக்கு SHARE செய்யுங்கள்."] + ([tg_line()] if tg_line() else []) + [
              "▶️ இதே தலைப்பின் மற்ற வீடியோக்கள்: எங்கள் சேனலின் Playlists பகுதியில் பாருங்கள்.",
              "", MARK]
    keys = ", ".join(make_tags(list(extra_tags), kind, topic)[:10])
    if pre:
        lines.append(clean(pre))
    if post:
        lines.append(clean(post))
    lines += ["", "🔎 " + keys, "", HASHTAGS.get(kind, "#TNPSC") + " #Shorts"]
    return "\n".join(lines)[:4800]


def new_video_meta(kind, s, focus="", topic="", pre="", post=""):
    """(title, description, tags) for a new upload, from the finished script `s`."""
    cards = s.get("cards") if isinstance(s.get("cards"), list) else []
    if kind == "aptitude":
        hook = s.get("screen_question") or s.get("title") or ""
        body = [x.strip(" -•") for x in str(s.get("description") or "").split("\n") if x.strip()]
        points, question = body[:2], "இந்த கேள்விக்கு உங்கள் விடை என்ன? வீடியோ பார்க்கும் முன் முயற்சி செய்யுங்கள்!"
    else:
        hook = s.get("headline") or s.get("title") or ""
        points = [f"{c.get('title', '')}: {c.get('detail', '')}" for c in cards[:3] if isinstance(c, dict)] \
            or [x.strip(" -•") for x in str(s.get("description") or "").split("\n") if x.strip()][:3]
        question = s.get("quiz") or ""
    title = make_title(s.get("title") or hook, kind)
    desc = make_description(kind, hook, points, question, pre, post, topic or focus.split(":")[0], s.get("tags") or [])
    return title, desc, make_tags(s.get("tags") or [], kind, topic or focus.split(":")[0])


def revamp_existing(kind, title, desc):
    """New (title, description) for a video that is already on the channel; the old text is kept inside it."""
    if MARK in (desc or ""):   # already in the new format: only add the Telegram link if it is missing (no other change)
        link = tg_link()
        if link and link not in desc:
            lines = desc.split("\n")
            i = next((k for k, x in enumerate(lines) if x.startswith("📤")), None)
            if i is not None:
                lines.insert(i + 1, tg_line())
                return title, "\n".join(lines)
        return None
    body, _, rest = (desc or "").strip().partition("\n\n")
    points = [x.strip(" -•") for x in body.split("\n") if x.strip()]
    pre = post = ""
    hashtags = ""
    for ln in rest.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("#"):
            hashtags = ln
        elif ln.lower().startswith(("sources:", "topic:")):
            pre = ln
        else:
            post = ln
    t = re.sub(r"#\w+", "", clean(title))
    t = re.sub(r"^[^\w஀-௿]+", "", t)
    new_title = make_title(t, kind)
    topic = pre.split(":", 1)[1].strip() if pre.lower().startswith("topic:") else ""
    new_desc = make_description(kind, t, points[:3], "", pre, post, topic)
    return new_title, new_desc


# ---------------------------------------------------------------- thumbnail
THUMB_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;font-family:'Noto Sans Tamil','Latha','Nirmala UI','FreeSans',sans-serif}
body{background:linear-gradient(160deg,%(c1)s,%(c2)s);color:#fff;position:relative}
.tag{position:absolute;left:50%%;transform:translateX(-50%%);top:300px;background:%(accent)s;color:%(on)s;font-weight:900;font-size:56px;padding:12px 44px;border-radius:60px;white-space:nowrap}
.ico{position:absolute;left:0;right:0;top:430px;text-align:center;font-size:190px}
.hook{position:absolute;left:70px;right:70px;top:660px;height:720px;display:flex;align-items:center;justify-content:center;text-align:center;
  font-weight:900;line-height:1.25;text-shadow:0 6px 24px rgba(0,0,0,.55)}
.hook b{color:%(accent)s}
.foot{position:absolute;left:70px;right:70px;top:1440px;text-align:center;font-weight:800;font-size:52px}
.foot span{color:%(accent)s}
.sub{margin-top:18px;font-size:48px}
"""
THUMB_THEMES = {"news": ("#0B1B3A", "#12306B", "#FFC93C", "#0B1B3A"), "lesson": ("#06261C", "#0E5C42", "#7CF0B0", "#06261C"),
                "aptitude": ("#2A0A12", "#7A162C", "#FFC45A", "#3A0A16")}
CHIP = {"news": "நடப்பு நிகழ்வுகள்", "lesson": "TNPSC பாடம்", "aptitude": "கணித குறுக்குவழி"}


def make_thumbnail(hook, kind, out_path):
    """1080x1920 (9:16, for Shorts) JPEG under 2 MB: big question on a bright background, all text in the middle so a crop never cuts it. Returns the path (raises on a failure)."""
    import html as _h
    from pathlib import Path
    from playwright.sync_api import sync_playwright

    c1, c2, acc, on = THUMB_THEMES.get(kind, THUMB_THEMES["news"])
    text = _cut(clean(hook), 70)
    words = text.split()
    k = max(1, len(words) // 2)
    marked = _h.escape(" ".join(words[:k])) + " <b>" + _h.escape(" ".join(words[k:])) + "</b>"
    size = 132 if len(text) <= 28 else (112 if len(text) <= 46 else 94)
    doc = (f"<!doctype html><html><head><meta charset='utf-8'><style>{THUMB_CSS % dict(c1=c1, c2=c2, accent=acc, on=on)}"
           f".hook{{font-size:{size}px}}</style></head><body><div class='tag'>{CHIP.get(kind, '')}</div>"
           f"<div class='ico'>{ICON.get(kind, '')}</div><div class='hook'><div>{marked}</div></div>"
           f"<div class='foot'><div>TNPSC <span>Group 1 · 2 · 4</span></div><div class='sub'>தினமும் ▶ SUBSCRIBE</div></div></body></html>")
    out_path = Path(out_path)
    html_path = out_path.with_suffix(".html")
    html_path.write_text(doc, encoding="utf-8")
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome")
        except Exception:
            browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(html_path.resolve().as_uri())
        page.evaluate("document.fonts.ready")
        page.screenshot(path=str(out_path), type="jpeg", quality=88)
        browser.close()
    return out_path


def set_thumbnail(yt, video_id, image_path):  # sets set_thumbnail.blocked when YouTube is rate-limiting thumbnails
    """Sets the custom thumbnail. Never raises: a channel without this feature just keeps the automatic picture."""
    from googleapiclient.http import MediaFileUpload
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(image_path), mimetype="image/jpeg")).execute()
        return True
    except Exception as e:   # not verified channel / missing permission / quota
        print(f"THUMBNAIL SKIPPED ({str(e)[:160]})", flush=True)
        set_thumbnail.blocked = "429" in str(e) or "too many" in str(e).lower() or "quota" in str(e).lower()
        return False
