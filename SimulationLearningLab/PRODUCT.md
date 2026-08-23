# Simulation Learning Lab — Product Architecture

Simulation Learning Lab is a multimodal learning workbench that converts concepts and source material into interactive causal simulations.

## Product loop

1. **Create a lab** from a topic, image, video, or any combination.
2. **Prepare evidence** by storing media, probing video metadata and extracting timestamped representative frames.
3. **Enrich evidence** with OCR and optional audio transcription.
4. **Generate a mechanism** with the built-in multimodal provider or an external coding/reasoning agent.
5. **Author and correct** the simulation spec in a structured editor.
6. **Compile** the spec into the runtime.
7. **Learn actively** through stage traversal, state inspection, scenario changes and retrieval questions.
8. **Persist mastery** in the browser and export the compiled lab as a portable ZIP.

## Boundaries

The product deliberately separates:

- deterministic preprocessing from semantic interpretation;
- media observation from inference;
- mechanism/state from visual rendering;
- source-grounded facts from scaled, assumed or illustrative teaching choices.

## Backend

FastAPI provides:

- session/media APIs;
- OCR/transcription enrichment;
- optional OpenAI multimodal generation;
- spec validation and persistence;
- compilation;
- runtime preview;
- portable ZIP export.

Sessions remain file-based by design for local portability. A hosted multi-user edition can replace the storage adapter without changing the compiler contract.

## Runtime

The runtime supports eight visual grammars:

- state-machine
- factory
- isometric-town
- circuit
- agent-field
- timeline
- robot-world
- layer-stack

Every runtime shares the same causal state model and active-recall engine.

## AI provider

The built-in OpenAI adapter is optional. Without a key, the app remains fully usable as an authoring/compiler environment and exports a provider-neutral agent handoff prompt.

When configured, the provider receives the learning prompt, OCR/transcript context, selected uploaded images and timestamped video frames. It returns a validated simulation spec.
