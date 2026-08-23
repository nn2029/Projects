from pathlib import Path
from app.pipeline import build_agent_prompt, build_blueprint


def test_blueprint_counts_media():
    manifest = {
        "topic": "Raft", "target_level": "practitioner", "learning_outcome": "diagnose elections",
        "media": [
            {"id": "a", "kind": "image", "original_name": "diagram.png", "stored_name": "a.png", "width": 100, "height": 100},
            {"id": "b", "kind": "video", "original_name": "demo.mp4", "stored_name": "b.mp4", "duration_seconds": 30,
             "keyframes": [{"timestamp":"00:10", "relative_path":"keyframes/b/frame-01.jpg"}]},
        ]
    }
    bp = build_blueprint(manifest)
    assert bp["input_summary"]["image_count"] == 1
    assert bp["input_summary"]["video_count"] == 1
    assert bp["input_summary"]["representative_video_frames"] == 1
    prompt = build_agent_prompt(manifest)
    assert "00:10" in prompt
    assert "diagram.png" in prompt
