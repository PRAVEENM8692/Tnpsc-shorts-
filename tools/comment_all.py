"""Posts one question comment on every video of the channel that does not have a comment of the channel yet.

Each comment costs 50 YouTube quota units (daily quota 10,000, the day's uploads use most of it), so MAX_COMMENTS is small by
default; run it again on the next days. Safe to run again: a video that already has a comment of the channel is skipped.
Set DRY_RUN=1 to only list what would be posted. The comments cannot be pinned by the API: pin them by hand in Studio.
"""
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as P  # noqa: E402
from revamp_videos import kind_of  # noqa: E402

TEXT = {
    "news": "இந்த வீடியோவில் உங்களுக்கு புதிதாகத் தெரிந்த செய்தி எது? கமெண்ட்ல சொல்லுங்க, நான் படிக்கிறேன்!",
    "lesson": "இந்த பாடத்தில் உங்களுக்கு சந்தேகம் உள்ள பகுதி எது? கமெண்ட்ல கேளுங்க, நான் படிக்கிறேன்!",
    "aptitude": "இந்த கணக்கின் பதிலை கமெண்ட்ல சொல்லுங்க! சரியா தவறான்னு பார்க்கலாம்!",
}


def main():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from shorts_helpers import yt_error

    limit = int(os.environ.get("MAX_COMMENTS") or 20)
    dry = (os.environ.get("DRY_RUN") or "0") == "1"
    creds = Credentials(None, refresh_token=P.env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
                        client_id=P.env("YT_CLIENT_ID"), client_secret=P.env("YT_CLIENT_SECRET"))
    yt = build("youtube", "v3", credentials=creds)
    ch = yt.channels().list(part="id,contentDetails", mine=True).execute()["items"][0]
    me, uploads = ch["id"], ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids, token = [], None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50, pageToken=token).execute()
        ids += [it["contentDetails"]["videoId"] for it in r.get("items", [])]
        token = r.get("nextPageToken")
        if not token:
            break
    videos = []
    for i in range(0, len(ids), 50):
        videos += yt.videos().list(part="snippet", id=",".join(ids[i:i + 50])).execute().get("items", [])
    P.log(f"{len(videos)} videos on the channel")

    posted = skipped = 0
    for v in videos:   # newest first
        sn = v["snippet"]
        kind = kind_of(sn.get("title", ""), sn.get("description", ""))
        if not kind:
            continue
        try:
            r = yt.commentThreads().list(part="snippet", videoId=v["id"], maxResults=100, order="time").execute()
        except HttpError as e:
            P.log(f"{v['id']}: comments not readable ({yt_error(e, 120)}); skipped")
            skipped += 1
            continue
        if any(((t["snippet"]["topLevelComment"]["snippet"].get("authorChannelId") or {}).get("value") == me) for t in r.get("items", [])):
            skipped += 1
            continue
        if posted >= limit:
            P.log(f"stopped after {posted} comments (daily API quota); run again tomorrow to continue")
            break
        title = re.sub(r"\s+", " ", sn.get("title", ""))[:50]
        if dry:
            P.log(f"would comment on {v['id']} ({kind}): {title}")
            posted += 1
            continue
        try:
            yt.commentThreads().insert(part="snippet", body={"snippet": {"videoId": v["id"], "topLevelComment": {
                "snippet": {"textOriginal": TEXT[kind]}}}}).execute()
            posted += 1
            P.log(f"commented on {v['id']} ({kind}): {title}")
        except HttpError as e:
            P.log(f"STOPPED, YouTube refused the comment on {v['id']}: {yt_error(e)}")
            break
        time.sleep(4)
    P.log(f"done: {posted} {'would be ' if dry else ''}commented, {skipped} already had a comment of the channel or could not be read")


if __name__ == "__main__":
    main()
