"""Sets the Telegram channel's name, description (About) and profile picture so that people who search Telegram for
TNPSC / Group 4 / current affairs / aptitude find it. The bot must be an admin of the channel with the right to change info.
DRY_RUN=1 (default) only prints what would be set. Uses TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (never printed)."""
import os
import sys
from pathlib import Path

import requests

TITLE = "TNPSC Shorts தமிழ் | Group 1, 2, 4 Current Affairs & Aptitude"
DESC = ("TNPSC Group 1, 2, 4 தேர்வு: Current Affairs, Aptitude குறுக்குவழிகள், சிலபஸ் பாடங்கள் – தமிழில் Shorts. "
        "புதிய வீடியோ + YouTube லிங்க் இங்கே. #TNPSC #Group4 #CurrentAffairs")


def yt_link():
    """The YouTube channel link (so people can subscribe); empty if it cannot be read."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        import pipeline as P
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials(None, refresh_token=P.env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
                            client_id=P.env("YT_CLIENT_ID"), client_secret=P.env("YT_CLIENT_SECRET"))
        it = build("youtube", "v3", credentials=creds).channels().list(part="id,snippet", mine=True).execute()["items"][0]
        cu = (it["snippet"].get("customUrl") or "").strip()
        return f"https://youtube.com/{cu if cu.startswith('@') else 'channel/' + it['id']}"
    except Exception as e:
        print(f"YouTube link not read ({str(e)[:100]})")
        return ""


def main():
    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    dry = (os.environ.get("DRY_RUN") or "1") != "0"
    if not token or not chat:
        sys.exit("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID secrets are missing")
    link = yt_link()
    desc = DESC
    if link and len(desc) + len(link) + 14 <= 255:
        desc += f" ▶️ {link}"
    desc = desc[:255]
    print(f"title ({len(TITLE)}): {TITLE}\ndescription ({len(desc)}): {desc}")
    if dry:
        print("dry run: nothing changed")
        return
    base = f"https://api.telegram.org/bot{token}"
    ok_all = True
    for name, call in (("title", lambda: requests.post(base + "/setChatTitle", data={"chat_id": chat, "title": TITLE}, timeout=60)),
                       ("description", lambda: requests.post(base + "/setChatDescription", data={"chat_id": chat, "description": desc}, timeout=60)),
                       ("photo", lambda: requests.post(base + "/setChatPhoto", data={"chat_id": chat},
                                                       files={"photo": open(Path(__file__).resolve().parent.parent / "assets" / "telegram_profile.png", "rb")}, timeout=120))):
        r = call()
        j = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        ok = r.ok and j.get("ok")
        ok_all &= bool(ok)
        print(f"{name}: {'done' if ok else 'FAILED ' + str(r.status_code) + ' ' + str(j.get('description', ''))[:150]}")
    if not ok_all:
        sys.exit("some parts failed: make the bot an admin with the 'Change Channel Info' right, then run again")


if __name__ == "__main__":
    main()
