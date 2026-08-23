# Simulation Patterns

Use this reference to select an interaction model quickly.

| Topic shape | Good simulation pattern | State to expose | Useful challenge |
|---|---|---|---|
| Sequential manufacturing | Factory / transport route | material form, quality, cost, time | identify bad stage from output defect |
| Algorithm | Stepper / state machine | arrays, vectors, queue, stack, weights | predict next state |
| Networking | Packet journey | headers, latency, congestion, retries | inject loss/cache miss/timeout |
| Distributed systems | Nodes + message graph | term, log, quorum, leader state | partition a node and diagnose |
| Robotics | Perception-planning-control world | sensor estimates, map, path, command | add sensor noise / blocked route |
| ML / LLM | Token/vector pipeline | tokens, embeddings, activations, attention | change context/temperature/mask |
| Economics | Agent/flow sandbox | supply, demand, inventories, rates | apply shock and explain second-order effect |
| Physics | Parameterized scene | forces, energy, momentum, field values | predict motion before run |
| Cybersecurity | Trust-boundary map | identity, tokens, privileges, events | introduce misconfiguration and trace blast radius |
| Databases | Query/data journey | plan nodes, pages, rows, cache | add index / skew / cache miss |

## Visual choice rule

Do not choose a city/factory merely because it looks attractive. Choose it only if geography encodes sequence, grouping, repetition, scale, or ownership. If not, use a more direct visualization.
