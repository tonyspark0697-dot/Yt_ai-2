import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE = Path(__file__).parent
OUT_DIR = BASE / "output"
OUT_DIR.mkdir(exist_ok=True)
HISTORY_FILE = BASE / "history.json"
CLIENT_SECRET = BASE / "client_secret.json"   # OAuth file from Google Cloud
TOKEN_FILE = BASE / "token.json"              # created after first login

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

REGION = os.getenv("REGION", "IN")
LANGUAGE = os.getenv("LANGUAGE", "English")
VOICE = os.getenv("VOICE", "en-IN-NeerjaNeural")
NICHE_HINT = os.getenv("NICHE_HINT", "").strip()
SHORTS = os.getenv("SHORTS", "true").lower() == "true"
PRIVACY = os.getenv("PRIVACY", "private")
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

WIDTH, HEIGHT = (1080, 1920) if SHORTS else (1920, 1080)
