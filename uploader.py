"""Step 4: upload to YouTube through the official Data API (OAuth)."""
import base64
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import config

# "youtube" scope (not "youtube.upload") because it also works with the phone-friendly device login.
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def _service():
    # Cloud runs: the token comes from a GitHub secret.
    if os.getenv("TOKEN_B64") and not config.TOKEN_FILE.exists():
        config.TOKEN_FILE.write_bytes(base64.b64decode(os.environ["TOKEN_B64"]))

    creds = None
    if config.TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(config.TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(config.CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)  # laptop only; on a phone use auth_device.py
        try:
            config.TOKEN_FILE.write_text(creds.to_json())
        except OSError:
            pass
    return build("youtube", "v3", credentials=creds)


def upload(video_path, script: dict) -> str:
    hashtags = [("#" + h.lstrip("#").replace(" ", "")) for h in script.get("hashtags", [])][:5]
    if config.SHORTS and "#shorts" not in [h.lower() for h in hashtags]:
        hashtags.append("#Shorts")
    description = f"{script['description']}\n\n{' '.join(hashtags)}\n\nMade with AI voice-over and stock footage."[:4900]

    tags, total = [], 0
    for t in script.get("tags", []):
        if total + len(t) + 1 > 450:
            break
        tags.append(t)
        total += len(t) + 1

    body = {
        "snippet": {
            "title": script["title"][:100],
            "description": description,
            "tags": tags,
            "categoryId": str(script.get("category_id", "22")),
        },
        "status": {
            "privacyStatus": config.PRIVACY,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,  # YouTube's AI/altered-content disclosure
        },
    }
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    req = _service().videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  upload {int(status.progress() * 100)}%")
    return f"https://youtu.be/{resp['id']}"
