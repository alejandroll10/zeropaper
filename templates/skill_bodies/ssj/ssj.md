## What this is

The **sequence-space Jacobian (SSJ)** method as a capability for the pipeline's theory work. It wraps the official `sequence-jacobian` package (Auclert, Bardóczy, Rognlie, Straub, *Econometrica* 2021) so the theory agents can **solve and analyze heterogeneous-agent general-equilibrium (HA-GE) models** — a question class that sympy and codex-math cannot touch, because it requires the time-dimension linear algebra (general-equilibrium Jacobians via the fake-news algorithm, impulse-response solving, determinacy) that is infeasible by hand.

The division of labor: **you supply the economics** (the heterogeneous-agent block, the simple blocks for firms/prices/market-clearing, and the calibration, written as a Python module); the driver at `code/utils/ssj/ssj_solve.py` runs the standardized pipeline:

```
load module -> steady state -> GE Jacobians -> determinacy -> IRFs -> plots
```

A worked finance example ships at `code/utils/ssj/example_asset_pricing.py` (heterogeneous-agent asset pricing: wealth distribution -> risk-premium impulse response).

## What it unlocks (new questions, not a checker)

SSJ is a *generative* capability — it lets the pipeline pose and answer questions that are out of reach for representative-agent theory:

- **Distributional general equilibrium**: how the cross-section of wealth/MPCs shapes equilibrium prices and aggregate dynamics.
- **Who-gains-who-loses**: the heterogeneous incidence of a shock or policy.
- **Heterogeneous-agent asset pricing** (finance): wealth distribution -> risk premia; household portfolio choice under aggregate risk; intermediary and term-structure models.
- **HANK / inequality-and-business-cycle** (macro): the workhorse models of the current frontier.

If the candidate theory is fundamentally about *heterogeneity interacting with prices in GE*, this is the tool. If it is a representative-agent or partial-equilibrium model, it is not — use the normal theory tooling.

## When to use

- **`theory-explorer` (Stage 2b)** — the natural home. Once a theory with a heterogeneous-agent GE structure has passed the math audit, use SSJ to compute its GE Jacobians, trace impulse responses, check determinacy, and probe robustness across calibrations.
- **`idea-prototyper` (tractability pre-check)** — if a candidate idea hinges on an HA-GE mechanism, a quick SSJ steady-state + Jacobian confirms the model actually solves and the headline comparative dynamic has the claimed sign *before* committing to full theory development. If the steady state won't solve or the IRF has the wrong sign, that is a concrete BLOCKED finding — BLOCKED-DIFFICULTY unless the barrier is provably fundamental (BLOCKED-IMPOSSIBLE), per the prototyper's verdict rules.

## The model module contract

Your model module must expose a single function `dag()` returning a dict:

```python
def dag():
    ...
    return {
        "model":    model,           # CombinedBlock: the dynamic model (Jacobians / IRFs)
        "ss":       ss,              # SteadyStateDict: already solved
        "unknowns": ["K"],           # GE unknown path(s)
        "targets":  ["asset_mkt"],   # GE equilibrium condition(s)
        "inputs":   ["Z"],           # exogenous shock(s)
        "report_outputs": ["r","K","C","Y"],          # (optional) what to print/plot
        "shocks":   {"Z": {"rho": 0.8, "size": 0.01}}, # (optional) AR(1) shock config
    }
```

Solve the steady state *inside* `dag()` — typically by building a second,
SS-inverted model (`model_ss` in the example) and calling its
`solve_steady_state` — and return only the solved `ss`. The driver consumes
`ss`, not the SS model, so `model_ss` is a local of your `dag()`, not a contract key.

Then run:

```bash
python code/utils/ssj/ssj_solve.py code/utils/ssj/example_asset_pricing.py --T 300
# options: --shock NAME  --rho R  --size S  --out DIR  --no-plot  --skip-determinacy
```

Outputs land in `output/ssj/` (`irf.csv`, `irf.png`).

## The workflow (what the driver does, and what you must get right)

1. **Define blocks.** A `@het` block is the household problem (backward iteration for policies, forward iteration for the distribution); `@simple` blocks are firms, prices, and market clearing. Reuse the package's shipped household blocks (`sequence_jacobian.hetblocks.hh_sim`, `hh_labor`, `hh_twoasset`) when one fits — the example uses `hh_sim` (one-asset SIM household).
2. **Steady state.** Use the standard SSJ inversion trick: write a separate `firm_ss`-style `@simple` block that *inverts* the firm FOCs to back out structural parameters from steady-state targets, so the steady-state solve has as few unknowns as possible (the example reduces it to a single unknown, the discount factor `beta`). `model.solve_steady_state(calibration, unknowns, targets, solver="brentq")`.
3. **GE Jacobians.** `model.solve_jacobian(ss, unknowns, targets, inputs, outputs=..., T=...)` returns the general-equilibrium Jacobian map `G[output][input]` — the dynamic response of every output to every shock, *after* imposing market clearing. This is the fake-news/SSJ payoff: the cross-sectional household responses are aggregated and fed through GE in one linear solve.
4. **Determinacy.** The driver computes the winding number of `det H_U` (the Jacobian of targets w.r.t. unknowns) and reports DETERMINATE / INDETERMINATE. See the limitation note below.
5. **IRFs.** For an AR(1) shock path `dZ`, the impulse response of output `o` is `G[o][shock] @ dZ`. The driver writes `irf.csv` and `irf.png`.

