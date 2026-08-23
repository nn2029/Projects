from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastapi import Body, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .ai import AIProviderError, generate_spec_openai, provider_status
from .enrichment import enrich_manifest
from .media import inspect_saved_media, save_upload_stream
from .pipeline import build_agent_prompt, build_blueprint, create_session, read_manifest, write_manifest
from .simulation import SpecValidationError, build_starter_spec, compile_bundle, validate_spec
from .storage import export_session_zip, list_sessions, read_json_if_exists

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_ROOT = Path(os.getenv("SLL_DATA_DIR", BASE_DIR / "data"))
STATIC_DIR = Path(__file__).resolve().parent / "static"
DATA_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Simulation Learning Lab", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _session_dir(session_id: str) -> Path:
    session_dir = DATA_ROOT / session_id
    if not (session_dir / "manifest.json").exists():
        raise HTTPException(404, "Session not found")
    return session_dir


def _load_blueprint(session_dir: Path, manifest: dict) -> dict:
    path = session_dir / "blueprint.json"
    return read_json_if_exists(path) or build_blueprint(manifest)


def _load_starter(session_dir: Path, manifest: dict, blueprint: dict) -> dict:
    path = session_dir / "starter-spec.json"
    starter = read_json_if_exists(path)
    if starter:
        return starter
    starter = build_starter_spec(manifest, blueprint)
    path.write_text(json.dumps(starter, indent=2), encoding="utf-8")
    return starter


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "version": "1.0.0",
        "product": "Simulation Learning Lab",
        "providers": provider_status(),
    }


@app.get("/api/providers")
def providers():
    return provider_status()


@app.get("/api/sessions")
def sessions_index():
    return {"sessions": list_sessions(DATA_ROOT)}


@app.post("/api/sessions")
async def new_session(
    topic: str = Form(default=""),
    target_level: str = Form(default="practitioner"),
    learning_outcome: str = Form(default=""),
    files: list[UploadFile] = File(default=[]),
):
    if not topic.strip() and not files:
        raise HTTPException(400, "Provide a topic or at least one image/video.")
    session_id, session_dir, manifest = create_session(DATA_ROOT, topic, target_level, learning_outcome)
    manifest["schema_version"] = "3.1"
    errors = []
    try:
        for upload in files:
            try:
                saved_path, mime_type = save_upload_stream(
                    upload.file, upload.filename or "upload", upload.content_type, session_dir / "uploads"
                )
                item = inspect_saved_media(
                    saved_path, upload.filename or saved_path.name, mime_type, session_dir
                )
                manifest["media"].append(item.to_dict())
            except Exception as exc:
                errors.append({"file": upload.filename, "error": str(exc)})
        manifest["status"] = "prepared"
        manifest["errors"] = errors
        prompt = build_agent_prompt(manifest)
        (session_dir / "agent-prompt.md").write_text(prompt, encoding="utf-8")
        blueprint = build_blueprint(manifest)
        (session_dir / "blueprint.json").write_text(json.dumps(blueprint, indent=2), encoding="utf-8")
        starter = build_starter_spec(manifest, blueprint)
        (session_dir / "starter-spec.json").write_text(json.dumps(starter, indent=2), encoding="utf-8")
        write_manifest(session_dir, manifest)
        return {"session": manifest, "blueprint": blueprint, "agent_prompt": prompt, "starter_spec": starter}
    finally:
        for upload in files:
            await upload.close()


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    session_dir = _session_dir(session_id)
    manifest = read_manifest(session_dir)
    blueprint = _load_blueprint(session_dir, manifest)
    starter_spec = _load_starter(session_dir, manifest, blueprint)
    generated = read_json_if_exists(session_dir / "generated-spec.json")
    compiled = read_json_if_exists(session_dir / "compiled" / "simulation-spec.json")
    return {
        "session": manifest,
        "blueprint": blueprint,
        "starter_spec": starter_spec,
        "generated_spec": generated,
        "compiled_spec": compiled,
    }


@app.post("/api/sessions/{session_id}/enrich")
def enrich_session(
    session_id: str,
    payload: dict[str, Any] = Body(default={}),
):
    session_dir = _session_dir(session_id)
    manifest = read_manifest(session_dir)
    enriched = enrich_manifest(
        session_dir,
        manifest,
        ocr=bool(payload.get("ocr", True)),
        transcribe=bool(payload.get("transcribe", True)),
    )
    enriched["status"] = "enriched"
    write_manifest(session_dir, enriched)
    prompt = build_agent_prompt(enriched)
    (session_dir / "agent-prompt.md").write_text(prompt, encoding="utf-8")
    return {"session": enriched, "agent_prompt": prompt}


