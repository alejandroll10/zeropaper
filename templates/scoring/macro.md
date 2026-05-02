## Scoring criteria (used by scorer agent)

### Hard requirements (binary PASS/FAIL)

| # | Requirement |
|---|------------|
| H1 | One clear idea — contribution statable in one sentence |
| H2 | Well-defined setup — a reader can write down the equilibrium (agents' problems, market clearing, equilibrium concept) |
| H3 | Key result is mathematically correct (math audit passed) |
| H4 | The result is new (novelty check passed; INCREMENTAL triggers Gate 3 cross-check — see scorer for details) |
| H5 | Economic channel is clear — why the result holds, in terms of economic forces not algebra |

### Scored dimensions

| Dimension | Weight | Calibration |
|-----------|--------|-------------|
| Importance | 30% | What decision/belief changes if true? Must name it. 100 = changes a first-order policy decision routinely made, 70 = sharpens a specific policy trade-off in a specific context, 55 = formalizes something roughly believed, 40 = internally interesting but no decision changes, 20 = minor extension of NK |
| Novelty | 15% | New channel/mechanism = 100, known channel in new setting with surprising implication = 80, known channel in new setting with predictable implication = 40 |
| Surprise | 20% | Sign reversal or existence result no one expected = 100, non-obvious comparative static or multiplicity = 60, confirms intuition with precise conditions = 40, formalizes what everyone already believed = 15 |
| Rigor | 15% | Full equilibrium characterization with stated assumptions + both audits passed = 80 (default), boundary behavior characterized for main result = 100, gaps a reader would notice = 60, hand-waving = 20 |
| Parsimony | 10% | Tractable GE with one key friction, every assumption load-bearing = 100, one or two robustness extensions = 80, multiple non-load-bearing extensions = 60, kitchen-sink DSGE = 20. Assumptions added to address audits but not used in main proof count against. **Exception: scope conditions that reflect a genuine mathematical necessity surfaced by the math audit or theory-explorer do NOT count against parsimony — they are Rigor.** |
| Fertility | 10% | Reframes a literature or changes policy thinking = 100, dead-end result = 20 |

Threshold to advance: tier-dependent — see `docs/stage_4.md` tier table (defaults: `top-5` 80+, `field` 65+, `letters` 55+).

**Scope integrity (applies across dimensions; any theory version after v1, including within-Gate-2 iterations).** If the current version removed a claim that was unverified or falsified in a prior version, or narrowed an over-broad theorem to its proved scope, treat this as positive — credit +Rigor (accurate characterization) rather than -Parsimony or -Surprise (narrower claim). Honest scope narrowing is a gain, not a loss. Does not apply at v1 (no prior version exists).
