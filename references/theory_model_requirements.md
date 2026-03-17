# Requirements for a Finance Theory Model

Scoring criteria for the adversarial scorer. Calibrated against what actually gets published, not what a textbook says a model should look like.

---

## What the canonical papers actually look like

The bar is set by papers like these:

- **Mean-variance (Markowitz 1952)**: One idea — investors care about mean and variance. No utility function. Setup fits on one page. Changed portfolio theory forever.
- **CAPM (Sharpe 1964)**: Mean-variance + equilibrium. One equation: E[R] = Rf + beta * (E[Rm] - Rf). No existence proof. No formal propositions in the modern sense.
- **APT (Ross 1976)**: No-arbitrage + approximate factor structure → linear pricing. Doesn't fully specify preferences. The insight is that arbitrage alone disciplines prices.
- **Optimal debt contract (Townsend 1979, Gale-Hellwig 1985)**: One friction (costly state verification). One result: optimal contract is standard debt. Clean, minimal.
- **Modigliani-Miller (1958)**: No frictions → capital structure irrelevant. The theorem is what DOESN'T matter, which tells you what DOES.

### Common pattern
1. One clean idea that fits in a sentence
2. Minimal setup — only what's needed for the result
3. One key result that changes thinking
4. The math serves the idea, not the other way around

### What they DON'T have
- Exhaustive specification of every primitive
- Formal existence/uniqueness proofs (usually)
- Specific functional forms (often general preferences)
- 12 propositions covering every case

---

## The three things that matter (from JFE referee guidelines)

The JFE tells referees to evaluate three things:

1. **Is the question of sufficiently broad interest?**
2. **Does it make a sufficient leap over existing literature?**
3. **Is the analysis correct?**

That's it. Everything else is secondary.

---

## Hard requirements (binary — any failure kills the theory)

| # | Requirement | Why |
|---|------------|-----|
| H1 | **One clear idea** | Can you state the contribution in one sentence? If not, the paper doesn't know what it is. |
| H2 | **Setup is well-defined** | A reader can write down the agents' problem. Doesn't need every primitive listed — but the problem must be solvable as stated. |
| H3 | **Key result is correct** | The main result follows from the setup. No logical gaps in the core argument. (Side results can have gaps — the core cannot.) |
| H4 | **The result is new** | Not a known result repackaged, not a trivial extension. Must pass a literature check. |
| H5 | **Economic mechanism is clear** | Why does the result hold? Answer must be economics, not algebra. A reader who skips the math understands the contribution. |

Five requirements, not twelve. A paper that satisfies these five is potentially publishable. A paper that fails any one is not.

---

## Scored dimensions

| Dimension | Weight | What's scored | Calibration |
|-----------|--------|---------------|-------------|
| **Importance** | 30% | Does the question matter? Would anyone change behavior/thinking based on this result? | CAPM = 100, minor extension of existing model = 20 |
| **Novelty** | 25% | How new is the insight? Not the technique — the economic insight. | New mechanism = 100, known mechanism in new setting = 40 |
| **Rigor** | 20% | Is the core argument airtight? Are boundary cases acknowledged? | Full proof = 100, clear argument with acknowledged gaps = 60, hand-waving = 20 |
| **Parsimony** | 15% | Is this the simplest model that generates the result? Could any assumption be dropped? | One-friction model = 100, kitchen-sink model = 20 |
| **Fertility** | 10% | Does the model open new questions? Suggest new empirical tests? Nest existing results? | Reframes a literature = 100, dead-end result = 20 |

### Why this weighting

- **Importance is king.** A correct, novel, elegant result about something nobody cares about won't get published. The question must matter.
- **Novelty before rigor.** A rough but genuinely new idea beats a polished but incremental one. Rigor can be fixed in revision; lack of novelty cannot.
- **Parsimony over completeness.** The scorer should penalize complexity. If the model has 5 frictions, ask: which one drives the result? The other 4 are noise.
- **Fertility is a bonus.** Some papers open entire literatures (CAPM, MM). Most don't. But a paper that suggests follow-up work is more valuable than a dead end.

---

## Aggregate scoring

`total = 0` if any H1-H5 fails.

Otherwise: `total = 0.30 * importance + 0.25 * novelty + 0.20 * rigor + 0.15 * parsimony + 0.10 * fertility`

### Thresholds

| Score | Decision |
|-------|----------|
| 75+ | Advance to paper writing |
| 55-74 | Revise and re-evaluate (max 2 rounds) |
| 35-54 | Major rework — return to theory generation with specific feedback on what's weak |
| <35 | Abandon this theory, start fresh with different idea |

---

## What the scorer must NOT do

1. **Don't demand exhaustive primitives.** If the paper says "risk-averse investors" and the result holds for any concave utility, demanding CRRA is wrong. General is better than specific when the result is general.

2. **Don't require existence/uniqueness proofs.** Many published papers solve for equilibrium constructively without a separate existence theorem. If you can find it, it exists.

3. **Don't penalize for not having testable predictions.** Some pure theory contributions (characterization theorems, impossibility results, mechanism design) are valuable without empirical implications. Score fertility instead.

4. **Don't reward length or exhaustiveness.** More propositions ≠ better paper. One proposition that matters > ten that don't.

5. **Don't confuse generality with vagueness.** "For any increasing concave utility function" is precise. "Agents have some preferences" is vague. The scorer must distinguish.

---

## Asset pricing specifics

When evaluating asset pricing theory:

- **Benchmark**: No-arbitrage / SDF framework. The result should either work within this framework or explain why it departs.
- **Prices must make sense**: No arbitrage opportunities unless explaining why they persist (limits to arbitrage).
- **Risk premia have an economic reason**: Covariance with something that matters to agents.
- **Connection to observables**: Even without formal empirical work, the objects in the model (factors, portfolios, returns) should map to things we can measure.

Key question: **What risk is being priced, and why?**

## Corporate finance specifics

When evaluating corporate finance theory:

- **Benchmark**: Modigliani-Miller. What friction makes the result non-trivial?
- **Standard frictions**: Agency (moral hazard, adverse selection), taxes, bankruptcy costs, asymmetric information, incomplete contracts.
- **One friction at a time**: The best papers isolate one friction and show what it implies. Adding multiple frictions muddies the mechanism.
- **Contract/security design**: If the paper designs an optimal contract, it must specify the contracting environment (what's observable, what's verifiable, what's committable).

Key question: **What friction matters, and what does it imply for firm behavior?**
