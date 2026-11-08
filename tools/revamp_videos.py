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


def auto_thumbnails(yt, videos):
    """Sets the new vertical thumbnail on EVERY video of the channel, a few per run. YouTube limits custom thumbnails (HTTP 429
    after about 9), so this stops at the first refusal and continues in the next run. Progress is kept in thumbs_done.json."""
    import json
    from shorts_helpers import clean_title

    state = Path("thumbs_done.json")
    try:
        done = set(json.loads(state.read_text(encoding="utf-8")).get("ids", []))
    except Exception:
        done = set()
    limit = int(os.environ.get("THUMB_MAX") or 9)
    todo = [v for v in videos if v["id"] not in done]   # videos come newest first: the newest videos get their thumbnail first
    P.log(f"thumbnails: {len(done)} done, {len(todo)} left; setting up to {limit} now")
    tmp = Path(tempfile.mkdtemp())
    ok = 0
    for v in todo:
        if ok >= limit:
            break
        sn = v["snippet"]
        kind = kind_of(sn.get("title", ""), sn.get("description", "")) or "news"
        text = re.sub(r"#\w+|^[^\w\u0B80-\u0BFF]+", "", seo_meta.clean(sn.get("title", ""))).strip()
        text = clean_title(text, 70) or text
        try:
            img = seo_meta.make_thumbnail(text, kind, tmp / f"{v['id']}.jpg")
        except Exception as e:
            P.log(f"thumbnail not made for {v['id']}: {str(e)[:100]}")
            continue
        if seo_meta.set_thumbnail(yt, v["id"], img):
            ok += 1
            done.add(v["id"])
            state.write_text(json.dumps({"ids": sorted(done)}, indent=0), encoding="utf-8")
        elif getattr(seo_meta.set_thumbnail, "blocked", False):
            P.log("YouTube is limiting thumbnails right now; the rest continues in the next run")
            break
    P.log(f"thumbnails set in this run: {ok}; left for later runs: {len([v for v in videos if v['id'] not in done])}")


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

    if (os.environ.get("THUMB_AUTO") or "0") == "1":
        auto_thumbnails(yt, videos)
        return

    only = [x.strip() for x in (os.environ.get("THUMB_IDS") or "").split(",") if x.strip()]
    if only:   # thumbnails only, for videos whose description is already new
        tmp = Path(tempfile.mkdtemp())
        by_id = {v["id"]: v for v in videos}
        ok = 0
        for vid in only:
            v = by_id.get(vid)
            if not v:
                continue
            sn = v["snippet"]
            kind = kind_of(sn.get("title", ""), sn.get("description", ""))
            try:
                img = seo_meta.make_thumbnail(re.sub(r"#\w+|^[^\w஀-௿]+", "", seo_meta.clean(sn["title"])).strip(),
                                              kind or "news", tmp / f"{vid}.jpg")
            except Exception as e:
                P.log(f"thumbnail not made for {vid}: {str(e)[:100]}")
                continue
            if seo_meta.set_thumbnail(yt, vid, img):
                ok += 1
            elif getattr(seo_meta.set_thumbnail, "blocked", False):
                P.log("YouTube is limiting thumbnails; stopping. Remaining ids: " + ",".join(only[only.index(vid):]))
                break
        P.log(f"thumbnails set: {ok} of {len(only)}")
        return

    done = skipped = 0
    thumbs_ok = True
    pending = []
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
                if pending:
                    P.log("THUMB_PENDING " + ",".join(pending))
                return
            title, desc = new
            P.log(f"{'(dry run) ' if dry else ''}{sn.get('title', '')[:40]!r} -> {title[:50]!r}")
            if not dry:
                body = {"id": v["id"], "snippet": {
                    "title": title[:100], "description": desc, "categoryId": sn.get("categoryId", "27"),
                    "tags": seo_meta.make_tags(sn.get("tags") or [], kind),
                    "defaultLanguage": sn.get("defaultLanguage", "ta")}}
                yt.videos().update(part="snippet", body=body).execute()
                if with_thumbs and not thumbs_ok:
                    pending.append(v["id"])
                elif with_thumbs:
                    try:
                        img = seo_meta.make_thumbnail(re.sub(r"#\w+|^[^\w஀-௿]+", "", seo_meta.clean(sn["title"])).strip(),
                                                      kind, tmp / f"{v['id']}.jpg")
                        if not seo_meta.set_thumbnail(yt, v["id"], img):
                            pending.append(v["id"])
                            if getattr(seo_meta.set_thumbnail, "blocked", False):
                                thumbs_ok = False
                    except Exception as e:
                        P.log(f"thumbnail skipped: {str(e)[:120]}")
            done += 1
    except HttpError as e:
        if e.resp.status in (401, 403):
            sys.exit("YouTube refused (login has no permission, or the daily quota is used up). Run again tomorrow. "
                     f"Details: {str(e)[:220]}")
        raise
    if pending:
        P.log("THUMB_PENDING " + ",".join(pending))
    P.log(f"done: {done} changed, {skipped} left alone (already new format or not recognised). "
          "If nothing was changed, all videos are done.")


if __name__ == "__main__":
    main()
