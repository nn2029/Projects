# Master Prompt — Build a Learning Simulation

Use the `simulation-learning-lab` skill.

Topic: [TOPIC]
Target learner: [LEVEL / BACKGROUND]
Outcome: By the end, I should be able to [PREDICT / EXPLAIN / DIAGNOSE / CALCULATE].

Build this as a source-grounded interactive learning simulation, not a decorative animation.

Requirements:
1. Research the mechanism using authoritative sources and build an evidence map before coding.
2. Model the real state transitions independently of the renderer.
3. Choose a visual metaphor that preserves causality; do not force an isometric city if another representation is clearer.
4. Show the state being carried through the system.
5. Include play/pause, step, reset, speed, and direct navigation where relevant.
6. Include at least four active-learning interactions: predict-next, parameter sandbox, failure injection, checkpoint retrieval, counterfactual, explain-back, trace, compare, challenge, or mastery revisit.
7. Publish an Accuracy & Simplifications panel classifying important elements as COMPUTED, SOURCE-GROUNDED, SCALED, ASSUMED, ILLUSTRATIVE, or UNKNOWN.
8. Never describe the output as perfectly accurate. Surface uncertainty and disagreements.
9. Separate model, renderer, lesson, scenario, and assessment logic.
10. Verify mechanics, claims, mobile layout, accessibility, and controls before reporting completion.

Before implementation, show me a compact blueprint with:
- learning objective
- causal/mechanism model
- evidence plan
- visual metaphor
- interactions
- fidelity risks
- architecture
- validation plan

Then implement it fully.
