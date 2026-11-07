"""Gives the videos that are already on the channel the new engagement-focused title and description
(hook line, key points, comment / subscribe / share call, keywords, hashtags) and, if asked, a thumbnail.

Safe to run again and again: a video whose description already has the new format is skipped.
YouTube quota: every change costs 50 units (daily quota 10,000, uploads use most of it), so MAX_UPDATES is small by
default. Run it in the evening after the day's videos and repeat on the next days until it says "all videos are done".
"""
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline as P  # noqa: E402
import seo_meta  # noqa: E402
from backfill_playlists import WORLD  # noqa: E402


def kind_of(title, desc):
    low = f"{title}\n{desc}".lower()
    if re.search(r"Topic:\s*([^:\n]+):", desc or ""):
        return "lesson"
    if "aptitude" in low or "mathstricks" in low:
        return "aptitude"
    if "sources:" in low or "#currentaffairs" in low:
        return "news"
    return ""


def main():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    limit = int(os.environ.get("MAX_UPDATES") or 40)
    with_thumbs = (os.environ.get("WITH_THUMBNAILS") or "0") == "1"
    dry = (os.environ.get("DRY_RUN") or "0") == "1"
    creds = Credentials(None, refresh_token=P.env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
                        client_id=P.env("YT_CLIENT_ID"), client_secret=P.env("YT_CLIENT_SECRET"))
    yt = build("youtube", "v3", credentials=creds)

    uploads = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
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

    done = skipped = 0
    tmp = Path(tempfile.mkdtemp())
    try:
        for v in reversed(videos):   # oldest first
            sn = v["snippet"]
            kind = kind_of(sn.get("title", ""), sn.get("description", ""))
            new = seo_meta.revamp_existing(kind, sn.get("title", ""), sn.get("description", "")) if kind else None
            if not new:
                skipped += 1
                continue
            if done >= limit:
                P.log(f"stopped after {done} videos (daily API quota); run again tomorrow to continue")
                return
            title, desc = new
            P.log(f"{'(dry run) ' if dry else ''}{sn.get('title', '')[:40]!r} -> {title[:50]!r}")
            if not dry:
                body = {"id": v["id"], "snippet": {
                    "title": title[:100], "description": desc, "categoryId": sn.get("categoryId", "27"),
                    "tags": seo_meta.make_tags(sn.get("tags") or [], kind),
                    "defaultLanguage": sn.get("defaultLanguage", "ta")}}
                yt.videos().update(part="snippet", body=body).execute()
                if with_thumbs:
                    try:
                        img = seo_meta.make_thumbnail(re.sub(r"#\w+|^[^\w஀-௿]+", "", seo_meta.clean(sn["title"])).strip(),
                                                      kind, tmp / f"{v['id']}.jpg")
                        seo_meta.set_thumbnail(yt, v["id"], img)
                    except Exception as e:
                        P.log(f"thumbnail skipped: {str(e)[:120]}")
            done += 1
    except HttpError as e:
        if e.resp.status in (401, 403):
            sys.exit("YouTube refused (login has no permission, or the daily quota is used up). Run again tomorrow. "
                     f"Details: {str(e)[:220]}")
        raise
    P.log(f"done: {done} changed, {skipped} left alone (already new format or not recognised). "
          "If nothing was changed, all videos are done.")


if __name__ == "__main__":
    main()
