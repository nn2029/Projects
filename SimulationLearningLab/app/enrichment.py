from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def _command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def ocr_image(path: Path, language: str = "eng") -> dict:
    """Run local OCR when tesseract is installed.

    OCR output is explicitly treated as extracted text, not semantic truth.
    """
    if not _command_exists("tesseract"):
        return {"status": "unavailable", "provider": "tesseract", "text": "", "reason": "tesseract not installed"}
    proc = subprocess.run(
        ["tesseract", str(path), "stdout", "-l", language, "--psm", "6"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return {"status": "error", "provider": "tesseract", "text": "", "reason": proc.stderr.strip()}
    text = proc.stdout.strip()
    return {"status": "completed", "provider": "tesseract", "text": text}


def extract_audio(video_path: Path, out_path: Path) -> Path:
    if not _command_exists("ffmpeg"):
        raise RuntimeError("ffmpeg is required to extract video audio")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(video_path), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "wav", str(out_path),
        ],
        check=True,
    )
    return out_path


def transcribe_video(video_path: Path, session_dir: Path) -> dict:
    """Transcribe video audio.

    Provider order:
    1. OpenAI transcription when OPENAI_API_KEY and the official SDK are available.
    2. Local `whisper` CLI when available.
    3. Return a capability status without failing the session.
    """
    transcript_dir = session_dir / "transcripts"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    audio_path = transcript_dir / f"{video_path.stem}.wav"
    try:
        extract_audio(video_path, audio_path)
    except Exception as exc:
        return {"status": "error", "provider": None, "text": "", "reason": str(exc)}

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=api_key)
            model = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")
            with audio_path.open("rb") as fh:
                result = client.audio.transcriptions.create(model=model, file=fh)
            text = getattr(result, "text", "") or ""
            payload = {
                "status": "completed",
                "provider": "openai",
                "model": model,
                "text": text.strip(),
            }
            (transcript_dir / f"{video_path.stem}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return payload
        except Exception as exc:
            openai_error = str(exc)
    else:
        openai_error = "OPENAI_API_KEY not configured"

    if _command_exists("whisper"):
        try:
            with tempfile.TemporaryDirectory() as temp:
                subprocess.run(
                    [
                        "whisper", str(audio_path), "--output_dir", temp,
                        "--output_format", "txt", "--model", os.getenv("SLL_WHISPER_MODEL", "base"),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                candidates = list(Path(temp).glob("*.txt"))
                text = candidates[0].read_text(encoding="utf-8").strip() if candidates else ""
            payload = {"status": "completed", "provider": "whisper-cli", "text": text}
            (transcript_dir / f"{video_path.stem}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return payload
        except Exception as exc:
            return {"status": "error", "provider": "whisper-cli", "text": "", "reason": str(exc)}

    return {
        "status": "unavailable",
        "provider": None,
        "text": "",
        "reason": f"No transcription provider available. OpenAI: {openai_error}",
    }


def enrich_manifest(session_dir: Path, manifest: dict, *, ocr: bool = True, transcribe: bool = True) -> dict:
    for item in manifest.get("media", []):
        source = session_dir / "uploads" / item["stored_name"]
        if item.get("kind") == "image" and ocr:
            item["ocr"] = ocr_image(source)
        elif item.get("kind") == "video":
            if ocr:
                frame_results = []
                for frame in item.get("keyframes") or []:
                    frame_path = session_dir / frame["relative_path"]
                    result = ocr_image(frame_path)
                    frame_results.append({
                        "timestamp": frame.get("timestamp"),
                        "relative_path": frame.get("relative_path"),
                        **result,
                    })
                item["frame_ocr"] = frame_results
            if transcribe:
                item["transcript"] = transcribe_video(source, session_dir)
    return manifest