## Worked finance example: wealth distribution -> risk-premium IRF

`example_asset_pricing.py` is the canonical Krusell–Smith incomplete-markets economy **read as an asset-pricing model**: physical capital is the single risky asset, its return `r` is the asset price, and an aggregate-productivity (`Z`) shock is the aggregate risk. Households face uninsurable idiosyncratic income risk and save in the capital claim, so the equilibrium return is pinned down by the *wealth distribution* (precautionary savers bid it down) and its impulse response is shaped by the cross-section of MPCs — the object a representative-agent asset pricer cannot produce. Running it yields a positive on-impact jump in `r` to a positive `Z` shock that mean-reverts as capital accumulates, a DETERMINATE verdict, and the IRF plot.

### Extending to an explicit equity premium

To price an explicit risky-vs-riskless spread, add a riskless bond in zero net supply and a second market-clearing condition. The sequence-space workflow is unchanged — one more unknown, one more target. A two-asset household (`hetblocks.hh_twoasset`) gives portfolio choice between a liquid and an illiquid asset.

## Gotchas (read before you debug)

- **Blocks must live in a real `.py` file.** `sequence-jacobian` discovers each block's outputs by running `inspect.getsource()` and regex-matching the `return` line. Blocks defined in a REPL, a `python -c` one-liner, a heredoc piped to stdin, or `exec()` fail with `OSError: could not get source code`. Always write the model to a module on disk and run the driver against it (the driver imports from disk, which is fine).
- **`numba` is a heavy, finicky dependency.** The package itself declares *no* dependencies, so an unpinned install can backtrack to an ancient `numba` that is incompatible with modern Python and fail to build. setup.sh installs `sequence-jacobian numpy scipy "numba>=0.59"` explicitly for this reason. If imports fail in a deployed project, reinstall with that explicit pin. The install is **non-fatal** — a numba hiccup warns but never breaks setup, so on a host where numba won't build, this skill is simply unavailable (like the codex CLI when absent).
- **The `return` line is parsed literally.** Keep each block's `return a, b, c` on one line with the output names you intend; the package reads those names as the block's outputs.
- **Steady-state solver bracketing.** `brentq` needs a bracket that actually contains a sign change; if the steady state won't solve, widen the unknown's `(lo, hi)` bracket or sanity-check the inversion block.
- **The determinacy step recomputes the partial Jacobians.** To assemble `H_U`, the driver calls `model.jacobian(...)` independently of the cache `solve_jacobian` builds internally, so the expensive het-block Jacobian (backward/forward iteration over the distribution) runs twice. On large models (`nA >= 200`) this roughly doubles runtime. If that matters, pass `--skip-determinacy` and rely on the corroborating signal: `solve_jacobian` factorizes `H_U` and fails loudly if it is singular, so a successful Jacobian solve already implies `H_U` is invertible (a locally unique solution).

## Determinacy: scope and limitation (documented, not hidden)

The winding-number determinacy check (`winding_number_determinacy` in `ssj_solve.py`) implements the Onatski (2006) / Auclert et al. (2021, Appendix) criterion: the model is determinate iff the winding number of `det A(λ)` around the unit circle is zero, where `A(λ)` is the symbol of the (asymptotically Toeplitz) Jacobian `H_U`. It is exact for the common single-unknown case and reliable for interior multi-unknown systems. **Known limitation:** it recovers the symbol from the *central* block-diagonals of the truncated `H_U`, so it assumes the diagonals have converged (it warns if `T < 50`) and it is **fragile near a determinacy boundary** (a knife-edge model). Corroborating signals: `solve_jacobian` factorizes `H_U` and will fail loudly if `H_U` is singular (non-existence / boundary indeterminacy). For a definitive verdict on a model deliberately sitting near the boundary, confirm with the hand calculation in Auclert et al. (2021, Appendix B). Do not report a near-boundary determinacy result as settled on the winding number alone.

## Output locations

| Artifact | Path |
|----------|------|
| IRF table | `output/ssj/irf.csv` |
| IRF plot | `output/ssj/irf.png` |
| Worked example model | `code/utils/ssj/example_asset_pricing.py` |
| Driver | `code/utils/ssj/ssj_solve.py` |
