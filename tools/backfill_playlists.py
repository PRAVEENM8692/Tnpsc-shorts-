"""Puts the videos that are already on the channel into their playlists (same rules as new uploads).

Safe to run again and again: a video that is already in a playlist is skipped. YouTube's daily API quota limits how many
can be added per run (each add costs 50 units), so run it once a day until it says "all videos are in their playlists".
Needs the YT_* secrets with the playlist permission (run get_youtube_token.py again).
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pipeline as P  # noqa: E402

APT_KEYS = {   # words in a title / description -> aptitude topic
    "Percentage shortcuts": ("percentage", "சதவீதம்"), "Ratio and proportion": ("ratio", "விகிதம்"),
    "Time and work": ("time and work", "வேலை"), "Speed, time and distance": ("speed", "வேகம்"),
    "Simple interest": ("simple interest", "தனி வட்டி"), "Compound interest shortcut": ("compound", "கூட்டு வட்டி"),
    "Average": ("average", "சராசரி"), "Profit and loss": ("profit", "இலாபம்", "லாபம்"), "HCF and LCM": ("hcf", "lcm", "மீ.பொ"),
    "Ages problems": ("ages", "வயது"), "Number series": ("series", "தொடர்"), "Square and cube tricks": ("square", "cube", "வர்க்க", "கனம்"),
    "Mixtures and alligation": ("mixture", "alligation", "கலவை"), "Pipes and cisterns": ("pipe", "cistern", "குழாய்"),
    "Trains problems": ("train", "ரயில்"), "Boats and streams": ("boat", "stream", "படகு"),
    "Mensuration (area, perimeter)": ("mensuration", "area", "பரப்பளவு"), "Divisibility rules": ("divisib", "வகுபடு"),
    "Simplification (BODMAS tricks)": ("bodmas", "simplification", "சுருக்க"), "Calendar and clock problems": ("calendar", "clock", "நாட்காட்டி", "கடிகார"),
}
WORLD = ("isro", "இஸ்ரோ", "விளையாட்டு", "sport", "cricket", "உலக", "சர்வதேச", "ஐ.நா", "science", "அறிவியல்", "olympic", "nasa", "world")


def classify(title, desc):
    """Playlist names for an existing video, from its title and description."""
    text = f"{title}\n{desc}"
    low = text.lower()
    m = re.search(r"Topic:\s*([^:\n]+):", desc)
    if m:   # a syllabus lesson: 'Topic: Subject: topic'
        return P.playlists_for("lesson", 0, m.group(1).strip() + ": x", "")
    if "#aptitude" in low or "mathstricks" in low or "aptitude" in low:
        topic = next((t for t, keys in APT_KEYS.items() if any(k in low for k in keys)), "")
        return P.playlists_for("aptitude", 0, "", topic)
    if "sources:" in low or "#currentaffairs" in low:
        slot = 1 if ("தமிழ்நாடு" in text or "tamil nadu" in low) else (4 if any(w in low for w in WORLD) else 2)
        return P.playlists_for("news", slot, "", "")
    return []


def main():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    limit = int(os.environ.get("MAX_ADDS") or 90)   # inserts per run (50 quota units each)
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

    mine, token = {}, None
    while True:
        r = yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=token).execute()
        mine.update({it["snippet"]["title"]: it["id"] for it in r.get("items", [])})
        token = r.get("nextPageToken")
        if not token:
            break
    members = {}   # playlist title -> set of video ids already inside

    def inside(name):
        if name not in members:
            members[name] = set()
            if name in mine:
                tk = None
                while True:
                    r = yt.playlistItems().list(part="contentDetails", playlistId=mine[name], maxResults=50, pageToken=tk).execute()
                    members[name] |= {it["contentDetails"]["videoId"] for it in r.get("items", [])}
                    tk = r.get("nextPageToken")
                    if not tk:
                        break
        return members[name]

    adds = skipped = 0
    try:
        for v in reversed(videos):   # oldest first
            names = classify(v["snippet"].get("title", ""), v["snippet"].get("description", ""))
            if not names:
                skipped += 1
                continue
            for name in names:
                if v["id"] in inside(name):
                    continue
                if adds >= limit:
                    P.log(f"stopped after {adds} additions (daily API quota); run again tomorrow to continue")
                    return
                if name not in mine:
                    mine[name] = yt.playlists().insert(part="snippet,status", body={
                        "snippet": {"title": name[:150], "description": "TNPSC Group 1, 2, 4 - தமிழில் தினசரி Shorts", "defaultLanguage": "ta"},
                        "status": {"privacyStatus": "public"}}).execute()["id"]
                    members[name] = set()
                    P.log(f"playlist created: {name}")
                yt.playlistItems().insert(part="snippet", body={"snippet": {
                    "playlistId": mine[name], "resourceId": {"kind": "youtube#video", "videoId": v["id"]}}}).execute()
                members[name].add(v["id"])
                adds += 1
                P.log(f"added '{v['snippet']['title'][:40]}' -> {name}")
    except HttpError as e:
        if e.resp.status in (401, 403):
            sys.exit("The YouTube login has no playlist permission (or the daily quota is used up): run get_youtube_token.py again "
                     f"and replace the YT_REFRESH_TOKEN secret. Details: {str(e)[:200]}")
        raise
    P.log(f"done: {adds} added, {skipped} videos not recognised (left alone). If this said nothing was added, all videos are in their playlists.")


if __name__ == "__main__":
    main()
