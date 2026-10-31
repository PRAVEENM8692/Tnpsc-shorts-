# Free daily TNPSC Tamil Shorts (GitHub Actions)

Every day at 8 PM IST: news search -> Tamil script with a memory trick -> Tamil voice -> images
-> zoom/pan video with BGM -> YouTube upload. No paid services.

## 1. Create the repo
Create a new GitHub repo (public repos get unlimited Actions minutes). Upload everything in this folder,
keeping the `.github/workflows/daily.yml` path. Add a royalty-free motivational track as `assets/bgm.mp3`
(YouTube Audio Library or Pixabay Music).

## 2. Free API keys
- Tavily (tavily.com): news search key. Free credits each month
- Groq (console.groq.com): LLM key. Free tier with rate limits

## 3. YouTube upload access (one-time)
1. console.cloud.google.com -> new project -> enable "YouTube Data API v3"
2. OAuth consent screen: External. Add yourself as a test user, then click "Publish app"
   (in Testing mode the refresh token expires after 7 days, so publish it; the unverified-app warning
   is fine for your own channel)
3. Credentials -> Create OAuth client ID -> Desktop app -> download JSON as `client_secret.json`
4. On your computer: `pip install google-auth-oauthlib` then `python get_youtube_token.py`
5. Sign in with the channel's Google account. It prints three values

## 4. GitHub secrets and variables (repo Settings -> Secrets and variables -> Actions)
Secrets: `TAVILY_API_KEY`, `LLM_API_KEY`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
Variables (optional): `LLM_MODEL` (default llama-3.3-70b-versatile; change it if Groq retires it),
`LLM_BASE_URL`, `TTS_VOICE` (ta-IN-PallaviNeural or ta-IN-ValluvarNeural), `YT_PRIVACY` (private/unlisted/public)

## 5. First test
Actions tab -> daily-tnpsc-short -> Run workflow, keep upload = false. Open the run, download the
artifact, watch the video and read `script-*.json`. When happy, run once with upload = true.

## Good to know
- YouTube locks uploads from unaudited API projects to PRIVATE. Either publish each video from YouTube
  Studio (one click) or apply for the YouTube API compliance audit to unlock public uploads.
- Pollinations (images) and edge-tts (voice) are free but unofficial and can be slow or change; if an image
  fails, the script uses a plain colour background so the run still finishes.
- GitHub may delay scheduled runs by up to about half an hour, and pauses schedules in repos with no
  activity for 60 days (run the workflow manually to restart).
- Facts come from the day's news search. Read each video's script for the first week before trusting it.
- Videos are marked as containing synthetic media, as YouTube requires for AI-generated content.
