from __future__ import annotations

import base64
import json
import os
import re
from pathlib import Path
from typing import Any

from .pipeline import build_agent_prompt
from .simulation import validate_spec


class AIProviderError(RuntimeError):
    pass


def provider_status() -> dict:
    try:
        from openai import OpenAI  # noqa: F401
        sdk = True
    except Exception:
        sdk = False
    return {
        "openai": {
            "configured": bool(os.getenv("OPENAI_API_KEY")) and sdk,
            "api_key": bool(os.getenv("OPENAI_API_KEY")),
            "sdk": sdk,
            "model": os.getenv("OPENAI_MODEL", "gpt-5.6-terra"),
            "web_search": os.getenv("SLL_ENABLE_WEB_SEARCH", "1") not in {"0", "false", "False"},
        }
    }


def _data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp", ".gif": "image/gif",
    }.get(suffix, "image/jpeg")
    raw = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{raw}"


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def _build_generation_prompt(manifest: dict, starter_spec: dict) -> str:
    base = build_agent_prompt(manifest)
    enrichments = []
    for item in manifest.get("media", []):
        if item.get("ocr", {}).get("text"):
            enrichments.append(f"IMAGE OCR {item['id']}:\n{item['ocr']['text'][:5000]}")
        transcript = item.get("transcript", {})
        if transcript.get("text"):
            enrichments.append(f"VIDEO TRANSCRIPT {item['id']}:\n{transcript['text'][:12000]}")
        frame_ocr = [x for x in item.get("frame_ocr", []) if x.get("text")]
        if frame_ocr:
            joined = "\n".join(f"{x['timestamp']}: {x['text'][:800]}" for x in frame_ocr[:12])
            enrichments.append(f"VIDEO FRAME OCR {item['id']}:\n{joined}")
    enrichment_block = "\n\n".join(enrichments) if enrichments else "No OCR/transcript enrichment is available."
    return f"""{base}

## Enrichment evidence
{enrichment_block}

## Runtime compiler contract
Return ONLY valid JSON, no markdown fences or commentary.
The JSON must be a complete `simulation-spec.json` compatible with the product runtime.
Use this starter shape as a structural guide, but replace placeholder content with the real mechanism:
{json.dumps(starter_spec, indent=2)}

Requirements:
- Make the simulation mechanistic rather than decorative.
- Use at least 4 stages when the topic supports it.
- Use meaningful entities and state variables.
- Include at least 2 scenarios when a counterfactual or failure mode exists.
- Include predict-next or checkpoint questions throughout the lesson.
- Preserve upload provenance in stage `provenance` entries whenever the claim comes from the media.
- Fidelity ledger entries must use one of COMPUTED, SOURCE-GROUNDED, SCALED, ASSUMED, ILLUSTRATIVE, UNKNOWN.
- Never label a media observation as SOURCE-GROUNDED merely because it appeared in the upload.
- If web research is available, use it for high-impact factual claims and summarize the source in fidelity/source notes.
"""


def generate_spec_openai(session_dir: Path, manifest: dict, starter_spec: dict, *, model: str | None = None) -> dict:
    try:
        from openai import OpenAI  # type: ignore
    except Exception as exc:
        raise AIProviderError("Install the official OpenAI Python SDK to use built-in generation.") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIProviderError("OPENAI_API_KEY is not configured.")

    client = OpenAI(api_key=api_key)
    chosen_model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
    prompt = _build_generation_prompt(manifest, starter_spec)
    content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt}]

    max_images = int(os.getenv("SLL_MAX_MODEL_IMAGES", "16"))
    image_count = 0
    for item in manifest.get("media", []):
        if image_count >= max_images:
            break
        if item.get("kind") == "image":
            path = session_dir / "uploads" / item["stored_name"]
            content.append({"type": "input_image", "image_url": _data_url(path), "detail": "high"})
            image_count += 1
        elif item.get("kind") == "video":
            frames = item.get("keyframes") or []
            per_video = max(1, min(8, max_images - image_count))
            if len(frames) > per_video:
                indexes = [round(i * (len(frames) - 1) / (per_video - 1)) for i in range(per_video)] if per_video > 1 else [len(frames)//2]
                selected = [frames[i] for i in indexes]
            else:
                selected = frames
            for frame in selected:
                if image_count >= max_images:
                    break
                path = session_dir / frame["relative_path"]
                content.append({"type": "input_text", "text": f"Video {item['id']} frame at {frame['timestamp']}"})
                content.append({"type": "input_image", "image_url": _data_url(path), "detail": "high"})
                image_count += 1

    kwargs: dict[str, Any] = {
        "model": chosen_model,
        "input": [{"role": "user", "content": content}],
    }
    if os.getenv("SLL_ENABLE_WEB_SEARCH", "1") not in {"0", "false", "False"}:
        kwargs["tools"] = [{"type": "web_search"}]

    response = client.responses.create(**kwargs)
    raw_text = getattr(response, "output_text", "") or ""
    if not raw_text:
        raise AIProviderError("The model returned no output text.")

    try:
        spec = validate_spec(_extract_json(raw_text))
    except Exception as exc:
        error_path = session_dir / "ai-generation-error.txt"
        error_path.write_text(raw_text, encoding="utf-8")
        raise AIProviderError(f"The model response was not a valid simulation spec: {exc}") from exc

    (session_dir / "generated-spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return spec
