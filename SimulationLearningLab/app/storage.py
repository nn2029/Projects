from __future__ import annotations

import json
import shutil
from pathlib import Path


def list_sessions(data_root: Path) -> list[dict]:
    sessions = []
    if not data_root.exists():
        return sessions
    for child in data_root.iterdir():
        if not child.is_dir():
            continue
        manifest_path = child / "manifest.json"
        if not manifest_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        sessions.append({
            "id": manifest.get("id", child.name),
            "topic": manifest.get("topic") or "Untitled simulation",
            "target_level": manifest.get("target_level"),
            "learning_outcome": manifest.get("learning_outcome"),
            "created_at": manifest.get("created_at"),
            "status": manifest.get("status"),
            "media_count": len(manifest.get("media") or []),
            "compiled": manifest.get("compiled"),
        })
    sessions.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return sessions


def export_session_zip(session_dir: Path) -> Path:
    export_dir = session_dir / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    base = export_dir / "simulation-learning-lab-export"
    zip_path = Path(shutil.make_archive(str(base), "zip", root_dir=session_dir, base_dir="compiled"))
    return zip_path


def read_json_if_exists(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
