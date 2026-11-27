"""Sets the owner-chosen thumbnails (made in ChatGPT) on already-uploaded Long videos: every tools/story/thumbs/<videoId>.jpg goes to that video."""
import os, sys
from pathlib import Path
sys.path.insert(0, ".")
import pipeline as P
import seo_meta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
yt = build("youtube", "v3", credentials=Credentials(None, refresh_token=P.env("YT_REFRESH_TOKEN"), token_uri="https://oauth2.googleapis.com/token",
           client_id=P.env("YT_CLIENT_ID"), client_secret=P.env("YT_CLIENT_SECRET"), scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]))
for f in sorted(Path("tools/story/thumbs").glob("*.jpg")):
    P.log(f"thumbnail on {f.stem}: {seo_meta.set_thumbnail(yt, f.stem, f)}")
