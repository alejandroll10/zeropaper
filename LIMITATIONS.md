# LIMITATIONS

Known architectural limits in the pipeline. Each entry: failure mode, what would close it, tracking issue.

Per `CLAUDE.md` ("no unsolved or undocumented architectural limits"), additions go here when a limit is identified during a pipeline edit but not closed in the same pass.

---

## Macro empirical work has no identification gate

**Scope:** the `macro` variant, and any future `macro_empirical` variant or macro `--ext empirical` flow.

**Failure mode:** when the empirical extension is enabled for macro work, `empiricist` and `empirics-auditor` audit data, code, and methodology, but no agent gates **identification design**. A macro empirical paper can therefore reach Stage 6 with an under-specified SVAR identification scheme, an HFI surprise series that ignores the information effect / Bauer-Swanson predictability critique, narrative shocks without an exclusion argument, or a calibrated DSGE whose parameters are not actually identified by the chosen targets — and the pipeline will not catch this until referee-mechanism. Identification mistakes caught at the referee are expensive (a Major-Revision cycle minimum) compared to catching them at the plan stage.

**Asymmetry with finance:** the finance variant has `identification-designer` + `identification-auditor` (see `extensions/empirical/agent_bodies/finance/`) wired into Stage 3a step 3, which gates the empirical plan on identification before execution. These agents are deliberately finance-only: they apply applied-micro / labor-style identification standards (heterogeneity-robust DiD, Olea-Pflueger weak-IV, robust bias-corrected RD, Cinelli-Hazlett OVB sensitivity, Feng-Giglio-Xiu factor-zoo test) that would mis-flag standard macro practice. A top macro referee will accept a calibrated DSGE without a micro-style identification strategy when calibration is the accepted standard for the question; the finance auditor would (wrongly) FAIL it.

**What would close it:** add `templates/agents/macro/identification-designer.md` and `templates/agents/macro/identification-auditor.md` with the macro toolkit — SVAR identification (recursive, long-run, sign restrictions, narrative sign restrictions); HFI around FOMC/ECB windows with Jarociński-Karadi info-shock decomposition and Bauer-Swanson orthogonalization; LP-IV (Stock-Watson, Ramey); narrative shocks (Romer-Romer monetary/tax, Ramey military, Hamilton/Kilian oil); identification through heteroskedasticity (Rigobon); and an explicit allowlist for calibration-as-identification when the macro literature treats it as the standard. Wire into whatever empirical macro flow exists at the time. Update both `extensions/empirical/agent_metadata/macro_agents.json` and the macro-side stage docs.

**Tracking:** [issue #18](https://github.com/alejandroll10/zeropaper/issues/18). Blocked on (a) finance pair shipping first so the architecture is settled (#17), and (b) empirical macro tooling existing in the macro variant (currently the macro variant is theory-only).

**Interim behavior:** the finance `identification-designer` and `identification-auditor` both return `OUT-OF-SCOPE` if the plan invokes a macro-style design — they do not silently apply finance standards to macro work. The orchestrator's step-3 handling in `extensions/empirical/docs/stage_3a_empirical.md` flags `OUT-OF-SCOPE` for the macro variant and either reframes the empirical work as descriptive / model-fit or escalates.

---

## Faithful-mode contribution-drift check is orchestrator-self-performed — CLOSED (#29)

**Scope:** `--faithful` runs (all variants/extensions).

**Failure mode:** the `--faithful` "frozen" guards (contribution `Headline:` sentence and stated results are contract-immovable; publishability/editor-driven re-headlining → `[RESPONSE]`; results not re-derived away) are enforced by the **orchestrator comparing the current draft against the contract's `Headline:` sentence**. The orchestrator is the same agent that, under plateau/referee pressure, has the incentive to rationalize a drift as a within-contribution reorganization. This is a self-referential check: an orchestrator that drifts can also mis-classify its own drift as compliant. The `victori-faithful-1` run is the witnessed instance — an editor-directed contribution re-headline ("bounded-attribution design as contribution") was routed as `[FIX]`, shipped at pipeline `COMPLETE`, and only an operator commit restored the seed framing.

**Mitigation in place (not closure):** the contract now carries a single verbatim `Headline:` sentence (faithful.md Step 0) so the check is anchored to a near-string-level referent rather than fuzzy prose; the routing table, Gate-5 and Gate-4 overrides, and the developing-agent inject pointer all reference that one sentence; MISATTRIBUTED/DECORATIVE are the sole authorized in-place `Headline:` updates and must write back to `mechanism_contract.md`. This narrows but does not eliminate the self-referential gap — classification of "publishability-driven vs correctness-driven demotion" is still an orchestrator judgment.

**Closure:** the external `faithful-drift-auditor` shared evaluator agent (body `agent_bodies/shared/faithful-drift-auditor.md`, metadata `category: evaluator`, `pipeline_only`) is now launched at Gate 4 (plateau-ship rule) and Gate 5 (ship gate). It independently compares the paper's headline contribution and stated results against the live `Headline:` line in `mechanism_contract.md` and emits `DRIFT` / `NO-DRIFT` to `output/seed/drift_audit_gate{N}_r*.md`; the orchestrator cannot author the verdict, and `DRIFT` is a non-bypassable restore-gate (re-audit until `NO-DRIFT` before advancing/shipping). As an evaluator it does not receive the faithful inject pointer. This applies the same impartial-evaluator pattern faithful mode uses for scorer/referee.

**Residual (accepted, bounded):** the orchestrator still *executes* the restore action and re-launches the auditor; a maximally adversarial orchestrator could in principle ignore the verdict. This is the identical residual already accepted for every faithful evaluator (scorer/referee/math-auditor) — the verdict is independent and on-disk, so the failure is detectable post-hoc rather than self-rationalized silently. Not separately tracked.

**Tracking:** [issue #29](https://github.com/alejandroll10/zeropaper/issues/29) — closeable; both the v1 "faithful = frozen" patch and this external-agent upgrade are shipped.
