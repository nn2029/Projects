# Multimodal Architecture

## v3 update

The architecture now has three layers instead of two:

1. **Multimodal intake** — prepare image/video/text evidence with provenance.
2. **Reasoning layer** — produce the mechanism model and emit `simulation-spec.json`.
3. **Compiler/runtime layer** — validate the spec and render a runnable learning simulation.

## Why the compiler layer matters

Without a compiler contract, every generated simulation becomes a one-off engineering project.

The compiler layer introduces a stable interchange format so that an AI agent can reason once and a generic runtime can immediately render the result.

That bridge is the key addition in v3.

## Compiler contract

The reasoning agent should output a structured `simulation-spec.json` with:

- metadata (`title`, `objective`, `target_level`);
- the chosen `visual_grammar`;
- `entities` the learner should track;
- base `state` variables;
- optional `scenarios` for counterfactuals or failure injection;
- ordered `stages` with summaries, `state_patch` updates, focus entities and active-learning questions;
- a `fidelity_ledger`.

The compiler validates the structure and then produces a portable runtime bundle.

## Runtime model

The runtime is deliberately generic.

It computes current state as:

**base state + scenario overrides + cumulative stage patches**

and renders:

- the current stage;
- the currently focused entities;
- state variables;
- stage questions;
- provenance notes;
- the fidelity ledger.

This keeps the mechanism model independent from presentation.

## Authoring boundary

The runtime does not infer meaning from media. It only executes the emitted spec.

The media understanding and pedagogy decisions still belong to the reasoning layer.
