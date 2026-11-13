"""Uploads assets/banner.png (2560x1440) as the YouTube channel banner. Everything else in the channel branding is kept.
DRY_RUN=1 (default) only checks the file."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline as P  # noqa: E402


def main():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    f = Path("assets/banner.png")
    P.log(f"banner file: {f} {f.stat().st_size // 1024} KB")
    if (os.environ.get("DRY_RUN") or "1") != "0":
        P.log("dry run: nothing changed")
        return
    creds = Credentials(None, refresh_token=P.env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
                        client_id=P.env("YT_CLIENT_ID"), client_secret=P.env("YT_CLIENT_SECRET"))
    yt = build("youtube", "v3", credentials=creds)
    try:
        url = yt.channelBanners().insert(media_body=MediaFileUpload(str(f), mimetype="image/png")).execute()["url"]
        ch = yt.channels().list(part="id,brandingSettings", mine=True).execute()["items"][0]
        bs = ch.get("brandingSettings") or {}
        bs.setdefault("image", {})["bannerExternalUrl"] = url
        yt.channels().update(part="brandingSettings", body={"id": ch["id"], "brandingSettings": bs}).execute()
        P.log("channel banner updated")
    except HttpError as e:
        sys.exit(f"YouTube refused ({e.resp.status}): {str(e)[:300]}")


if __name__ == "__main__":
    main()
