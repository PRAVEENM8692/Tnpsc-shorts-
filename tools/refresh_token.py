"""Gets a new YouTube login token with playlist permission, without a computer (everything runs in GitHub Actions).

Step 1 (no input): prints the Google consent link.      Step 2 (input = the address you were sent to): swaps it for a
refresh token and stores it straight into the YT_REFRESH_TOKEN secret (needs the ADMIN_PAT secret). The token is never printed.
"""
import os
import subprocess
import sys
import urllib.parse

import requests

REDIRECT = "http://localhost:8080"
SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube"


def consent_link(client_id):
    q = urllib.parse.urlencode({"client_id": client_id, "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPES,
                                "access_type": "offline", "prompt": "consent"})
    # GitHub hides secret values in logs; writing the dots as %2E keeps the link working (Google decodes it) and visible
    return "https://accounts.google.com/o/oauth2/v2/auth?" + q.replace(".", "%2E")


def main():
    cid, secret = os.environ["YT_CLIENT_ID"], os.environ["YT_CLIENT_SECRET"]
    given = (os.environ.get("REDIRECT_URL") or "").strip()
    if not given:
        link = consent_link(cid)
        print("\nSTEP 1 - open this link on your phone, sign in with the CHANNEL account and press Allow.")
        print("The page that opens afterwards will say it cannot be reached - that is expected. Copy the full address of that page")
        print("(it starts with http://localhost:8080/?code=...) and run this workflow again, pasting it into 'redirect_url'.\n")
        print(link + "\n")
        with open(os.environ.get("GITHUB_STEP_SUMMARY", os.devnull), "a", encoding="utf-8") as f:
            f.write(f"### Step 1\n[Open this Google link]({link})\n\nSign in with the channel account, press **Allow**, then copy the address of "
                    "the page that fails to load and run this workflow again with it in *redirect_url*.\n")
        return
    code = urllib.parse.parse_qs(urllib.parse.urlparse(given).query).get("code", [""])[0] or (given if "/" not in given and len(given) > 20 else "")
    if not code:
        sys.exit("No code found: paste the whole address that starts with http://localhost:8080/?code=")
    r = requests.post("https://oauth2.googleapis.com/token", data={"code": code, "client_id": cid, "client_secret": secret,
                      "redirect_uri": REDIRECT, "grant_type": "authorization_code"}, timeout=60)
    if r.status_code != 200:
        sys.exit(f"Google refused the code (it can be used only once and expires fast - start again from step 1): {r.text[:200]}")
    d = r.json()
    token = d.get("refresh_token")
    if not token:
        sys.exit("Google gave no refresh token: start again from step 1 and make sure you press Allow on the consent screen.")
    if "https://www.googleapis.com/auth/youtube" not in d.get("scope", "").split():
        sys.exit(f"The playlist permission was not granted (granted: {d.get('scope')}). Tick every box on the consent screen.")
    print(f"::add-mask::{token}")
    p = subprocess.run(["gh", "secret", "set", "YT_REFRESH_TOKEN", "--repo", os.environ["GITHUB_REPOSITORY"]],
                       input=token, text=True, capture_output=True)
    if p.returncode:
        sys.exit("Could not store the secret (is the ADMIN_PAT secret set, with 'Secrets: read and write' on this repo?): " + p.stderr[:200])
    print("DONE: YT_REFRESH_TOKEN was replaced with the new token (upload + playlist permission). Now run add-existing-videos-to-playlists.")


if __name__ == "__main__":
    main()
