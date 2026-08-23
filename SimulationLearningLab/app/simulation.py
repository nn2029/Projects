from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .pipeline import FIDELITY_CLASSES, read_manifest

DEFAULT_STYLES = {
    "state-machine": {"accent": "#264653", "surface": "#f6f3ee", "node_shape": "pill"},
    "factory": {"accent": "#8f4b2f", "surface": "#f7f1ea", "node_shape": "rect"},
    "isometric-town": {"accent": "#5e548e", "surface": "#f4f1fb", "node_shape": "rect"},
    "circuit": {"accent": "#0f766e", "surface": "#eef8f6", "node_shape": "pill"},
    "agent-field": {"accent": "#375c2c", "surface": "#f1f7ed", "node_shape": "pill"},
    "timeline": {"accent": "#1d3557", "surface": "#eef3f8", "node_shape": "pill"},
    "robot-world": {"accent": "#6b2f6a", "surface": "#f6edf7", "node_shape": "rect"},
    "layer-stack": {"accent": "#7a3e12", "surface": "#faf1ea", "node_shape": "rect"},
}


class SpecValidationError(ValueError):
    pass


def _load_json(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return json.loads(value)
    raise SpecValidationError("Simulation spec must be a JSON object or JSON string.")


def build_starter_spec(manifest: dict, blueprint: dict | None = None) -> dict:
    """Create a starter spec that an agent or user can fill in.

    This is intentionally skeletal. It bridges the agent output format to the runtime.
    """
    blueprint = blueprint or {}
    provenance_nodes = []
    for item in manifest.get("media", []):
        if item.get("kind") == "image":
            provenance_nodes.append({
                "id": item["id"],
                "label": item["original_name"],
                "kind": "evidence",
                "detail": f"Image upload · {item.get('width')}×{item.get('height')}"
            })
        else:
            provenance_nodes.append({
                "id": item["id"],
                "label": item["original_name"],
                "kind": "evidence",
                "detail": f"Video upload · {len(item.get('keyframes') or [])} representative frames"
            })

    topic = manifest.get("topic") or "Untitled simulation"
    objective = manifest.get("learning_outcome") or "Explain the mechanism, predict the next state and diagnose one failure mode."
    return {
        "schema_version": "3.0",
        "title": topic,
        "objective": objective,
        "target_level": manifest.get("target_level") or "practitioner",
        "visual_grammar": "state-machine",
        "lesson": {
            "guided_intro": f"This simulation is a starter scaffold for '{topic}'. Replace the placeholder stages with the real mechanism.",
            "challenge_prompt": "Use the controls or scenarios, then explain why the system behaves that way.",
        },
        "entities": provenance_nodes or [
            {"id": "input", "label": "Input", "kind": "entity", "detail": "Starting point"},
            {"id": "process", "label": "Process", "kind": "entity", "detail": "Main transformation"},
            {"id": "output", "label": "Output", "kind": "entity", "detail": "Observed result"},
        ],
        "state": {
            "phase": "start",
            "status": "idle",
            "notes": "Replace the starter values with real state variables."
        },
        "scenarios": [
            {
                "id": "baseline",
                "label": "Baseline",
                "description": "Nominal execution path.",
                "state_overrides": {},
            },
            {
                "id": "failure",
                "label": "Failure case",
                "description": "Use this scenario to model a meaningful failure injection.",
                "state_overrides": {"status": "degraded"},
            },
        ],
        "stages": [
            {
                "id": "observe",
                "label": "Observe evidence",
                "summary": "Inspect the source material and note what is directly visible before interpreting it.",
                "focus_entities": [e["id"] for e in provenance_nodes[:2]] if provenance_nodes else ["input"],
                "state_patch": {"phase": "observe", "status": "collecting evidence"},
                "questions": [
                    {
                        "type": "predict-next",
                        "prompt": "After observing the source material, what should happen next?",
                        "choices": [
                            "Research and reconcile claims",
                            "Jump straight to final explanation",
                            "Ignore provenance"
                        ],
                        "answer_index": 0,
                        "explanation": "A trustworthy simulation reconciles observed evidence with external understanding before teaching the mechanism."
                    }
                ],
                "provenance": [],
            },
            {
                "id": "model",
                "label": "Extract the mechanism",
                "summary": "Turn the evidence into entities, state transitions, constraints and outputs.",
                "focus_entities": [e["id"] for e in provenance_nodes[:2]] if provenance_nodes else ["process"],
                "state_patch": {"phase": "model", "status": "mechanism extracted"},
                "questions": [
                    {
                        "type": "checkpoint",
                        "prompt": "Name one state variable that actually changes during the process.",
                        "answer_text": "Any real changing state variable from the model is acceptable.",
                        "explanation": "The runtime is strongest when it exposes state rather than only sequence."
                    }
                ],
                "provenance": [],
            },
            {
                "id": "challenge",
                "label": "Challenge the learner",
                "summary": "Introduce a meaningful variation or failure and ask the learner to diagnose it.",
                "focus_entities": provenance_nodes[:1] and [provenance_nodes[0]["id"]] or ["output"],
                "state_patch": {"phase": "challenge", "status": "testing understanding"},
                "questions": [
                    {
                        "type": "failure-injection",
                        "prompt": "What breaks if a critical step is skipped or corrupted?",
                        "answer_text": "Describe the observed failure and why the mechanism can no longer produce the expected output.",
                        "explanation": "Failure diagnosis is where the causal model proves whether it has been learned."
                    }
                ],
                "provenance": [],
            },
        ],
        "fidelity_ledger": [
            {
                "element": "Placeholder starter spec",
                "classification": "ASSUMED",
                "detail": "This initial spec is scaffolding. Replace it with a real mechanism before treating it as instructional content.",
                "confidence": 0.45,
            }
        ],
        "validation_checks": blueprint.get("pipeline") or [
            "Mechanism matches trusted evidence",
            "Key state transitions are visible",
            "At least one failure case is testable",
        ],
    }


def validate_spec(value: Any) -> dict:
    spec = _load_json(value)
    if not isinstance(spec, dict):
        raise SpecValidationError("Simulation spec must be a JSON object.")

    title = str(spec.get("title") or "").strip()
    if not title:
        raise SpecValidationError("Spec requires a non-empty 'title'.")

    stages = spec.get("stages")
    if not isinstance(stages, list) or not stages:
        raise SpecValidationError("Spec requires a non-empty 'stages' array.")

    entities = spec.get("entities") or []
    if not isinstance(entities, list):
        raise SpecValidationError("'entities' must be an array.")
    entity_ids = set()
    for entity in entities:
        if not isinstance(entity, dict):
            raise SpecValidationError("Each entity must be an object.")
        entity_id = str(entity.get("id") or "").strip()
        if not entity_id:
            raise SpecValidationError("Every entity requires an 'id'.")
        if entity_id in entity_ids:
            raise SpecValidationError(f"Duplicate entity id: {entity_id}")
        entity_ids.add(entity_id)
        entity.setdefault("label", entity_id.replace("_", " ").title())
        entity.setdefault("kind", "entity")
        entity.setdefault("detail", "")

    grammar = spec.get("visual_grammar") or "state-machine"
    if grammar not in DEFAULT_STYLES:
        raise SpecValidationError(
            f"Unsupported visual_grammar '{grammar}'. Supported: {', '.join(DEFAULT_STYLES)}"
        )

    base_state = spec.get("state") or {}
    if not isinstance(base_state, dict):
        raise SpecValidationError("'state' must be an object.")

    stage_ids = set()
    for idx, stage in enumerate(stages, start=1):
        if not isinstance(stage, dict):
            raise SpecValidationError(f"Stage {idx} must be an object.")
        stage_id = str(stage.get("id") or "").strip()
        label = str(stage.get("label") or "").strip()
        summary = str(stage.get("summary") or "").strip()
        if not stage_id or not label or not summary:
            raise SpecValidationError(f"Stage {idx} requires 'id', 'label', and 'summary'.")
        if stage_id in stage_ids:
            raise SpecValidationError(f"Duplicate stage id: {stage_id}")
        stage_ids.add(stage_id)
        stage["focus_entities"] = stage.get("focus_entities") or []
        if not isinstance(stage["focus_entities"], list):
            raise SpecValidationError(f"Stage {stage_id} 'focus_entities' must be an array.")
        unknown_entities = [e for e in stage["focus_entities"] if e not in entity_ids]
        if unknown_entities:
            raise SpecValidationError(
                f"Stage {stage_id} references unknown entities: {', '.join(unknown_entities)}"
            )
        stage.setdefault("state_patch", {})
        if not isinstance(stage["state_patch"], dict):
            raise SpecValidationError(f"Stage {stage_id} 'state_patch' must be an object.")
        stage.setdefault("questions", [])
        if not isinstance(stage["questions"], list):
            raise SpecValidationError(f"Stage {stage_id} 'questions' must be an array.")
        for q_index, q in enumerate(stage["questions"], start=1):
            if not isinstance(q, dict) or not str(q.get("prompt") or "").strip():
                raise SpecValidationError(f"Stage {stage_id} question {q_index} requires a prompt.")
            q.setdefault("type", "checkpoint")
            q.setdefault("explanation", "")
            if "choices" in q:
                if not isinstance(q["choices"], list) or len(q["choices"]) < 2:
                    raise SpecValidationError(f"Stage {stage_id} question {q_index} choices must contain at least 2 options.")
                answer_index = q.get("answer_index")
                if not isinstance(answer_index, int) or not 0 <= answer_index < len(q["choices"]):
                    raise SpecValidationError(f"Stage {stage_id} question {q_index} requires a valid answer_index.")
        stage.setdefault("provenance", [])
        if not isinstance(stage["provenance"], list):
            raise SpecValidationError(f"Stage {stage_id} 'provenance' must be an array.")

    scenarios = spec.get("scenarios") or []
    if not isinstance(scenarios, list):
        raise SpecValidationError("'scenarios' must be an array.")
    scenario_ids = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise SpecValidationError("Each scenario must be an object.")
        scenario_id = str(scenario.get("id") or "").strip()
        if not scenario_id:
            raise SpecValidationError("Every scenario requires an 'id'.")
        if scenario_id in scenario_ids:
            raise SpecValidationError(f"Duplicate scenario id: {scenario_id}")
        scenario_ids.add(scenario_id)
        scenario.setdefault("label", scenario_id.replace("_", " ").title())
        scenario.setdefault("description", "")
        scenario.setdefault("state_overrides", {})
        if not isinstance(scenario["state_overrides"], dict):
            raise SpecValidationError(f"Scenario {scenario_id} 'state_overrides' must be an object.")

    ledger = spec.get("fidelity_ledger") or []
    if not isinstance(ledger, list) or not ledger:
        raise SpecValidationError("Spec requires a non-empty 'fidelity_ledger' array.")
    for i, row in enumerate(ledger, start=1):
        if not isinstance(row, dict):
            raise SpecValidationError(f"Fidelity row {i} must be an object.")
        classification = row.get("classification")
        if classification not in FIDELITY_CLASSES:
            raise SpecValidationError(
                f"Fidelity row {i} classification must be one of: {', '.join(FIDELITY_CLASSES)}"
            )
        row.setdefault("element", f"Element {i}")
        row.setdefault("detail", "")
        row.setdefault("confidence", None)

    spec.setdefault("schema_version", "3.0")
    spec.setdefault("objective", "Explain the mechanism clearly.")
    spec.setdefault("target_level", "practitioner")
    spec.setdefault("lesson", {})
    spec["lesson"].setdefault("guided_intro", "")
    spec["lesson"].setdefault("challenge_prompt", "")
    spec["visual_grammar"] = grammar
    spec["theme"] = DEFAULT_STYLES[grammar]
    spec.setdefault("validation_checks", [])
    return spec


def compile_bundle(session_dir: Path, spec: dict, runtime_static_dir: Path) -> dict:
    compiled_dir = session_dir / "compiled"
    compiled_dir.mkdir(parents=True, exist_ok=True)

    spec_path = compiled_dir / "simulation-spec.json"
    spec_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")

    # Copy self-contained runtime assets so the bundle can be opened directly.
    runtime_js = runtime_static_dir / "runtime.js"
    runtime_css = runtime_static_dir / "runtime.css"
    if not runtime_js.exists() or not runtime_css.exists():
        raise FileNotFoundError("Runtime assets are missing.")

    shutil.copy2(runtime_js, compiled_dir / "runtime.js")
    shutil.copy2(runtime_css, compiled_dir / "runtime.css")

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{spec['title']}</title>
  <link rel=\"stylesheet\" href=\"runtime.css\" />
</head>
<body>
  <div id=\"app\"></div>
  <script>window.SLL_SPEC_URL = 'simulation-spec.json';</script>
  <script src=\"runtime.js\"></script>
</body>
</html>
"""
    (compiled_dir / "index.html").write_text(html, encoding="utf-8")

    manifest = read_manifest(session_dir)
    manifest["status"] = "compiled"
    manifest["compiled"] = {
        "title": spec["title"],
        "visual_grammar": spec["visual_grammar"],
        "stage_count": len(spec.get("stages") or []),
        "scenario_count": len(spec.get("scenarios") or []),
        "runtime": "compiled/index.html",
        "spec": "compiled/simulation-spec.json",
    }
    (session_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {
        "runtime_path": "compiled/index.html",
        "spec_path": "compiled/simulation-spec.json",
        "stage_count": len(spec.get("stages") or []),
        "scenario_count": len(spec.get("scenarios") or []),
    }
