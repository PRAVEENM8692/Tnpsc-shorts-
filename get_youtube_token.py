"""Run ONCE on your own computer to get a YouTube refresh token.

1. pip install google-auth-oauthlib
2. Put the downloaded OAuth "Desktop app" file next to this script as client_secret.json
3. python get_youtube_token.py   (a browser opens; sign in with the channel's Google account)
(Upload + playlist + comment permission are all asked.)
4. Copy the three values it prints into GitHub repo secrets.
"""
import json

from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json", scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.force-ssl"]
)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
info = json.load(open("client_secret.json"))
app = info.get("installed") or info.get("web")
print("\nAdd these as GitHub repository secrets:")
print("YT_CLIENT_ID     =", app["client_id"])
print("YT_CLIENT_SECRET =", app["client_secret"])
print("YT_REFRESH_TOKEN =", creds.refresh_token)
