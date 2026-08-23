# Multimodal Evidence Ledger

Use this before converting an upload into a causal model.

| ID | Asset | Time / region | OBSERVED | INFERRED | Confidence | Needs external verification? | Used in simulation? |
|---|---|---|---|---|---:|---|---|
| M-001 | video-abc | 00:42 | UI changes from pending to retrying | Retry worker was triggered | 0.76 | Yes | Yes |

## Rules

- `OBSERVED` contains only what can be directly supported by the upload.
- `INFERRED` may contain interpretation, but uncertainty must remain visible.
- A video claim needs a timestamp or timestamp range.
- If a key transition is missing between samples, densify that interval before filling the row.
- An image claim should specify a visible region when the location matters.
- General technical claims should not inherit truth merely because a demo or diagram depicts them.
