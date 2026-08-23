from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


FIDELITY_CLASSES = [
    "COMPUTED", "SOURCE-GROUNDED", "SCALED", "ASSUMED", "ILLUSTRATIVE", "UNKNOWN"
]


def create_session(root: Path, topic: str, level: str, outcome: str) -> tuple[str, Path, dict]:
    session_id = uuid4().hex[:12]
    session_dir = root / session_id
    (session_dir / "uploads").mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "2.0",
        "id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic.strip(),
        "target_level": level,
        "learning_outcome": outcome.strip(),
        "media": [],
        "status": "created",
    }
    write_manifest(session_dir, manifest)
    return session_id, session_dir, manifest


def write_manifest(session_dir: Path, manifest: dict) -> None:
    (session_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def read_manifest(session_dir: Path) -> dict:
    return json.loads((session_dir / "manifest.json").read_text(encoding="utf-8"))


def build_agent_prompt(manifest: dict) -> str:
    media_lines = []
    for item in manifest.get("media", []):
        if item["kind"] == "image":
            media_lines.append(
                f"- IMAGE {item['id']}: {item['original_name']} ({item.get('width')}x{item.get('height')})"
            )
        else:
            frame_refs = ", ".join(
                f"{f['timestamp']}={f['relative_path']}" for f in item.get("keyframes") or []
            )
            media_lines.append(
                f"- VIDEO {item['id']}: {item['original_name']} ({item.get('duration_seconds', 0):.1f}s). "
                f"Representative frames: {frame_refs}"
            )
    media_block = "\n".join(media_lines) if media_lines else "- No uploaded media."
    return f"""# Multimodal Simulation Learning Task

Use the simulation-learning-lab skill.

Topic: {manifest.get('topic') or '[infer from media]'}
Target level: {manifest.get('target_level')}
Learning outcome: {manifest.get('learning_outcome') or 'Infer the most useful measurable outcome.'}

Uploaded evidence:
{media_block}

## Required intake behavior
1. Inspect every uploaded image.
2. For every video, inspect the representative keyframes in timestamp order. If the keyframes are insufficient to understand an important transition, request or extract denser frames around that interval rather than guessing.
3. Treat visible text, diagrams, UI, demonstrations, spoken claims supplied by transcripts, and user annotations as evidence to be reconciled with authoritative external sources where the concept requires factual verification.
4. Keep provenance. Every media-derived claim must reference the asset ID and, for video, the timestamp/frame.
5. Distinguish what the upload SHOWS from what you INFER it means.
6. Do not use an uploaded example as proof that a general mechanism is correct.

## Produce
- multimodal evidence map
- causal/mechanism model
- misconceptions or ambiguities detected in the media
- simulation grammar recommendation
- active-learning interactions
- fidelity ledger using: {', '.join(FIDELITY_CLASSES)}
- implementation blueprint
- a complete `simulation-spec.json` matching the runtime compiler format
- then compile and implement the simulation when tools permit
"""


def build_blueprint(manifest: dict) -> dict:
    """Create a deterministic pre-analysis blueprint.

    This is intentionally not a fake vision model. Semantic conclusions are left for a
    multimodal model/agent. The output tells the agent exactly what evidence is available.
    """
    media = manifest.get("media", [])
    images = [m for m in media if m.get("kind") == "image"]
    videos = [m for m in media if m.get("kind") == "video"]
    provenance = []
    for image in images:
        provenance.append({
            "asset_id": image["id"], "kind": "image", "source": image["original_name"],
            "inspect": f"uploads/{image['stored_name']}"
        })
    for video in videos:
        provenance.append({
            "asset_id": video["id"], "kind": "video", "source": video["original_name"],
            "duration_seconds": video.get("duration_seconds"),
            "frames": [
                {"timestamp": f["timestamp"], "path": f["relative_path"]}
                for f in video.get("keyframes") or []
            ]
        })
    return {
        "topic": manifest.get("topic"),
        "target_level": manifest.get("target_level"),
        "learning_outcome": manifest.get("learning_outcome"),
        "input_summary": {
            "image_count": len(images),
            "video_count": len(videos),
            "representative_video_frames": sum(len(v.get("keyframes") or []) for v in videos),
        },
        "provenance_index": provenance,
        "pipeline": [
            "multimodal intake",
            "media observation ledger",
            "external evidence reconciliation",
            "causal model extraction",
            "simulation grammar selection",
            "active-learning design",
            "fidelity ledger",
            "simulation spec emission",
            "implementation",
            "validation and transfer testing",
        ],
        "fidelity_policy": {
            "classes": FIDELITY_CLASSES,
            "media_rule": "Uploaded media can ground observations, but general factual claims still require appropriate verification.",
            "video_rule": "Timestamp every video-derived claim and densify frames when a transition is ambiguous.",
        },
        "agent_prompt_file": "agent-prompt.md",
    }
