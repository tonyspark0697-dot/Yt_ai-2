# Auto Tube: YouTube automation you control from your phone

**How it works:** GitHub Actions (free cloud computer) does the heavy work. Your phone only taps a button.

```
Phone app (docs/)  ->  GitHub Actions  ->  trends -> Claude script -> voice + footage -> YouTube upload
   (button, status)      (also runs daily by itself at 9:00 AM IST)
```

## One-time setup (all doable from a phone browser)

### 1. Get the code into GitHub
Create a free GitHub account, create a **new repository** (public is fine; your keys stay in secrets), unzip this project and upload all files, including the hidden `.github` folder. (Easier: open github.com in "Desktop site" mode in your browser and use *Add file -> Upload files*.)

### 2. Get your keys
| Key | Where |
|---|---|
| `YOUTUBE_API_KEY` | console.cloud.google.com -> new project -> enable **YouTube Data API v3** -> Credentials -> API key |
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `PEXELS_API_KEY` | pexels.com/api (free, stock footage) |

### 3. Log in to YouTube from your phone
1. In the same Google Cloud project: Credentials -> **Create OAuth client ID** -> type **"TVs and Limited Input devices"**. Note the client ID and secret.
2. OAuth consent screen: set audience to **External** and publishing status to **In production**. (If it stays on "Testing", Google expires your login after 7 days.) The "unverified app" warning is normal for your own use.
3. Run `python auth_device.py` somewhere with Python, e.g. a free **GitHub Codespace** (green *Code* button -> Codespaces) or Google Colab. Enter the client ID and secret, open google.com/device on your phone, type the code, and approve.
4. It prints a long text called **TOKEN_B64**. Copy it.

### 4. Add the secrets to GitHub
Repo -> Settings -> Secrets and variables -> Actions -> **New repository secret**. Add these four:
`YOUTUBE_API_KEY`, `ANTHROPIC_API_KEY`, `PEXELS_API_KEY`, `TOKEN_B64`.

Optional *Variables* (same page, Variables tab): `REGION` (IN), `LANGUAGE`, `VOICE`, `NICHE_HINT`, `SHORTS` (true/false), `PRIVACY`.

### 5. Turn on the phone app
1. Repo -> Settings -> **Pages** -> Source: *Deploy from a branch* -> Branch `main`, folder **/docs** -> Save.
2. After a minute your app is at `https://YOURNAME.github.io/REPONAME/`. Open it on your phone and use **Add to Home Screen** (Chrome menu -> *Install app*).
3. Create a token: GitHub -> Settings -> Developer settings -> Fine-grained tokens -> select **only this repo**, permissions **Actions: read and write**, **Contents: read**.
4. In the app, open *Connection settings*, enter `yourname/reponame` and the token, tap Save.

### 6. First test
In the app turn on **Test only**, tap **Create & upload now**. After about 5 to 10 minutes the run turns green. Open it and download the `video` artifact to check quality. Then turn the switch off and run a real one.

## Using it
- **Create & upload now:** one video on demand. Niche and visibility are set right in the app.
- **Daily auto-run:** edit the `cron` line in `.github/workflows/upload.yml` (or delete the schedule to stop it).
- **Recent runs / Uploaded videos:** live status and links to your videos.

## Good to know
- **Uploads start private.** New Google API projects are locked to private uploads until they pass YouTube's API audit. Until then, switch videos to public in YouTube Studio.
- **Upload quota:** about 6 uploads per day on the default quota.
- **Free limits:** GitHub gives 2,000 Actions minutes per month on private repos (public repos are unlimited). One video takes roughly 5 to 10 minutes. Note GitHub pauses scheduled runs in a public repo after 60 days without activity; each upload commits a history file, which keeps it active.
- **Monetization:** fully automated, repetitive videos can be treated as "mass-produced" by YouTube. Pick a niche, review the first videos, keep facts accurate. Uploads are tagged with YouTube's AI-content disclosure.
- Keep your token and secrets private. Anyone with `TOKEN_B64` can post to your channel.

## Run on a laptop instead
`pip install -r requirements.txt`, copy `.env.example` to `.env`, then `python main.py --dry-run`.

## Files
`main.py` pipeline - `trends.py` viral hashtag finder - `script_gen.py` Claude script - `video_maker.py` voice, footage, captions - `uploader.py` YouTube upload - `auth_device.py` phone login - `docs/` phone app - `.github/workflows/upload.yml` cloud runner
