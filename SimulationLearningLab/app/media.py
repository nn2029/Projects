from __future__ import annotations

import json
import math
import mimetypes
import shutil
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from PIL import Image

SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
SUPPORTED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm", "video/x-matroska"}
MAX_UPLOAD_BYTES = 500 * 1024 * 1024


@dataclass
class MediaItem:
    id: str
    kind: str
    original_name: str
    stored_name: str
    mime_type: str
    size_bytes: int
    width: int | None = None
    height: int | None = None
    duration_seconds: float | None = None
    frame_count: int | None = None
    fps: float | None = None
    keyframes: list[dict] | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def _run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return proc.stdout


def _safe_suffix(name: str) -> str:
    suffix = Path(name).suffix.lower()
    return suffix if suffix and len(suffix) <= 10 else ""


def _probe_video(path: Path) -> dict:
    raw = _run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_streams", "-show_format", str(path)
    ])
    data = json.loads(raw)
    video_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    duration = video_stream.get("duration") or data.get("format", {}).get("duration")
    duration_f = float(duration) if duration else 0.0
    rate = video_stream.get("avg_frame_rate") or "0/1"
    try:
        num, den = rate.split("/")
        fps = float(num) / float(den) if float(den) else 0.0
    except Exception:
        fps = 0.0
    frame_count = video_stream.get("nb_frames")
    if frame_count is None and duration_f and fps:
        frame_count = int(round(duration_f * fps))
    else:
        frame_count = int(frame_count) if frame_count else None
    return {
        "width": int(video_stream.get("width")) if video_stream.get("width") else None,
        "height": int(video_stream.get("height")) if video_stream.get("height") else None,
        "duration_seconds": duration_f,
        "fps": fps or None,
        "frame_count": frame_count,
    }


def _timestamp_label(seconds: float) -> str:
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def extract_keyframes(video_path: Path, output_dir: Path, max_frames: int = 10) -> list[dict]:
    """Extract evenly spaced representative frames.

    This deliberately uses deterministic sampling instead of pretending to infer semantic
    scene importance. A model/agent may later re-rank or request denser extraction.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    meta = _probe_video(video_path)
    duration = max(float(meta.get("duration_seconds") or 0), 0.0)
    if duration <= 0:
        return []

    count = min(max_frames, max(1, int(math.ceil(duration / 12.0))))
    if count == 1:
        timestamps = [duration / 2]
    else:
        margin = min(0.5, duration * 0.02)
        start = margin
        end = max(start, duration - margin)
        timestamps = [start + (end - start) * i / (count - 1) for i in range(count)]

    frames: list[dict] = []
    for index, ts in enumerate(timestamps, start=1):
        out = output_dir / f"frame-{index:02d}.jpg"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{ts:.3f}", "-i", str(video_path), "-frames:v", "1",
            "-vf", "scale='min(1280,iw)':-2", "-q:v", "3", str(out)
        ], check=True)
        frames.append({
            "index": index,
            "timestamp_seconds": round(ts, 3),
            "timestamp": _timestamp_label(ts),
            "file": out.name,
        })
    return frames


def inspect_saved_media(path: Path, original_name: str, mime_type: str, session_dir: Path) -> MediaItem:
    stat = path.stat()
    media_id = path.stem
    if mime_type in SUPPORTED_IMAGE_TYPES:
        with Image.open(path) as im:
            width, height = im.size
        return MediaItem(
            id=media_id,
            kind="image",
            original_name=original_name,
            stored_name=path.name,
            mime_type=mime_type,
            size_bytes=stat.st_size,
            width=width,
            height=height,
        )
    if mime_type in SUPPORTED_VIDEO_TYPES:
        meta = _probe_video(path)
        keyframe_dir = session_dir / "keyframes" / media_id
        frames = extract_keyframes(path, keyframe_dir)
        for frame in frames:
            frame["relative_path"] = f"keyframes/{media_id}/{frame['file']}"
        return MediaItem(
            id=media_id,
            kind="video",
            original_name=original_name,
            stored_name=path.name,
            mime_type=mime_type,
            size_bytes=stat.st_size,
            keyframes=frames,
            **meta,
        )
    raise ValueError(f"Unsupported media type: {mime_type}")


def save_upload_stream(stream, original_name: str, content_type: str | None, uploads_dir: Path) -> tuple[Path, str]:
    uploads_dir.mkdir(parents=True, exist_ok=True)
    guessed = content_type or mimetypes.guess_type(original_name)[0] or "application/octet-stream"
    if guessed not in SUPPORTED_IMAGE_TYPES | SUPPORTED_VIDEO_TYPES:
        raise ValueError(f"Unsupported file type: {guessed}")
    filename = f"{uuid4().hex}{_safe_suffix(original_name)}"
    target = uploads_dir / filename
    size = 0
    with target.open("wb") as out:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                out.close()
                target.unlink(missing_ok=True)
                raise ValueError("Upload exceeds 500 MB limit")
            out.write(chunk)
    return target, guessed
