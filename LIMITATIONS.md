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

## `bls-census` SSA life tables are unreachable from datacenter/cloud hosts

**Scope:** the `bls-census` empirical skill (`--ext empirical`), specifically `ssa_period_life_table()`. BLS, ACS, and CPS paths of the skill are unaffected.

**Failure mode:** `ssa.gov` sits behind Akamai bot protection that returns HTTP 403 to datacenter/cloud IP ranges even with a browser User-Agent. The autonomous pipeline typically runs on exactly such hosts, so `ssa_period_life_table()` will *reliably* fail in the default deployment environment — any paper whose design needs SSA mortality/retirement-age tables (cohort survival weighting, actuarial discounting) cannot source them through this skill when run autonomously. The helper fails loud (a `RuntimeError` naming the cause, not a silent empty frame) and the BLS/Census paths still work, so the failure is contained, not corrupting — but the data is genuinely unavailable on the affected hosts.

**What would close it:** (a) route SSA fetches through a residential/allowlisted proxy or a pipeline-level fetch service whose egress IP is not Akamai-blocked; or (b) vendor the small set of SSA OACT period/cohort life tables as static CSVs into `extensions/empirical/utils/` (they update ~annually and are public-domain), and have `ssa_period_life_table()` prefer the local copy, falling back to the live scrape only for refresh. Option (b) is the robust fix and removes the network dependency entirely.

**Tracking:** no issue yet — file one if a paper design actually requires SSA tables. Until then this is documented-and-deferred per `CLAUDE.md`.

**Interim behavior:** documented in the skill body (`templates/skill_bodies/empirical/bls-census.md`, "SSA period life table" section + `## Rules`) and the helper docstring; `ssa_period_life_table()` raises a clear `RuntimeError` on the 403 rather than returning bad data; the skill's test treats SSA as best-effort (PASS on data, SKIP on the documented 403) so it never produces a false test failure.
