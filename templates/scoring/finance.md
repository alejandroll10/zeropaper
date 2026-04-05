## Scoring criteria (used by scorer agent)

### Hard requirements (binary PASS/FAIL)

| # | Requirement |
|---|------------|
| H1 | One clear idea — contribution statable in one sentence |
| H2 | Well-defined setup — a reader can write down the agents' problem |
| H3 | Key result is mathematically correct (math audit passed) |
| H4 | The result is new (novelty check passed) |
| H5 | Economic mechanism is clear — why the result holds, in economics not algebra |

### Scored dimensions

| Dimension | Weight | Calibration |
|-----------|--------|-------------|
| Importance | 30% | CAPM-level = 100, minor extension = 20 |
| Novelty | 15% | New mechanism = 100, known mechanism in new setting with surprising implication = 80, known mechanism in new setting with predictable implication = 40 |
| Surprise | 15% | Sign reversal or existence result no one expected = 100, non-obvious comparative static = 60, confirms intuition with precise conditions = 40, formalizes what everyone already believed = 15 |
| Rigor | 20% | Full proof = 100, clear with small gaps = 60, hand-waving = 20 |
| Parsimony | 10% | One-friction model = 100, kitchen-sink = 20 |
| Fertility | 10% | Reframes a literature = 100, dead-end result = 20 |

Threshold to advance: 75+
