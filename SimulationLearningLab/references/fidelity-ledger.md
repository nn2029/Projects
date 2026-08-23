# Fidelity Ledger Template

Every simulation should expose this to the learner.

| Element | Classification | What is real | What is simplified | Confidence | Source |
|---|---|---|---|---|---|
| Example: attention weights | COMPUTED | scaled dot-product attention | tiny dimension/head count | High | paper/docs |
| Example: factory cycle time | ASSUMED | order of operations | representative timing only | Medium | source |
| Example: building appearance | ILLUSTRATIVE | station identity | visual form not literal | High | n/a |

## Classification rules

- `COMPUTED`: the software performs the actual relevant operation, even at reduced scale.
- `SOURCE-GROUNDED`: the behavior is directly encoded from referenced material but not numerically simulated.
- `SCALED`: the relation is faithful but count, size, duration, or dimension is compressed.
- `ASSUMED`: selected representative value that should not be treated as universal.
- `ILLUSTRATIVE`: a visual storytelling device only.
- `UNKNOWN`: the project does not currently have enough evidence.

Never use a number without deciding which class it belongs to.