@app.post("/api/sessions/{session_id}/generate")
def generate_session_spec(
    session_id: str,
    payload: dict[str, Any] = Body(default={}),
):
    session_dir = _session_dir(session_id)
    manifest = read_manifest(session_dir)
    blueprint = _load_blueprint(session_dir, manifest)
    starter = _load_starter(session_dir, manifest, blueprint)
    provider = payload.get("provider", "openai")
    if provider != "openai":
        raise HTTPException(400, "Only the OpenAI provider is built in currently; manual/agent spec import remains provider-neutral.")
    try:
        spec = generate_spec_openai(session_dir, manifest, starter, model=payload.get("model"))
    except AIProviderError as exc:
        raise HTTPException(503, str(exc))
    manifest["status"] = "generated"
    manifest["generation"] = {
        "provider": "openai",
        "model": payload.get("model") or os.getenv("OPENAI_MODEL", "gpt-5.6-terra"),
    }
    write_manifest(session_dir, manifest)
    return {"ok": True, "spec": spec, "session": manifest}


@app.get("/api/sessions/{session_id}/starter-spec")
def get_starter_spec(session_id: str):
    session_dir = _session_dir(session_id)
    manifest = read_manifest(session_dir)
    blueprint = _load_blueprint(session_dir, manifest)
    return _load_starter(session_dir, manifest, blueprint)


@app.put("/api/sessions/{session_id}/spec")
def save_spec(session_id: str, payload: Any = Body(...)):
    session_dir = _session_dir(session_id)
    try:
        spec = validate_spec(payload.get("spec") if isinstance(payload, dict) and "spec" in payload else payload)
    except (SpecValidationError, json.JSONDecodeError) as exc:
        raise HTTPException(400, str(exc))
    (session_dir / "generated-spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    manifest = read_manifest(session_dir)
    manifest["status"] = "authored"
    write_manifest(session_dir, manifest)
    return {"ok": True, "spec": spec}


@app.post("/api/sessions/{session_id}/compile")
def compile_session(session_id: str, payload: Any = Body(...)):
    session_dir = _session_dir(session_id)
    try:
        raw = payload.get("spec") if isinstance(payload, dict) and "spec" in payload else payload
        if raw in (None, {}):
            raw = read_json_if_exists(session_dir / "generated-spec.json") or read_json_if_exists(session_dir / "starter-spec.json")
        spec = validate_spec(raw)
        result = compile_bundle(session_dir, spec, STATIC_DIR)
        return {"ok": True, "compiled": result, "spec": spec}
    except SpecValidationError as exc:
        raise HTTPException(400, str(exc))
    except json.JSONDecodeError as exc:
        raise HTTPException(400, f"Invalid JSON: {exc}")


@app.get("/api/sessions/{session_id}/compiled/spec")
def get_compiled_spec(session_id: str):
    session_dir = _session_dir(session_id)
    path = session_dir / "compiled" / "simulation-spec.json"
    if not path.exists():
        raise HTTPException(404, "Compiled simulation spec not found")
    return json.loads(path.read_text())


@app.get("/api/sessions/{session_id}/export")
def export_session(session_id: str):
    session_dir = _session_dir(session_id)
    if not (session_dir / "compiled" / "index.html").exists():
        raise HTTPException(409, "Compile the simulation before exporting it.")
    zip_path = export_session_zip(session_dir)
    return FileResponse(zip_path, media_type="application/zip", filename=f"simulation-learning-lab-{session_id}.zip")


@app.get("/runtime/{session_id}")
def runtime(session_id: str):
    _session_dir(session_id)
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Simulation Runtime</title>
  <link rel=\"stylesheet\" href=\"/static/runtime.css\" />
</head>
<body>
  <div id=\"app\"></div>
  <script>window.SLL_SPEC_URL = '/api/sessions/{session_id}/compiled/spec'; window.SLL_SESSION_ID = '{session_id}';</script>
  <script src=\"/static/runtime.js\"></script>
</body>
</html>
"""
    return HTMLResponse(html)


@app.get("/api/sessions/{session_id}/files/{path:path}")
def get_session_file(session_id: str, path: str):
    session_dir = _session_dir(session_id).resolve()
    candidate = (session_dir / path).resolve()
    if not str(candidate).startswith(str(session_dir)) or not candidate.is_file():
        raise HTTPException(404, "File not found")
    return FileResponse(candidate)
