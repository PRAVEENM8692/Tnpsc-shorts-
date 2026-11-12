"""Read-only: prints views / likes / comments / privacy for every video of the channel (nothing is changed)."""
import os, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
                    client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"])
yt = build("youtube", "v3", credentials=creds)
ch = yt.channels().list(part="contentDetails,statistics", mine=True).execute()["items"][0]
print("channel: subscribers", ch["statistics"].get("subscriberCount"), "videos", ch["statistics"].get("videoCount"),
      "total views", ch["statistics"].get("viewCount"))
pl = ch["contentDetails"]["relatedPlaylists"]["uploads"]
ids, tok = [], None
while True:
    r = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50, pageToken=tok).execute()
    ids += [i["contentDetails"]["videoId"] for i in r["items"]]
    tok = r.get("nextPageToken")
    if not tok:
        break
rows = []
for k in range(0, len(ids), 50):
    r = yt.videos().list(part="snippet,statistics,status,contentDetails", id=",".join(ids[k:k + 50])).execute()
    for v in r["items"]:
        s = v["statistics"]
        rows.append((v["snippet"]["publishedAt"][:16], v["id"], v["status"]["privacyStatus"], v["contentDetails"]["duration"],
                     int(s.get("viewCount", 0)), int(s.get("likeCount", 0)), int(s.get("commentCount", 0)), v["snippet"]["title"][:60]))
rows.sort(reverse=True)
print("published(UTC)\tid\tprivacy\tduration\tviews\tlikes\tcomments\ttitle")
for r in rows:
    print("\t".join(str(x) for x in r))
