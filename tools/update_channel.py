"""Sets the channel's About text (description) and search keywords from tools/channel_about.txt.
Everything else in the channel's branding (title, country, language ...) is kept as it is.
DRY_RUN=1 (default) only prints the current and the new text."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline as P  # noqa: E402

KEYWORDS = ('TNPSC "TNPSC Group 4" "TNPSC Group 2" "TNPSC Group 1" "TNPSC current affairs" "TNPSC in Tamil" '
            '"TNPSC aptitude" "TNPSC syllabus" "Tamil Shorts" "current affairs Tamil" "maths shortcuts Tamil"')


def main():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    dry = (os.environ.get("DRY_RUN") or "1") != "0"
    text = (Path(__file__).with_name("channel_about.txt")).read_text(encoding="utf-8").strip()
    chat = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()   # @channelusername -> https://t.me/channelusername
    if chat.startswith("@") and len(chat) > 3:
        tg = f"📲 Telegram channel (வீடியோ + TNPSC அறிவிப்புகள்): https://t.me/{chat[1:]}"
        text = text.replace("🔔 புதிய வீடியோக்களை", tg + "\n🔔 புதிய வீடியோக்களை", 1) if "🔔 புதிய வீடியோக்களை" in text else text + "\n" + tg
    else:
        P_warn = "Telegram link not added: TELEGRAM_CHAT_ID is not an @channelusername"
        print(P_warn)
    text = text[:990]
    creds = Credentials(None, refresh_token=P.env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
                        client_id=P.env("YT_CLIENT_ID"), client_secret=P.env("YT_CLIENT_SECRET"))
    yt = build("youtube", "v3", credentials=creds)
    try:
        ch = yt.channels().list(part="id,brandingSettings", mine=True).execute()["items"][0]
        bs = ch.get("brandingSettings") or {}
        cur = bs.setdefault("channel", {})
        P.log("CURRENT description:\n" + (cur.get("description") or "(empty)"))
        P.log("NEW description:\n" + text)
        if dry:
            P.log("dry run: nothing changed")
            return
        cur["description"] = text
        cur["keywords"] = KEYWORDS
        cur.setdefault("defaultLanguage", "ta")
        yt.channels().update(part="brandingSettings", body={"id": ch["id"], "brandingSettings": bs}).execute()
        P.log("channel description updated")
    except HttpError as e:
        sys.exit(f"YouTube refused ({e.resp.status}): {str(e)[:250]}")


if __name__ == "__main__":
    main()
