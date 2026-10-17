"""Full pipeline: trends -> script -> video -> upload.

python main.py --dry-run          # make the video, do not upload
python main.py                    # make + upload one video
python main.py --loop 24          # one video every 24 hours
python main.py --niche "space facts" --privacy unlisted
"""
import argparse
import json
import os
import time
import traceback
from datetime import datetime, timezone

import config
import script_gen
import trends
import uploader
import video_maker

UPLOADS_FILE = config.BASE / "uploads.json"


def _load(path) -> list:
    return json.loads(path.read_text()) if path.exists() else []


def run_once(dry_run: bool):
    print("1/4 Reading YouTube trends...")
    report = trends.get_trend_report()
    print("   hashtags:", report["top_hashtags"][:8])

    print("2/4 Writing script with Claude...")
    hist = _load(config.HISTORY_FILE)
    script = script_gen.generate(report, hist)
    print("   title:", script["title"])

    print("3/4 Building video...")
    workdir = config.OUT_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
    video = video_maker.build_video(script, workdir)
    (workdir / "script.json").write_text(json.dumps(script, indent=2, ensure_ascii=False))
    print("   saved:", video)

    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if dry_run:
        print("4/4 Dry run: skipping upload.")
        if summary:
            with open(summary, "a") as f:
                f.write(f"### Dry run\n**{script['title']}**\n\nVideo is in the *video* artifact below.\n")
        return

    print("4/4 Uploading...")
    url = uploader.upload(video, script)
    config.HISTORY_FILE.write_text(json.dumps(hist + [script["topic"]], indent=2, ensure_ascii=False))
    log = _load(UPLOADS_FILE)
    log.insert(0, {"title": script["title"], "url": url, "privacy": config.PRIVACY,
                   "time": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    UPLOADS_FILE.write_text(json.dumps(log[:100], indent=2, ensure_ascii=False))
    print("   LIVE:", url)
    if summary:
        with open(summary, "a") as f:
            f.write(f"### Uploaded\n**{script['title']}**\n\n{url} ({config.PRIVACY})\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--loop", type=float, metavar="HOURS", help="repeat every N hours")
    ap.add_argument("--niche", help="override NICHE_HINT")
    ap.add_argument("--privacy", choices=["private", "unlisted", "public"], help="override PRIVACY")
    args = ap.parse_args()
    if args.niche is not None:
        config.NICHE_HINT = args.niche
    if args.privacy:
        config.PRIVACY = args.privacy

    while True:
        try:
            run_once(args.dry_run)
        except Exception:
            traceback.print_exc()
            if not args.loop:
                raise SystemExit(1)
        if not args.loop:
            break
        time.sleep(args.loop * 3600)
