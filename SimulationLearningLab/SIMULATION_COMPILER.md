# Simulation Compiler and Runtime

## Purpose

The simulation compiler turns a structured lesson specification into a runnable interactive learning artifact.

It exists to prevent every lesson from requiring a bespoke frontend implementation.

## Input

A JSON object with the validated simulation spec shape.

## Output

A compiled bundle inside the session folder:

- `compiled/index.html`
- `compiled/simulation-spec.json`
- `compiled/runtime.js`
- `compiled/runtime.css`

## Compiler stages

1. Validate structural correctness.
2. Normalize defaults.
3. Attach theme defaults based on `visual_grammar`.
4. Persist the spec.
5. Copy runtime assets.
6. Generate a self-contained HTML entrypoint.
7. Update the session manifest to reflect compiled status.

## Current runtime feature set

- guided stage progression;
- scenario switching;
- cumulative state inspection;
- stage-specific provenance cards;
- multiple-choice and text-answer prompts;
- fidelity ledger display.

## Design choice

The runtime is intentionally less visually ambitious than a handcrafted explorable explanation.

Its job is portability and speed: once an AI produces a valid mechanism model, the learner should immediately have something they can inspect, click through and test.

After that, higher-fidelity custom renderers can be built for specific grammars.
