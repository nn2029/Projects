---
name: simulation-learning-lab
description: Turn a difficult concept, system, process, algorithm, mechanism, uploaded image, or uploaded video into a source-grounded interactive learning simulation. Use when the user wants to understand how something works, learn a complex technical topic visually, analyze a diagram/demo/recording as learning evidence, build an explorable explanation, or convert abstract material into a simulation. The simulation must preserve media provenance, distinguish observation from inference and real computation from simplification, and include active-recall learning loops rather than passive animation only.
---

# Simulation Learning Lab

Build a **learning instrument**, not a decorative animation.

The goal is to convert an abstract topic into an interactive mental model in which the learner can see state change, manipulate causes, predict outcomes, test misconceptions, and explain the mechanism back.

## Core principles

1. **Ground before generating.** Build the knowledge model from authoritative sources before designing the simulation.
2. **Separate mechanism from metaphor.** The visual world may be a city, factory, circuit, robot, pipeline, network, lab, or map, but the underlying state transitions must correspond to the real mechanism.
3. **Expose fidelity.** Every important claim, number, process step, or simplification is labelled as `computed`, `source-grounded`, `scaled`, `assumed`, `illustrative`, or `unknown`.
4. **Make the learner predict.** Before revealing a transition, ask what they expect to happen.
5. **Make variables movable.** Where meaningful, provide sliders, toggles, parameter inputs, failure injection, or alternative scenarios.
6. **Teach causality, not sequence alone.** A learner should be able to answer not only “what happens next?” but “why?” and “what changes if X changes?”
7. **Use retrieval, not rereading.** Add checkpoint questions, explain-back prompts, and short delayed reviews.
8. **Never claim perfect accuracy.** Report confidence and unresolved uncertainty.

## Trigger conditions

Use this skill when requests resemble:
- “Teach me how X works visually.”
- “Turn this topic into a simulation.”
- “Build an interactive explainer.”
- “Help me understand this system end-to-end.”
- “Make me a learning game for this concept.”
- “I keep reading this but it is not clicking.”
- “Visualize what happens inside X.”

Do not default to this skill for a simple factual question, a single static chart, or a topic where interaction does not improve understanding.

## Multimodal intake contract

The learner may supply text, images, video, or a mixture. Treat uploads as **evidence inputs**, not as automatic truth.

### Image uploads

For every image:
- Inspect the full image before focusing on crops.
- Record the asset ID and relevant visible region for each observation.
- Separate `OBSERVED` (directly visible) from `INFERRED` (interpretation).
- Preserve diagrams, labels, UI state, axes, legends, annotations, and spatial relationships.
- If tiny text is materially important and cannot be read reliably, say so rather than inventing it.

### Video uploads

For every video:
- Inspect it as a timeline, not one blob.
- Start with representative timestamped keyframes and available metadata/transcript.
- If an important state change occurs between sampled frames, extract or request denser frames around that interval.
- Maintain provenance as `video asset → timestamp → frame → observation → interpretation`.
- Distinguish demonstration-specific behavior from general claims about how a system works.
- When audio/transcript is available, keep spoken claims timestamped and reconcile them with visible evidence.

### Media-derived learning

Uploads can be used to:
- infer the topic when the user provides none;
- reconstruct a demonstrated workflow;
- turn a static diagram into an executable model;
- turn a screen recording into a state-machine or causal walkthrough;
- locate misconceptions or missing transitions;
- reproduce the teaching pattern while replacing the original subject matter.

Never claim a semantic conclusion was computed locally if only deterministic keyframes/metadata were extracted.

## Workflow

### Phase 1 — Define the learning target

Create a compact learning contract:
- Topic.
- Target depth: intuitive / practitioner / interview / academic / expert refresher.
- Prerequisites.
- What the learner should be able to **predict, calculate, diagnose, or explain** after the simulation.
- Scope boundaries: what is deliberately excluded.

If the user did not specify a level, infer the least-simplified level that matches their context and state the assumption.

### Phase 2 — Build the evidence map

First build a **media observation ledger** for all uploads, then research the mechanism before designing visuals. Media observations must retain asset/timestamp provenance and keep direct observation separate from interpretation.

Prefer sources in this order where possible:
1. Primary documentation, standards, textbooks, papers, official technical references.
2. High-quality university or institutional material.
3. Reputable engineering explainers.
4. Community material only for implementation experience or intuition, not core facts.

Create an internal evidence table:
- Claim or mechanism step.
- Supporting source.
- Confidence.
- Disagreement or variability.
- Whether it is safe to simplify.

Do not let one model “verify itself” count as verification.

### Phase 3 — Extract the causal model

Represent the topic as:
- **Entities** — what exists.
- **State** — what each entity can hold or become.
- **Inputs** — what enters the system.
- **Transformations** — what changes state.
- **Constraints** — limits and invariants.
- **Outputs** — what leaves or is observed.
- **Feedback loops** — what recurs.
- **Failure modes** — what can go wrong.
- **Observables** — what should be displayed numerically or visually.

Write the real mechanism independently of the renderer. If the animation layer disappeared, the model should still be understandable and testable.

### Phase 4 — Choose the simulation grammar

Pick the visual metaphor that preserves the mechanism best:

- **Factory / isometric town**: manufacturing pipelines, transformer layers, ETL, request lifecycles.
- **State-machine map**: protocols, auth flows, distributed systems, workflow engines.
- **Circuit / signal path**: electronics, control systems, sensor fusion, neural computation.
- **Agent field**: swarms, markets, epidemiology, queues, traffic, multi-agent systems.
- **Timeline / causal sandbox**: economics, historical systems, project operations.
- **Robot world**: perception → planning → control → actuation loops.
- **Layer stack / microscope**: chips, graphics pipelines, neural nets, materials.

