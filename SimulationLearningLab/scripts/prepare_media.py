#!/usr/bin/env python3
"""Prepare text/image/video inputs for Simulation Learning Lab.

Example:
  python scripts/prepare_media.py \
    --topic "How does this checkout flow work?" \
    --level practitioner \
    --outcome "Diagnose failed payment states" \
    screenshot.png demo.mp4

Prints the created session directory. The AI agent should inspect agent-prompt.md,
manifest.json and the referenced image/keyframe files.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.media import inspect_saved_media  # noqa: E402
from app.pipeline import build_agent_prompt, build_blueprint, create_session, write_manifest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare multimodal learning evidence")
    parser.add_argument("media", nargs="*", type=Path, help="Image/video files")
    parser.add_argument("--topic", default="", help="Concept or question")
    parser.add_argument("--level", default="practitioner", choices=["intuitive", "practitioner", "interview", "academic", "expert refresher"])
    parser.add_argument("--outcome", default="", help="Desired learning outcome")
    parser.add_argument("--output", type=Path, default=ROOT / "data", help="Session output root")
    args = parser.parse_args()

    if not args.topic.strip() and not args.media:
        parser.error("Provide --topic or at least one media file")

    sid, session_dir, manifest = create_session(args.output, args.topic, args.level, args.outcome)
    errors = []
    for source in args.media:
        try:
            source = source.expanduser().resolve()
            if not source.is_file():
                raise FileNotFoundError(source)
            mime = mimetypes.guess_type(source.name)[0] or "application/octet-stream"
            target = session_dir / "uploads" / f"{source.stem[:40]}-{source.stat().st_size}{source.suffix.lower()}"
            shutil.copy2(source, target)
            item = inspect_saved_media(target, source.name, mime, session_dir)
            manifest["media"].append(item.to_dict())
        except Exception as exc:
            errors.append({"file": str(source), "error": str(exc)})

    manifest["errors"] = errors
    manifest["status"] = "prepared"
    write_manifest(session_dir, manifest)
    (session_dir / "blueprint.json").write_text(json.dumps(build_blueprint(manifest), indent=2), encoding="utf-8")
    (session_dir / "agent-prompt.md").write_text(build_agent_prompt(manifest), encoding="utf-8")
    print(session_dir)
    if errors:
        print(json.dumps({"warnings": errors}, indent=2), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
