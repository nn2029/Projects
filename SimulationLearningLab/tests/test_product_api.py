import io
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


def _png_bytes() -> bytes:
    image = Image.new("RGB", (120, 80), "white")
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def test_full_manual_product_flow(monkeypatch, tmp_path: Path):
    import app.main as main

    monkeypatch.setattr(main, "DATA_ROOT", tmp_path)
    client = TestClient(app)

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["product"] == "Simulation Learning Lab"

    created = client.post(
        "/api/sessions",
        data={"topic": "How queues work", "target_level": "practitioner", "learning_outcome": "Diagnose backlog"},
        files={"files": ("diagram.png", _png_bytes(), "image/png")},
    )
    assert created.status_code == 200
    body = created.json()
    sid = body["session"]["id"]
    assert body["blueprint"]["input_summary"]["image_count"] == 1

    listed = client.get("/api/sessions").json()["sessions"]
    assert listed and listed[0]["id"] == sid

    saved = client.put(f"/api/sessions/{sid}/spec", json={"spec": body["starter_spec"]})
    assert saved.status_code == 200

    compiled = client.post(f"/api/sessions/{sid}/compile", json={"spec": saved.json()["spec"]})
    assert compiled.status_code == 200

    runtime = client.get(f"/runtime/{sid}")
    assert runtime.status_code == 200
    assert "Simulation Runtime" in runtime.text

    exported = client.get(f"/api/sessions/{sid}/export")
    assert exported.status_code == 200
    assert exported.headers["content-type"] == "application/zip"