Use 3D only when depth itself teaches something. Prefer 2D/isometric if it communicates the model more clearly.

### Phase 5 — Design active learning interactions

A valid simulation contains at least four of these:

1. **Predict-next** — learner predicts the next state before it is revealed.
2. **Parameter sandbox** — change a meaningful variable and observe consequences.
3. **Failure injection** — disable or corrupt a component and diagnose the effect.
4. **Checkpoint retrieval** — answer a question from an earlier stage without rereading.
5. **Counterfactual** — “What if this component/step did not exist?”
6. **Explain-back** — learner explains the mechanism, then receives targeted correction.
7. **Trace mode** — inspect the exact state carried between stages.
8. **Compare mode** — compare two algorithms, architectures, parameter sets, or scenarios.
9. **Challenge mode** — solve a realistic task using the model.
10. **Mastery revisit** — later checkpoints preferentially target concepts previously missed.

Do not make points, badges, or scoring the primary learning mechanism.

### Phase 6 — Build the fidelity ledger

The simulation must display an “Accuracy & Simplifications” panel.

For every meaningful model element, classify it:
- `COMPUTED` — generated by the real reduced-scale algorithm/model.
- `SOURCE-GROUNDED` — directly based on an external authoritative source.
- `SCALED` — real relationship, reduced dimensions/time/counts for usability.
- `ASSUMED` — reasonable value chosen because the real value varies or is unavailable.
- `ILLUSTRATIVE` — visual metaphor only; should not be interpreted literally.
- `UNKNOWN` — unresolved or disputed.

Include confidence and source references for high-impact claims.

### Phase 7 — Implement

Default implementation tiers:

**Tier A — portable explainer**
- HTML + CSS + vanilla JS.
- Canvas or SVG.
- No backend.
- Opens locally and deploys to a static host.

Use when the lesson is self-contained.

**Tier B — rich learning app**
- React / Next.js or Vite.
- Canvas/SVG; optional lightweight physics.
- Local persistence for learner progress.
- Componentized model/render/UI separation.

Use when there are many controls, comparison modes, saved progress, or multiple lessons.

**Tier C — model-backed lab**
- Frontend plus Python/Node simulation service.
- Real datasets, numerical models, or inference.
- Reproducible experiment presets.

Use when the concept requires heavy computation or real-world data.

In all tiers keep these layers separate:
- `model`: real mechanism/state transition logic.
- `scenario`: parameters and presets.
- `renderer`: visuals only.
- `lesson`: narration, questions, explanations.
- `assessment`: predictions, answers, misconceptions, mastery.

### Phase 8 — Validate

Before calling the work complete:
- Test the mechanism independently of rendering.
- Confirm every simulation stage corresponds to a real concept.
- Verify high-impact claims against external sources.
- Check controls at boundary values.
- Test restart, pause, step, speed, and navigation.
- Test mobile and desktop.
- Test reduced motion and keyboard use.
- Check that explanations do not get cut off by animation pacing.
- Review labels for overlap and visual occlusion.
- Confirm the fidelity ledger matches what the software actually does.
- Confirm every media-derived claim resolves back to an uploaded asset and, for video, a timestamp/frame.
- Review ambiguous video intervals at higher temporal density rather than guessing transitions.
- Run at least one misconception test: intentionally enter a common wrong assumption and verify that the simulation exposes why it fails.

### Phase 9 — Teach through the simulation

Use a three-pass lesson:

**Pass 1 — Guided model**
Narrate the journey slowly. Stop at each new mechanism and explain only what is needed to understand the current state.

**Pass 2 — Prediction run**
Repeat faster. Pause before major transitions and ask the learner to predict what happens.

**Pass 3 — Challenge run**
Change parameters or introduce faults. Ask the learner to diagnose and explain.

Finish with:
- A blank-sheet explain-back.
- Five retrieval questions.
- Two transfer questions applying the concept to a new scenario.
- A list of misconceptions still detected.

## Learning quality rubric

Score the result from 0–2 on each dimension:
- Mechanistic correctness.
- Source quality.
- Fidelity transparency.
- Causal manipulability.
- State visibility.
- Retrieval practice.
- Transfer questions.
- Accessibility and pacing.
- Mobile usability.
- Testability.

Do not consider the explainer finished below 16/20, and never ship with a zero for mechanistic correctness, source quality, or fidelity transparency.

## Output expectations

When asked to build a simulation, first provide a concise blueprint containing:
- Learning objective.
- Multimodal evidence summary and provenance plan when uploads exist.
- Mechanism model.
- Evidence plan.
- Visual metaphor.
- Interactions.
- Fidelity risks.
- Technical architecture.
- Validation plan.

When the runtime compiler is available, also emit a complete `simulation-spec.json` that includes at minimum:
- `title`, `objective`, `target_level`, `visual_grammar`
- `entities[]`
- base `state{}`
- `scenarios[]` when counterfactuals or failure injection matter
- ordered `stages[]` with `summary`, `focus_entities`, `state_patch`, `questions`, and `provenance` when relevant
- `fidelity_ledger[]`

The simulation spec should be directly compilable into a generic runtime so the mechanism becomes explorable without writing a bespoke app first.

Then implement rather than stopping at the blueprint when the environment allows implementation.

## Anti-patterns

Reject or fix these:
- A beautiful animation driven entirely by pre-scripted frames.
- “The AI reviewed it, therefore it is accurate.”
- A visual metaphor that changes the real order or causality.
- A learner who can only press Play.
- Quiz questions that merely repeat labels shown one second earlier.
- Fake precision.
- Hidden assumptions.
- 3D complexity that makes the mechanism harder to inspect.
- Long narration unrelated to current visible state.
