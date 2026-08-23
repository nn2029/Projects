# Simulation Learning Lab

**Turn concepts, screenshots and videos into interactive learning simulations.**

Simulation Learning Lab is a full local-first product for building explorable mental models. It combines multimodal evidence intake, OCR/transcription, optional AI generation, a structured authoring surface, a simulation compiler, multiple visual grammars, active recall, mastery tracking and portable export.

## Product flow

```text
Topic / image / video
        ↓
Evidence + timestamped keyframes
        ↓
OCR / transcript enrichment
        ↓
AI mechanism generation or manual authoring
        ↓
simulation-spec.json
        ↓
Compiler
        ↓
Interactive runtime + mastery tracking
        ↓
Portable ZIP export
```

## Features

### Multimodal intake
- images and videos up to 500 MB each;
- deterministic video metadata probing;
- timestamped representative keyframe extraction;
- provenance IDs retained throughout the session.

### Evidence enrichment
- local Tesseract OCR for images and video keyframes;
- video audio extraction through ffmpeg;
- OpenAI transcription when configured;
- local Whisper CLI fallback when installed.

### Built-in AI generation
- optional OpenAI Responses API integration;
- image uploads and selected video keyframes supplied as multimodal evidence;
- optional web search for factual verification;
- provider-neutral agent prompt remains available when no key is configured.

### Simulation authoring
- structured title/objective/grammar editor;
- entity authoring;
- stage/state-transition authoring;
- retrieval-prompt authoring;
- advanced raw JSON editor.

### Simulation compiler
- validates the simulation contract;
- writes a portable compiled bundle;
- keeps the mechanism model separate from the renderer.

### Learning runtime
Eight visual grammars are included:
- state-machine
- factory
- isometric-town
- circuit
- agent-field
- timeline
- robot-world
- layer-stack

The learner can:
- step through causal stages;
- inspect cumulative state;
- switch scenarios;
- answer active-recall prompts;
- inspect provenance and the fidelity ledger;
- track mastery and stage completion locally.

### Workspace and export
- session library;
- embedded runtime preview;
- ZIP export of the compiled simulation;
- Docker support;
- GitHub Actions CI.

## Run locally

Requirements:
- Python 3.10+
- ffmpeg / ffprobe
- Tesseract for OCR

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Open `http://127.0.0.1:8787`.

## Enable built-in AI generation

Add an API key to `.env`:

```bash
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.6-terra
SLL_ENABLE_WEB_SEARCH=1
```

The product still works without an API key: prepare evidence, copy the agent handoff prompt, generate a spec with any capable reasoning/coding agent, and paste or visually edit the result in the Author tab.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

## Test

```bash
pytest -q
```

## Key files

- `app/main.py` — product API and session orchestration
- `app/media.py` — media intake and video keyframes
- `app/enrichment.py` — OCR/transcription
- `app/ai.py` — optional multimodal AI generation
- `app/simulation.py` — spec validation and compiler
- `app/static/` — workspace UI and learning runtime
- `references/simulation-spec-template.json` — compiler contract example
- `SKILL.md` — reusable AI coding-agent skill
- `PRODUCT.md` — architecture and product boundaries

## Security / privacy posture

- sessions are stored locally under `data/` by default;
- uploads are not sent to an AI provider unless the user triggers AI generation;
- provider keys are read from environment variables and never persisted in session files;
- file-serving paths are constrained to the current session directory;
- deterministic media preprocessing does not claim semantic understanding.

## Current scope

This is a local-first single-user product. Authentication, hosted object storage, collaborative workspaces and server-side mastery accounts are intentionally outside the first product release, but the compiler/runtime contract is designed so those can be layered on later without rebuilding the learning model.
