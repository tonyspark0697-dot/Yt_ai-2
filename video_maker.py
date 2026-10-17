"""Step 3: voice-over (edge-tts) + stock footage (Pexels) + captions, assembled with moviepy."""
import asyncio
import os
import random
from pathlib import Path

import edge_tts
import requests
from moviepy import (AudioFileClip, ColorClip, CompositeVideoClip, TextClip,
                     VideoFileClip, concatenate_videoclips)
from moviepy.video.fx import Loop

import config

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
FONT = next((f for f in FONT_CANDIDATES if os.path.exists(f)), None)


def _tts(text: str, path: Path):
    asyncio.run(edge_tts.Communicate(text, config.VOICE).save(str(path)))


def _pexels_clip(query: str, path: Path) -> Path | None:
    if not config.PEXELS_API_KEY:
        return None
    try:
        r = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": config.PEXELS_API_KEY},
            params={"query": query, "orientation": "portrait" if config.SHORTS else "landscape",
                    "per_page": 8, "size": "medium"},
            timeout=30,
        )
        r.raise_for_status()
        vids = r.json().get("videos", [])
        if not vids:
            return None
        files = [f for f in random.choice(vids)["video_files"]
                 if f.get("file_type") == "video/mp4" and (f.get("width") or 0) <= 1920]
        if not files:
            return None
        best = max(files, key=lambda f: f.get("width") or 0)
        data = requests.get(best["link"], timeout=120)
        data.raise_for_status()
        path.write_bytes(data.content)
        return path
    except Exception as e:
        print(f"  [pexels] {query!r} failed: {e}")
        return None


def _scene(narration: str, audio_path: Path, bg_path: Path | None):
    W, H = config.WIDTH, config.HEIGHT
    audio = AudioFileClip(str(audio_path))
    dur = audio.duration + 0.3

    if bg_path:
        bg = VideoFileClip(str(bg_path)).without_audio()
        bg = bg.with_effects([Loop(duration=dur)]) if bg.duration < dur else bg.subclipped(0, dur)
        bg = bg.resized(max(W / bg.w, H / bg.h))
        bg = bg.cropped(x_center=bg.w / 2, y_center=bg.h / 2, width=W, height=H)
    else:
        bg = ColorClip((W, H), color=random.choice([(20, 24, 54), (40, 20, 60), (14, 50, 62), (60, 24, 24)]),
                       duration=dur)

    layers = [bg]
    if FONT:
        try:
            cap = TextClip(font=FONT, text=narration, font_size=64 if config.SHORTS else 56,
                           color="white", stroke_color="black", stroke_width=4,
                           method="caption", size=(W - 140, None), text_align="center")
            layers.append(cap.with_duration(dur).with_position(("center", int(H * 0.60))))
        except Exception as e:
            print(f"  [caption] skipped: {e}")
    return CompositeVideoClip(layers, size=(W, H)).with_duration(dur).with_audio(audio)


def build_video(script: dict, workdir: Path) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)
    clips = []
    for i, sc in enumerate(script["scenes"]):
        print(f"  scene {i + 1}/{len(script['scenes'])}")
        a = workdir / f"s{i}.mp3"
        _tts(sc["narration"], a)
        bg = _pexels_clip(sc.get("visual_query", script["topic"]), workdir / f"s{i}.mp4")
        clips.append(_scene(sc["narration"], a, bg))
    final = concatenate_videoclips(clips, method="compose")
    out = workdir / "final.mp4"
    final.write_videofile(str(out), fps=30, codec="libx264", audio_codec="aac", logger=None)
    for c in clips:
        c.close()
    return out
