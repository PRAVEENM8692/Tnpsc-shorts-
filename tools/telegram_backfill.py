"""Posts the videos that are already on the YouTube channel into the Telegram channel (oldest first), one message each with the
YouTube link. A video that was posted once is remembered in telegram_posted.json and never posted twice.
DRY_RUN=1 (default) only lists what would be posted. MAX_POSTS limits one run."""
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import pipeline as P  # noqa: E402
import seo_meta  # noqa: E402

STATE = ROOT / "telegram_posted.json"


def main():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat:
        sys.exit("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID secrets are missing")
    dry = (os.environ.get("DRY_RUN") or "1") != "0"
    limit = int(os.environ.get("MAX_POSTS") or 80)
    posted = json.loads(STATE.read_text()) if STATE.exists() else []
    creds = Credentials(None, refresh_token=P.env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
                        client_id=P.env("YT_CLIENT_ID"), client_secret=P.env("YT_CLIENT_SECRET"))
    yt = build("youtube", "v3", credentials=creds)
    uploads = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, tok = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50, pageToken=tok).execute()
        ids += [it["contentDetails"]["videoId"] for it in r.get("items", [])]
        tok = r.get("nextPageToken")
        if not tok:
            break
    vids = []
    for i in range(0, len(ids), 50):
        vids += yt.videos().list(part="snippet,status", id=",".join(ids[i:i + 50])).execute().get("items", [])
    P.log(f"{len(vids)} videos on the channel, {len(posted)} already posted to Telegram")

    base = f"https://api.telegram.org/bot{token}"
    done = skipped = failed = 0
    for v in reversed(vids):   # oldest first
        if v["id"] in posted:
            continue
        if v["status"].get("privacyStatus") != "public":   # a viewer could not open the link, so it is not posted
            skipped += 1
            continue
        if done >= limit:
            break
        sn = v["snippet"]
        head = seo_meta._cut(seo_meta.clean(sn.get("title", "")).replace("#Shorts", "").strip(), 120)
        cap = (f"{head}\n\n▶️ YouTube-ல் பாருங்கள்: https://youtube.com/shorts/{v['id']}\n"
               "💬 உங்கள் பதிலை கமெண்ட்டில் சொல்லுங்கள்!\n🔔 புதிய வீடியோக்களுக்கு SUBSCRIBE செய்யுங்கள்.\n\n#TNPSC #Group4 #Group2 #Group1")
        if dry:
            P.log(f"(dry run) would post: {head[:70]}")
            done += 1
            continue
        r = requests.post(base + "/sendMessage", data={"chat_id": chat, "text": cap}, timeout=60)
        if r.status_code == 429:   # Telegram asks to slow down
            time.sleep(float((r.json().get("parameters") or {}).get("retry_after", 20)) + 1)
            r = requests.post(base + "/sendMessage", data={"chat_id": chat, "text": cap}, timeout=60)
        if r.ok:
            posted.append(v["id"])
            STATE.write_text(json.dumps(posted))
            done += 1
        else:
            failed += 1
            P.log(f"FAILED ({r.status_code}): {' '.join(r.text.split())[:140]}")
            if r.status_code in (400, 401, 403) and not done:
                break   # wrong chat id / bot not allowed: no point in trying the rest
        time.sleep(3.2)   # Telegram allows about 20 messages a minute in a channel
    P.log(f"{'would post' if dry else 'posted'}: {done}; not posted because the video is not public: {skipped}; failed: {failed}")


if __name__ == "__main__":
    main()
