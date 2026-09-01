# Changelog

All notable milestones of the autonomous research-paper pipeline template.

Versions follow [semantic versioning](https://semver.org/): **MAJOR** = a fundamental
change in what the pipeline *is*, **MINOR** = a new additive capability, **PATCH** = fixes.

This history was reconstructed retroactively from the git log (505 commits, Feb–Jul 2026)
and back-filled as annotated git tags on the anchor commits shown. Dates are the anchor
commit's authored date. The `VERSION` file at the repo root is the single source of truth
going forward; `setup.sh` stamps `<version>+<git-hash>` into every deployment.


> Note: the informal `v1`/`v2` labels in `CLAUDE.md` denote **variant maturity**
> (e.g. finance), a separate axis from this template version.

---

## [2.32.2] — 2026-09-01 (current)

**fix: require trigger-preserving debugger probes (#299).** Debugger hypothesis tests
must now preserve any request rate/count, ordering, concurrency, accumulated state, session
age, or workload size that could trigger the observed failure before treating an isolated
successful retry as contrary evidence. This closes the single-shot blind spot without adding
source-specific rules or duplicating debugging guidance across empirical stage documents.

## [2.32.1] — 2026-09-01

**fix: reserve the lifecycle-receipt suffix without blocking documentary snapshots (#294).**
The result registry still fails closed on every unknown `*results.receipt.json` file, but the
shared producer and evidence procedures now require byte-preserving documentary copies to use
`*results.receipt.snapshot.json`. The runner's preflight error names that repair directly, and
regression coverage proves the snapshot suffix is ignored while the lifecycle suffix remains
strict. This removes the recurring false-positive preflight failure without adding content-based
receipt equivalence or exempt filesystem zones.

## [2.32.0] — 2026-08-31

**feat: `results_pipeline run`/`run-empirical` refuse to start without a declared caller lifetime (#293).**
The fourth field occurrence (tradingdays v8/a30: a ~30-second child exec killed the trusted
runner during workspace setup, after that project's own a19 diagnostic had already prescribed
tracked-job launches) proved prompt-side knowledge does not survive across orchestrator turns.
`run` and `run-empirical` now require `--caller-allowance-seconds` — the invoking mechanism's real wall-clock
lifetime, minimum 1200 seconds — and refuses before any lock, transaction recovery, or
workspace work when it is absent or too small, with refusal text that carries the tracked-job
launch instructions. The startup banner names the requirement; every documented invocation
(results_evidence.md, stage_3a release run, empiricist/theory-explorer/experiment-designer
bodies) passes the flag via `CALLER_ALLOWANCE_SECONDS`. The declaration is honor-system by
construction — a caller can still overstate it — but it forces the duration contract into every
launch decision instead of relying on remembered doc text; #293 stays open for receipt-safe
acquisition checkpointing.

## [2.31.0] — 2026-08-31

**feat: make empirical specifications and result lineage machine-comparable.**
Empirical computations now use a parsimonious baseline/contract/execution-summary spine that
records reusable definitions, exact deviations, samples and filters, variables, procedure and
inference settings, adaptive choices, count flows, and result ownership without prescribing an
estimator taxonomy. `results_pipeline run-empirical` validates those records, emits receipt v3,
binds every result and displayed exhibit element to one analysis, freezes a receipt-qualified
comparison graph for paper audit, and keeps ordinary theory/LLM/release computation on receipt
v2. Historical comparison operands must belong to active or accepted replacement history; the
runner verifies their complete nested evidence closure and prevents retirement from stranding an
active dependent. The helper, schemas, empirical agents, manual/autonomous procedures, setup
ownership, CI, and all runtime assembly shapes ship the same contract.

## [2.30.12] — 2026-08-28

**fix: `results_pipeline run`/`render` announce their duration contract at startup (#293).**
The #293 failure mode recurred in the field despite v2.30.8's doc mandate — a fresh deployment's
empiricist killed a healthy producer three times with 30-second one-shot tool calls, seeing pure
silence because child output is buffered until completion. The runner now prints an immediate
unbuffered stderr banner on `run`/`render`: expected multi-minute duration, the tracked
long-allowance launch requirement, and that interim silence is normal — so even a killed short
call captures the explanation. The full mechanism gap (runner-owned allowance, receipt-safe
acquisition checkpointing) remains open in #293.

## [2.30.11] — 2026-08-27

**fix: shard ownership CI across independent target families (#290).**
The ownership integration harness now exposes four exhaustive shards while retaining its
single-process `all` mode. CI runs those shards as a fail-complete matrix on memory-backed
scratch space. Historical verification loads the reviewed current harness but points every
operation at the separately attested historical source checkout, so the test harness can be
parallelized without changing the source tree under test. Topology regressions bind the shard
set, historical harness selection, source root, and scratch policy.

## [2.30.10] — 2026-08-27

**fix: run confined CI producers with the sandbox-visible system interpreter (#290).**
GitHub's Python setup action installs its interpreter under `/opt/hostedtoolcache`, which the
production Bubblewrap namespace intentionally does not expose. The computed-results and
empirical-binding entry points now use `/usr/bin/python3` explicitly, so their child producers
execute inside the same confined filesystem the workflow probes. Topology tests bind both
sandboxed entry points to that interpreter.

## [2.30.9] — 2026-08-27

**fix: make attested historical-tree CI verification recoverable after a corrupted run (#290).**
The Dev instruction mirrors workflow now supports manual dispatch against an explicit full
commit SHA, and every constituent test job attests that its checked-out `HEAD` equals that same
target. The Actions run remains associated with the dispatch commit, so the logs record both
the run SHA and attested target SHA rather than claiming to replace a historical check suite.
A topology regression prevents future job splits from silently using the dispatch tree or
omitting the attestation. Normal push and pull-request checkouts retain their event defaults.

## [2.30.8] — 2026-08-27

**docs: mandate tracked long-allowance launches for `results_pipeline run` (#293).**
The `run` contract never told the invoking agent that producer runs are long; the runner has no
wall-clock allowance of its own, so a 30-second synchronous shell call silently destroyed a
legitimate ~20-minute acquisition on a live run (eventcal v6/a14) — total workspace loss by
design, one debug cycle wasted on a launcher-pattern mistake. `results_evidence.md`'s `run`
procedure now leads with the tracked-job mandate. The mechanism gap (runner-owned allowance,
receipt-safe acquisition checkpointing) is tracked in #293 with a LIMITATIONS entry.

## [2.30.7] — 2026-08-27

**fix: data-first releases enforce declared redistribution rights before publication.**
Stage 2 now emits an audited machine-readable source-rights inventory. Stage 3a builds the
public dataset in a separate offline, credential-free results run whose non-manifest inputs are
classified as data or the paired-analysis control; the trusted parent rejects restricted source
IDs, incomplete provenance, unlisted or
mischecksummed release files, and any ordinary networked analysis that targets `output/dataset/`.
The release plan is bound to Gate 2's accepted rights path, SHA-256, and current version in
autonomous deployments, or to an explicit caller authority under `--manual`; analysis
and release receipts activate or retire atomically with matching replacement lineage and remain
bound through Gate 4 and paper writing. Focused runner and assembly regressions protect the
release boundary. Addresses #282;
license interpretation and provenance truthfulness remain documented audit judgments.

## [2.30.6] — 2026-08-26

**fix: WRDS daemon wedged permanently by a deadline-less healthcheck on a half-open socket (#291).**
A transient upstream flap left `SELECT 1` blocking indefinitely inside `healthcheck()` while it
held the state lock, so every later ping reported the service unreachable with an empty auth
diagnostic and Stage 3a preflights halted a healthy host (observed three times in one day on a
live run). The daemon now installs libpq socket guards (TCP keepalives + `tcp_user_timeout`) at
first login, bounds the health probe with a real deadline recorded in the lock-owner metadata,
and reorders tier-2 recovery so a deadline expiry aborts pre-marker/pre-login as a timeout —
never as a false credential latch; after a spent-and-successful login, verification runs under a
fresh grace budget and extends the recorded owner deadline so concurrent pings stay truthful.
`psycopg2-binary>=2.9` floor added (older libpq hard-rejects `tcp_user_timeout`); the setup
fallback message now points at the requirements file instead of a flattened list that would
shell-mangle the pin. Three regression scenarios added to `test_wrds_auth_latch.sh`
([8a] slow-successful reconnect, [8b] expired deadline, [8c] sub-second deadline pre-marker
abort). Three review rounds; one-login-attempt invariant preserved throughout.

## [2.30.5] — 2026-08-26

**fix: data-first Stage 2 commits name the dataset specification.**
The versioned Stage 2 artifact commit label now resolves through the same layered vocab order
as agent assembly. Data-first renders `artifact: dataset spec v{N}` while every existing
variant and mode retains `artifact: theory draft v{N}` byte-for-byte; focused assembly checks
and full-tree characterization fixtures protect both paths. Closes #289.

## [2.30.4] — 2026-08-26

**fix: parallel CI jobs retain their sandbox prerequisites.**
The computed-results and empirical-binding jobs now load Ubuntu's scoped Bubblewrap AppArmor
profile and verify both namespace creation and the required zero-copy `--ro-bind-fd` capability,
fixing Ubuntu 24.04 runner denials without weakening the production sandbox. Evidence and
setup-integration jobs explicitly install the Bubblewrap prerequisite they previously inherited
from the monolithic workflow. Topology regressions protect the complete runner setup. Fixes #287.

## [2.30.3] — 2026-08-26

**fix: parallel CI test topology cuts feedback latency without dropping coverage.**
The dev-instruction workflow now runs mirrors, computed-results provenance, evidence assembly,
runtime integration, rendered-table validation, source policy, ownership, setup integration,
and the complete 43-shape setup characterization concurrently instead of serializing them in
one 15–16 minute job. A final aggregate retains the existing `Verify generated mirrors` check
name for branch-protection compatibility and fails on any failed, cancelled, or skipped suite.
New topology regressions require every pre-split command exactly once, keep the expensive suites
on independent runners, require every test job in the aggregate, and exercise both aggregate
success and failure. Measured pre-change ownership is the expected 5–6 minute critical path;
the complete workflow targets under seven minutes. Closes #286.

## [2.30.2] — 2026-08-26

**fix: Stage 3a freshness now follows result-receipt lifecycle.**
`empirical_input_manifest.py check-all` now resolves analysis ownership through the durable
results registry and the canonical receipt-v2 validator in an import-isolated interpreter,
freshness-checks only active and
pending analyses, and reports retired attempts as `EXCLUDED_RETIRED`. Missing or malformed
registry state, duplicate or absent ownership, and valid-looking orphan analysis/result/
verifier artifacts fail closed instead of either blocking forever as dead work or escaping
pollution detection. The registry-absent contract is deliberately strict because every
paper-producing deployment initializes it. Eighteen lifecycle-focused regressions include a
receipt emitted by the real results runner plus pending, retired, stale-retired, unregistered,
malformed, crash-prepared, orphan-sibling, missing-registry, stale-fingerprint, and
duplicate-ownership states. Read-only checking holds the results pipeline's shared lock through
the complete emitted verdict, rejects unresolved publication journals rather than blessing
crash-partial state, and verifies the receipt-declared plan and bundle still have their recorded
bytes.
The deployed-path regression also proves project modules cannot shadow standard-library imports
or create bytecode during the check; another proves generated executable bytecode deliberately
invalidates once and converges after a refresh. Stage 3a instructions now force-refresh
active/pending analyses only and invoke the manifest utility with `-I -S`; the complete
code-surface binding remains unchanged. Closes #288.

## [2.30.1] — 2026-08-26

**fix: Stage 3a all-analysis freshness gate halted on its own mandated artifacts.**
`empirical_input_manifest.py check-all` flagged every analysis's results triple
(`<stem>_results{,.plan,.receipt}.json` — the names the stage doc itself derives),
finalize-pass's documented `.candidate` intermediate, and `__pycache__` execution
byproducts as reserved-namespace pollution, guaranteeing
`halted_replication_artifact_collision` on the first full empirical analysis of every
deployment (first observed in a live data-first run). The scan now exempts exactly those
expected artifacts — symlink/non-regular-file hardening retained on every exempted name,
and the code-surface bytecode-detection posture deliberately unchanged — and the finalize
verifier subprocess runs with `-B` so it cannot seed the cache poison itself. Seven new
regression tests in `deploy_assets/scripts/test_empirical_input_manifest.py` (CI-run).

## [2.30.0] — 2026-08-24

**feat: `--mode data-first` — dataset-contribution papers (finance, v1).** The paper's
deliverable is an open, documented, validated dataset plus a portfolio of documented facts
(Chen-Zimmermann genre). Auto-implies `--ext empirical`. Gate 2 becomes a plan-time dataset-
specification audit (`mechanism-auditor` spec-audit body); Stage 3a becomes construction +
validation with a mandatory coverage-triangulation protocol independently verified by the new
`coverage-auditor` agent (an H3 leg); the identification agents are pruned and
`polish-identification` re-targets as the causal-overreach backstop; `puzzle-triager` treats a
failed replication as a candidate headline adjudication (PIVOT re-anchors the fact portfolio).
New state: `dataset_spec_version`, `coverage_triangulation`, `loops.{spec_audit_revision,coverage_audit}`.
Composes with `--seed` (the primary use case), `--faithful`, `--light`, `--manual`. Design and
five audit rounds: #278; follow-ups #279–#284. Existing modes verified byte-identical.

---

## [2.29.2] — 2026-08-24

**The extension-development path is now documented end to end (#195).** The canonical
`edit-pipeline` skill covers composition decisions, asset layout, flag resolution, agent and
skill assembly, ownership, dependency provisioning, mode pruning, state/doc injections,
cross-runtime coverage, test matrices, and developer-mirror synchronization. Extension agent
bodies now receive the same shared → variant → generated-tier → mode vocab precedence as base
agents; characterization tests enforce that order for theory and empirical extensions across
Claude, Codex, Gemini, and OpenCode, including modeless bodies. Implied-extension additions also
use the canonical ordered/deduplicated helper.

## [2.29.1] — 2026-08-23

**Large declared input files no longer require per-attempt copies on Linux (#269).** The computed-results runner now descriptor-pins each declared regular-file producer/renderer source, acquires a kernel read lease, and exposes it at the same workspace-relative path through a Bubblewrap read-only binding. A filesystem that cannot enforce the lease falls back to the existing snapshot copy; a host-side writer against a leased file interrupts the attempt, releases the blocked writer only after the sandbox is killed, and prevents publication even if the writer restores the original bytes. Declared directories retain the snapshot-copy path so their membership cannot change during execution. The writable workspace otherwise contains only empty mount points plus fresh outputs and the rest of the project remains hidden. This removes temporary disk and copy I/O for the common multi-gigabyte-file case even across filesystems without weakening the declared-source boundary. Platforms without Bubblewrap retain the reflink-first physical-copy fallback and the same normal/crash cleanup guardian. Regressions cover a 4 MiB zero-copy input, a transient `A → B → A` host rewrite, source mutation, undeclared-file isolation, copy fallback, and cleanup.

**IBES guidance now prevents silent basis, timing, and linking errors (#228).** The empirical skills prefer unadjusted Summary, Detail, and Actuals tables; require explicit measure, horizon/periodicity, currency, and Summary company-basis selection; distinguish issuance and activation from confirmation timestamps; preserve `pdf` as received-basis provenance; align unadjusted values with date-valid CRSP split factors; and use date-bounded, quality-filtered ICLINK rather than `ibes.id` for PERMNO linkage. Dedicated regressions protect the example queries and the corrected semantics across assembled runtimes.

## [2.29.0] — 2026-08-23

**Execution-time environment provenance for computed results (#271).** Result-receipt v2 now records a trusted historical environment manifest for every producer and renderer: the resolved launcher path and executable hash, platform/kernel/machine/libc and OS-release identity, relevant locale and numerical environment variables, recognized project dependency manifests, and the project venv's installed distribution versions plus wheel/source/entry-point/path metadata hashes. The trusted parent captures immediately before execution, exposes the existing environment read-only inside the result sandbox, and refuses publication if the same capture differs afterward. Each static snapshot is bounded to 64 MiB, 20,000 files, and 20,000 directory entries; it rejects credential aliases and unsafe recognized inputs and executes no environment-controlled inspection code. Agents retain the existing freedom to install packages before a computation; setup, dependency policy, and the producer/renderer computation itself are unchanged. The automatic manifest supports the honest default `captured` label without claiming imported-module/native-library closure; `exact` still requires a separately declared content-addressed environment input, and the stronger replay boundary remains documented under #271. Producer and renderer environment manifests receive exact nested structural validation and a self-digest, while full receipt/registry fingerprints retain their existing anti-rebaselining checks.

## [2.28.1] — 2026-08-22

**Post-release adversarial hardening for the computed-evidence architecture (#264).** Declared directory inputs now reject credential-bearing descendants, every `.env*` or `.git` path, and every hard-link alias; every trusted read/copy/discovery path walks complete directory trees iteratively through held no-follow descriptors and fails immediately and controllably on races, FIFOs, devices, symlinks, multiply linked or unreadable files, invalid UTF-8, backslash/control-bearing names, and other unsafe path shapes instead of blocking under the project lock, pruning evidence, escaping the project, aliasing credentials, recursing out, publishing an unusable receipt, or emitting a traceback. Receipt-contract validation also recomputes directory aggregate hashes and rejects impossible entry trees. The LaTeX scanner now processes comments before live verbatim delimiters and understands escaped-percent parity plus `verb`/`Verb`, `SaveVerb`, `lstinline`, `mintinline`, and both braced and delimiter-form URL/path literals (including escaped delimiters); short-inline definitions, executable inline options, comment-split settings, comments between a literal command/environment and its argument/options, and local/global escape-enabled verbatim/listing configuration fail closed, so a literal or commented `%` cannot hide a later live citation or dynamic file reader. Paper binding requires five distinct frozen/audit paths and identities. Paper-receipt v4 binds its audit-input inventories; `verify-paper` revalidates the frozen audit summaries/reports semantically, rejects deleted/rebased receipt inventories, requires a fresh source check for every citation occurrence at every checkpoint rather than trusting project-local reuse assertions, and always checks every bound result receipt even without deterministic rerendering. Result-receipt verification likewise requires exact plan/bundle/code/input/artifact/renderer/exhibit inventories and the original reproducibility assertion, so editing a registry hash cannot discard provenance. Published JSON Schemas reject common absolute/traversal/backslash/credential path hazards and duplicate objects while explicitly identifying themselves as structural preflight; the runtime remains the canonical cross-field, normalized-path, freshness, and lifecycle validator. `exact`/`bounded` remain audited producer assertions—not automatic verifier conclusions—until #271 closes environment capture. DeepVest markdown-table numeric coercion now supports both pandas object columns and the newer string-extension dtype.

Backward update compatibility is deliberately absent: v2.28.1 accepts only a complete manifest-backed v2.28.1 project. Every other template version must stay on its original checkout or be redeployed fresh. The updater never sniffs old layouts, creates missing mutable evidence state, migrates historical counters/halts, infers ownership from reports, fabricates receipt pointers, or carries recovery arrays through the live pipeline; the corresponding dead `legacy_reroute` and `legacy_update` Stage-0 prompt paths are removed too. This removes an ambiguous trust surface instead of pretending historical project bytes can be reconstructed soundly. Before replacement, the target's full selector and ownership inventory must equal a trusted same-version assembly, so deleting a manifest entry cannot suppress stale-infrastructure removal. Stage result report/receipt pointers must be both null or both populated, normalized, active, and externally fingerprinted; an acceptance version may be null while cumulative replacement is pending. Every selector dimension is immutable in place; update only refreshes the exact deployment shape and source snapshot explicitly attested by the operator, while any selector/source change requires a fresh deployment. Obsolete selector journals fail closed and are never interpreted. A separate fsynced update marker is published before recovery/replacement and removed only after state plus manifest publication; every supported launcher refuses to run while any update/selector marker remains. The authenticated ownership inventory still sweeps any managed path retired by this exact selector/source generation. Manual mode's polish chain resolves active evidence from its setup-created registry and runs evidence/citation checkpoints after every paper mutation, while core bypasses remain prominently surfaced in returned reports. Macro `--ext empirical` now deploys macro-specific identification designer/auditor roles covering SVAR, proxy/HFI, LP-IV, narrative, heteroskedastic, panel, calibration, structural identification, Lucas-critique regime invariance, and general-equilibrium counterfactual feedback; infeasible designs route directly to descriptive reframing or the canonical BACK-TO-IDEA transition without invoking a contradiction-only triager. These macro/manual changes repair routes already advertised as supported, so they are a patch release rather than new flags or modes. Cross-shape assembly, unsupported-version/state, hostile-file, manual, macro-agent, and CI regressions cover the fixes.

Independent post-release review also tightened the updater and renderer boundaries. Producer and renderer commands reject every non-empty credential embedded anywhere in an argument before execution or receipt serialization, including raw, percent-encoded, and decoded authenticated-proxy spellings. Retired lifecycle ownership is revalidated against its plan and bundle before any historical namespace can be reused. Containment executables resolve only from fixed system paths, never project/venv-controlled ambient `PATH`. Comment-aware delimiter balancing closes fake-closing-brace and fake-closing-bracket escapes in TeX literal settings. Updater manifest, state, and managed-leaf types fail before replacement, dry-run refuses rather than performs transaction recovery, ancient folder and launcher compatibility mutations are removed, and state/manifest publication is ordered and fsynced. Existing manual evidence state, evidence paths, and registry structure are preflighted before managed replacement. On Linux, renderers use a private network namespace whenever the inherited kernel policy still permits IPv4 or IPv6 sockets, and inherit an already-denied socket policy inside nested sandboxes that cannot create a second namespace. Stateful listings styles, language-scoped minted settings, and escaped URL/path delimiters can no longer hide live TeX dependencies or citations, while malformed snapshot arrays produce controlled stale/error results instead of tracebacks.

The final audit rounds also preserve every credential-length (at least eight-byte) host secret spelling for post-run leak scanning even when a renderer or uncredentialed producer receives none of those variables; suffix-appending LaTeX commands bind the suffixed file TeX consumes and reject an ambiguous extensionless/suffixed collision demonstrated against TeX's recorder output. Standard csquotes/biblatex citation commands—including multiprenote multicites, hybrid/hyphen cquotes, note cites, and low-level name/list forms—join the case-insensitive occurrence inventory; common user-defined citation aliases and custom graphics-extension ordering fail closed, and `.env`/`.git` plus the reserved audit namespace are rejected under case-insensitive filesystem aliases. Paired TeX control-symbol backslashes cannot fabricate dependencies, macOS containment no longer grants blanket Mach-service lookup (and therefore cannot expose the user Keychain), receipt-only structural validation remains possible after historical inputs disappear, and wide evidence trees use descriptors proportional to depth rather than sibling count. Evidence copies, backups, receipts, newly created output ancestors, and final publications fsync their bytes and directory entries before a committed lifecycle can outlive a machine crash; terminal transaction cleanup is durable too. Updater dry-runs stage entirely outside the target and leave target directory metadata unchanged. Every populated result pointer is normalized and opened through descriptor-relative no-follow traversal, every active/pending/retired receipt must match its externally recorded fingerprint and current receipt contract, and a stage report must be one of that receipt's generated artifacts. `.env` and manifest replacements stage on their destination filesystem; newly created control directories are parent-fsynced; stale infrastructure derives only from the already-authenticated manifest inventory and removes dangling/special leaves rather than silently abandoning ownership. A detached guardian retains the exclusive update lock until a killed updater body and descendants are drained, and a final recursive durability barrier fsyncs every managed file and affected directory before removing the launch-blocking marker. Every updater invocation requires the full operator-attested current selector, and both the selector and exact source version/digest must match the fresh verification assembly; no selector migration path remains. The updater never executes or mutates the agent-writable project virtualenv. Completed projects with stale or malformed paper evidence are atomically reopened at Stage 9, while malformed same-generation state fails before replacement. Started runs never change modes in place: a structural empirical-first halt or post-pipeline need for theorem infrastructure requires a fresh theory-first deployment rather than reinterpretation of incompatible state.

Pipeline state uses one fixed `archived_best_scores` map rather than dynamically adding round-specific top-level fields, so legitimate later regeneration rounds retain the same validated schema.

The closing audit rounds make update source identity an explicit operator attestation: every setup path prints one complete resolved canonical update command to record outside the project, including its content digest, implied extensions, and every positive/negative flag. Every update requires that `--source-digest` in addition to the complete current selector, and its authenticated launcher captures and verifies the full build-input snapshot before any setup/deploy module executes, so a project-writable manifest or changed live `setup.sh` cannot authorize or run a cross-snapshot refresh. Target control JSON is parsed with the runtime's duplicate-key and non-finite-number rejection. A new launch-blocking update marker is created only after all read-only preflight succeeds, while a crash-left marker still protects a genuinely partial publication. `launch.sh` also refuses to expose pipeline state while a computed-results transaction journal awaits recovery. Setup/update normalize their process umask so managed modes do not depend on the caller; updater `jq` comes only from validated fixed host installation paths rather than ambient `PATH`. Finally, natbib's standard `\bibentry` occurrences and `\nobibliography` database reads join the paper audit inventory, and every citation-bearing alias/redefinition—including aliases to `\bibentry`—fails closed.

The final independent pass additionally reserves every planned exhibit path from producer publication onward, including attempts retired before rendering; recognizes common etoolbox/xparse citation-definition forms; rejects root-level doubled separators in the published schemas; and separates theory-draft support from rendered empirical/experimental support in the paper-writer contract. Setup's externally recorded command authenticates the exact updater launcher, which acquires the project runtime lock before capturing and digesting the complete source snapshot; the snapshotted coordinator—not a mutable live inode—is then executed with a fixed protected Bash. Operator `.env` additions travel separately through an anonymous inherited file, remain outside build provenance, and cannot be stranded as named credential files on SIGKILL. Empty/lossy/duplicate selectors fail closed and mutable journal targets must remain on the variant's tier ladder. Update state validation compares source-defined loop caps and selector booleans to the fresh trusted assembly, while fixed `jq` resolution must remain inside its named host installation root. Dependency-file comments now describe their manifest-owned deployed provisioning copies, and DeepVest's pandas extension-string regression is deterministic across pandas versions.

All result publication, removal, rollback, and transaction cleanup is descriptor-relative beneath a physically canonical project/temp root; ancestor replacement cannot redirect deletion outside the project, and copied directories retain owner cleanup permissions even when a source mode would otherwise leave hidden staging residue. macOS `/var` temp aliases plus ordinary uv-managed and Homebrew Python bases remain usable without reopening project reads. The static TeX graph parses balanced optional arguments for listings, minted, graphics, PDF, CSV/pgfplots, package/class, and bibliography readers. Citation parsing now separates nested formatting braces in notes from actual citation keys for ordinary cites and csquotes, preserving the first paragraph's full claim text. Manual paper/evidence agents resolve arbitrary `output/` namespaces exclusively from active registry receipts, while macro empirical papers receive a rendered-paper identification audit calibrated to SVAR/proxy/HFI/LP-IV/narrative/calibration/structural claims, set identification, prior sensitivity, regime invariance, and general-equilibrium counterfactuals.

The closing containment pass captures producer/renderer stdout and stderr behind a bounded parent-side gate: literal credentials never reach terminal/model logs, safe diagnostics are forwarded on stderr, and the utility's stdout remains one machine-readable JSON result. External listing inputs reject code-enabling options, nested local package/class options remain transitive, and balanced citation-definition parsing no longer mistakes formatting brackets for argument boundaries. Manual deployments may still compose with extensions or architecture modes to select tools, but every paper/polish agent ignores autonomous state/stage paths and discovers evidence exclusively through active receipts; macro report mode now receives the same macroeconometric identification calibration rather than finance-only factor diagnostics. Update requires protected Bash 4+ at a fixed system/Homebrew path, closes the launch-lock descriptor before any refresh body runs, kills and drains a failed body's descendants, rejects FIFO source/launcher inputs without blocking, removes crash-left credential workspaces on retry, rejects empty mode selectors, and validates routing enums plus counter domains before replacement. Linux setup now checks the exact `/usr/bin/bwrap` path the runtime trusts instead of accepting an unusable ambient binary.

The final provenance pass anchors result locks and JSON publication to held no-follow directory descriptors, rejects project-overlapping temporary workspaces, follows TeX's `.tex` preference for ordinary extensionless inputs, recursively covers braceless package/class inputs, and accepts standard csquotes punctuation/language-note forms without weakening citation inventory. The updater validates the exact current manifest generation and top-level schema, keeps operator `.env` bytes anonymous through fresh assembly and direct merge, drains successful as well as failed refresh descendants before releasing its lock, and recovers a fixed Stage-9 state-publication file without accumulating hidden crash residue. Manual computed producers now use registry activation—not nonexistent stage pointers—as their durable handoff, and macro Stage-9 identification polish consistently follows the applicable Stage 1 or Stage 3a design artifact. The authenticated build-input documentation names both updater inputs, and theory-LLM dependency recovery includes Anthropic.

The final independent audit closes the remaining recovery and manual-mode edges. A project-writable results transaction journal may roll back only result-owned paths under `output/`, never paper, code, data, control state, or the audit namespace. Standard display-style csquotes environments join the occurrence inventory; conditional TeX inputs follow the same `.tex` preference as TeX itself, while explicit `.cfg`/`.def`/`.ltx` package reads retain their real suffix. Audit-report verdict, checkpoint, and digest markers are conflict-checked case-insensitively in both direct and Markdown-heading forms, so a mixed-case body verdict cannot hide behind a valid PASS header. The updater ignores ambient `TMPDIR`, transports operator `.env` through a framed anonymous pipe on both Linux and macOS, rejects truncated transfers, and lets its detached guardian arm the refresh body directly. A trusted outer supervisor also feeds public-launcher liveness into that guardian: launcher EOF cancels and drains the exact refresh process group under the exclusive project lock, then removes the pinned source snapshot before releasing the lock, including after uncatchable launcher death. A separate cleanup owner creates the pinned snapshot before any source copying, so even a pre-handoff SIGKILL has no unguarded temporary-directory window; its own failed status-pipe publication also acquires the project lock and cleans the snapshot. Verified no-follow cleanup repairs private directory permissions and removes read-only snapshot/workspace trees instead of silently abandoning them. Manual extension deployments no longer create Stage 3a/3b directories, and every result-consuming callable agent—not only producers and paper polishers—treats autonomous stage pointers as inapplicable in manual mode and resolves arbitrary namespaces exclusively through caller inputs plus active registry receipts. Manual deployments retain the selected mode's scientific review schemas and paper shape while removing only autonomous state/path blocks; paper writers therefore keep complete framing, contribution-section, appendix, LaTeX, and style guidance while using workflow-neutral accepted materials rather than autonomous stage paths.

## [2.28.0] — 2026-08-21

**`--ext theory_llm`: frontier-model backends — OpenAI GPT-5.x and Anthropic Claude — in `llm_client.py` (#274).** `call()` now routes `gpt-*`/`o*`/`chatgpt-*` to the OpenAI Chat Completions API (`OPENAI_API_KEY`; `max_completion_tokens`, `reasoning_effort` none…max, `temperature` withheld on gpt-5.x/o-series unless `reasoning_effort="none"`, hidden `reasoning_tokens` kept in `usage`) and `claude-*` to the native Anthropic Messages API via the `anthropic` SDK (`ANTHROPIC_API_KEY`; adaptive thinking with `display: "summarized"` + `output_config.effort` on Claude 4.6+, sampling parameters withheld except on Opus/Sonnet 4.6, legacy ≤4.5 models get plain `temperature`, `stop_reason: refusal` surfaced with its category). `gpt-oss*` still routes to UF; key-only fallback order is UF → DeepInfra → OpenAI → Anthropic → local. `LLMResponse` gains `finish_reason` and `request_params` — the decoding parameters *actually sent* after per-model gating, so a paper's decoding disclosure is copied from the response log rather than assumed; a provider 400 naming `temperature` is retried once without it and recorded as `None`. `anthropic` joins the extension deps; `OPENAI_API_KEY`/`ANTHROPIC_API_KEY` are seeded into `.env.example`, appended to existing deployments' `.env` by the theory_llm applier, and admitted to the results-pipeline `SECRET_ENV_KEYS`/`NETWORK_ENV_KEYS`/`RUNTIME_ENV_KEYS`, the run-plan `provider_credentials` enum, and the result-bundle fragment. experiment-designer/-reviewer and the `llm-experiments` skill name the frontier tiers as valid cross-family replication families (cost caveat: size the replication to the headline contrast), and tell designers to report decoding parameters as sent (`request_params`) and to score a `refusal`/truncation as such. The DeepInfra catalog was refreshed against the live `/v1/openai/models` list (10 of 13 baked-in IDs, including the old default `Qwen/QwQ-32B`, had been retired): default is now `deepseek-ai/DeepSeek-V4-Flash-0731`, and `reasoning_effort` is forwarded to DeepInfra as it is to UF — verified live to be the switch that turns DeepSeek V4 into thinking mode (V4-Pro answered a trivial arithmetic probe *wrong* without it) and to be ignored harmlessly by models without the knob. New `test_scripts/test_llm_client_backends.py`: offline routing + request-construction tests in CI, plus an opt-in live canary (`LLM_CLIENT_LIVE=1`). Google Gemini is deliberately not added (no key on hand; out of scope for now — #274 stays open for it).

## [2.27.0] — 2026-08-21

**New `--ext empirical` dataset skill: `deepvest` — the DeepVest AI research terminal through its remote MCP server (#272).** `code/utils/deepvest_utils.py` is a dependency-free Streamable-HTTP MCP client for `api.deepvest.ai/mcp` (X-API-Key auth from `DEEPVEST_API_KEY`, session handling, SSE/JSON responses, cursor-paginated `tools/list`, 429/5xx backoff honouring `Retry-After`, 20-req/min client-side spacing, 401/402 mapped to typed errors) with a CLI (`ping` / `tools` / `query` / `call` / `cache`), a per-`(tool, arguments)` JSON cache under `data/deepvest/` that doubles as the provenance record, and `parse_result` / `tables_from_response` / `parse_markdown_tables` for the vendor's `format="json"` envelope and prose tables. The skill body maps the 54 live tools to research uses (price/fundamentals by ticker, ETF flows and holdings, dividend payment records, as-of screens, options analytics/chains, earnings transcripts, EDGAR 13F/N-PORT, macro), and states the limits plainly: metered credits, LLM-mediated and not byte-reproducible, tickers only, unstated price basis, survivorship, no provenance badge, fetch before the results-pipeline run because the producer workspace carries no DeepVest key, and never report DeepVest's own backtests as results. `DEEPVEST_API_KEY` is seeded into `.env.example` and appended to existing deployments' `.env` by the empirical applier. Access, tool catalog, a typed tool, and the JSON envelope were verified live; the LLM-mediated re-query gap for the data-integrity audit is documented in `LIMITATIONS.md` and tracked in #272.

Same day, dev-only (no version bump): `test_scripts/test_setup_characterization.py` now strips optional-host-tool availability warnings (`⚠ codex CLI not found` / `codex-math skill will not work`) from captured CLI output before comparing with the golden. The golden was generated on a host with the codex CLI installed, so every `main` CI run — where codex is absent — had been failing the CLI-failure contract on that one host-dependent line while the assembled trees were identical; re-normalizing the failing run's uploaded `actual.json` against the golden gives zero mismatches.

## [2.26.0] — 2026-08-21

**Paper-facing computed evidence now has one reproducible producer-to-reader chain, and citation characterizations are independently source-bound after every paper mutation (#264).** Theory exploration, empirical analysis, and LLM experiments write flexible schema-v1 JSON result bundles through recorded analysis commands; separate presentation-only renderers generate every result-bearing LaTeX table and PDF/PNG figure. A stdlib verifier fingerprints declared code, inputs, raw/detail artifacts, bundles, renderers, and exhibits, rejects stale or hand-edited outputs, supports deterministic re-render checks, and binds exact paper source bytes to independent PASS reports. Paper-writer reads the exhibits readers see rather than JSON, cannot author or alter computed table cells/plot data, and requests missing evidence from its producer; formal theory notation stays outside the result schema.

After initial writing and every later writer/style/bibliography/table mutation, `evidence-auditor` verifies all active result receipts, the bundle→exhibit boundary, and every numerical or qualitative prose/caption interpretation. In parallel, `polish-bibliography` checkpoint mode inventories every citation use and requires exact primary/OpenAlex pointers for new or changed characterizations, reusing only prior characterizations mechanically matched to the byte-bound summary. The utility recursively derives supported static LaTeX source/asset/data dependencies—including local classes/packages and common listing/CSV/pgfplots inputs—and every supported biblatex/natbib citation occurrence with normalized claim text; unknown cite-family commands and known dynamic dependency commands fail closed, while arbitrary TeX file-reader completeness remains tracked in #270. Before analysis, a run plan declares exact code, inputs, artifacts, renderer, exhibits, and the minimum provider-key variables needed. Each producer or renderer runs in a default-deny workspace containing only those declared project sources, a neutral read-only mount of the provisioned venv and any external base interpreter, fixed system runtime files, and the query-only WRDS transport. Undeclared live-project data is absent, stdin is EOF, non-allowlisted ambient environment variables are removed, and every staged output is confined to `output/`. Provider-backed producers receive only plan-selected API variables plus outbound network; renderers receive no provider/network environment, and literal selected-provider credentials plus percent-decoded authenticated-proxy passwords of at least eight bytes are rejected from staged files. The trusted parent alone retains the results lock and publishes only validated artifacts, bundles, receipts, and complete exhibit sets; a lock-free supervisor kills and waits for the ordinary sandboxed process group on parent death, while Linux payloads run as PID 1 in their private namespace so normal exit cannot orphan a background descendant. This prevents hostile replacement and lock release, keeps undeclared controls invisible, preserves system, standard-venv, uv-managed, and Homebrew-style runtimes, and makes execution I/O linear in the current attempt rather than the full receipt history. An explicit command grammar requires the executed entrypoint itself to be declared, so inline/no-op wrappers cannot inherit old outputs. A dedicated process lock, phase-journaled idempotent publication transaction, and no-follow restoration/publication keep concurrent attempts and process kills at every backup/commit/rollback phase from corrupting lifecycle state or evidence. A durable mutable registry makes pending/active/retired/superseded receipt state explicit and externally fingerprints every pending/active receipt: rendering leaves a replacement pending through scientific review; explicit activation adds it alongside its predecessor, the stage pointer then moves atomically, and only afterward is the predecessor explicitly retired. Missing or altered history, incomplete pending work, and reuse of any historical attempt-owned namespace fail closed; shared code/input updates have an explicit superseding path without allowing output reuse. Accepted Stage 2b, Stage 3a, and Stage 3b report/receipt pairs propagate through explicit pipeline-state pointers. Both reports and all paper/result/registry bytes enter one canonical paper-evidence receipt under a bounded shared loop. This replaces and removes the empirical-only enumerator/grounder/verifier trio and its three counters, giving theory-only, empirical-first, measurement-first, seeded, and post-pipeline edits the same gate. Producer receipts default to historically `captured`; an `exact` label requires a declared audited content-addressed environment manifest, while automatic multi-language interpreter/dependency closure is tracked in #271. Update migration adds the shared evidence loop and recovery-safe mutable evidence skeleton before manifest/state commit, reopens only completed legacy runs lacking a paper receipt at Stage 9, retires old claim-loop fields, and creates a missing registry only when no historical result receipts exist; the registry is staged, fsynced, and atomically renamed so SIGKILL leaves either no final file or one complete JSON object. The utility directory is replacement-owned, while generated plans, bundles, and receipts remain mutable project evidence. Residual boundaries are documented and tracked in #267–#271.

The audit-only `output/evidence/` namespace is mechanically disjoint from result-owned paths, crash-stranded atomic/publication temporaries are ignored, and an independent workspace guardian closes the credential-residue window after the process supervisor exits.

## [2.25.3] — 2026-08-18

**The authenticated relay drains before closing, ending the residual mid-frame truncation that survived v7 (#263, #266).** Live diagnosis with the v7 daemon showed the remaining "wobbling ~500KB threshold" drops were not the daemon at all: the sandbox proxy chain buffers hundreds of kilobytes of a response frame in flight and discards the undelivered tail the moment the bridge closes first, so the truncation offset tracked forwarding progress, never a fixed limit, and only sandboxed clients (never host-side ones) were affected. After writing a response on a preface-authenticated connection, the bridge now holds the socket open until the client — which closes only after reading the whole frame — closes its end. The wait shares the write's payload-scaled 315-second-capped delivery deadline on the query path (write plus wait can never hold a query slot for two budgets) and takes a bounded 10-second allowance after error frames; unauthenticated connections never linger, so an anonymous peer cannot hold a relay thread. A discarding-relay regression double that forwards eagerly into a userspace buffer, trickles toward the client, and drops the buffer on relay-side EOF reproduces the production `incomplete WRDS response frame` against the pre-fix bridge and proves full delivery with the fix.

## [2.25.2] — 2026-08-18

**WRDS v7 prevents intermittent mid-frame truncation of large query responses and false busy-daemon outages (#263).** The daemon and authenticated relay no longer reuse the 15-second untrusted-request read timeout while writing responses. Both apply one payload-scaled, 315-second-capped wall deadline, track exact write progress, log the original transport failure, and close after a partial write without appending a corrupt second frame. SQL execution, response preparation, authenticated-relay setup, daemon-to-relay transfer, and relay-to-client transfer now receive composed rather than overlapping deadlines; a query that consumes its full execution allowance retains a full frame-transfer allowance at every hop. Queue wait, one guarded recovery, and retry share one total server operation deadline, with only the remaining time passed to each SQL attempt and late results rejected. DataFrame conversion plus final JSON encoding run in a separately timed, concurrency-bounded producer stage; an expired worker owns no socket and discards its eventual result. Proxy CONNECT byte trickles cannot reset their total setup clock. Explicit lock-owner/deadline metadata makes only an in-budget command busy-but-live; expired commands, healthcheck/recovery, unblock, and unknown owners remain unhealthy. Ordinary commands no longer run a lock-taking ping between their DB-free version handshake and real request. End-to-end delayed-query/mid-transfer, relay-setup/proxy-trickle, late-success/expired-owner, preparation-timeout, recovery-expiry, command-vs-healthcheck lock contention, and multi-megabyte delayed-reader regressions cover the direct and relayed paths. The safety/bridge protocols advance together so an updated deployment cannot silently reuse an affected v5/v6 host service.

## [2.25.1] — 2026-08-17

Codex launch pins the parent to MultiAgent V2 in headless, interactive `--once`, and `--light` sessions, so ordinary user configuration cannot remove the native role tool surface or silently switch Luna to the incompatible V1 task/wait schema; role-local session flags still make every child a leaf. The documented #240 containment residual includes deliberate daemonization, reparenting, and escape into a pre-existing non-descendant-owned process group; the watcher claim is limited to the bound descendant-owned groups it can freeze safely.

**Codex now dispatches the assembled agent roster through native custom roles, removing the detached-worker protocol (#243).** Codex 0.147.0's `agent_type` routing applies each `.codex/agents/*.toml` model, reasoning effort, and developer instructions directly. Generated roles suppress the orchestrator AGENTS.md and pin both the V2 feature and legacy agent switch off so parent/session and ordinary user-config overrides cannot restore recursive delegation; higher legacy managed/MDM layers and separate enterprise feature requirements remain explicit #240 boundaries. The headless launcher restores trust for exactly the physical project after ignoring ambient user config. The orchestrator keeps each child cohort inside its spawning turn, waits to terminal status, validates every promised artifact, and preserves each canonical stage's combined or no-commit boundary, because primary `codex exec` completion interrupts live native children. Fan-outs respect the four-slot parent-inclusive limit through bounded waves of at most three children. After an interrupted turn—including report mode, which commits a triage/ledger run baseline and then atomically commits each audit with its coverage-ledger row—task-owned uncommitted diffs fail closed and are rewritten/revalidated rather than inferred complete from file contents; committed stage boundaries are durable recovery receipts. Report mode's formerly improvised final reader is now the registered `report-reviewer` role, with one exact versioned CLEAN/FIX artifact and a durable repair/re-review protocol. Manual/report setup guidance now requires `codex --once` instead of recommending the pipeline-state driver they do not contain. The sentinel/output-banner wrapper, post-turn worker wait, stale-output heuristics, and deployed launcher utility are deleted, closing the obsolete interactive-collection, machine-readable-sidecar, and wrapper-pid gaps (#242, #243, #245). Every headless turn now has an anchor-backed root group plus an independently grouped parent-liveness watcher instead of a racy numeric-PID/start-time probe; before hard cleanup the watcher freezes the root, discovers and freezes descendant-owned groups, binds every live member to a kernel identity, kills those groups, and holds the project lock until the bound identities exit. The credential-free production regression uses a TERM-ignoring setsid tool child matching Codex 0.147 shell execution, then separately SIGKILLs the visible supervisor and proves recovery/update cannot overtake it. Deliberate pre-snapshot daemonization/reparenting remains the documented #240 containment boundary. Deterministic unit and full-assembly tests cover role/config generation and the recovery invariant; a bounded opt-in live Codex canary causally binds exactly one parent spawn result, successful wait result, child terminal notification, exact parent artifact read, and unique final answer to one rollout, proving the declared scorer role, pinned model/effort, fresh child context, leaf status despite a parent-side V2 session override, and byte-exact handoff against the installed CLI.

## [2.25.0] — 2026-08-16

**WRDS v6 closes the remaining lifecycle, false-halt, framing, and OpenCode-first-start gaps (#262).** The wire protocol now uses an unsigned 64-bit binary length prefix across the Unix client/server and authenticated Linux relay, replacing the accidental 90 MiB response ceiling with a documented 512 MiB malformed-peer safety bound and total frame deadlines; the separate one-million-row, 48 MiB materialization, and bounded `get_table` contracts remain and the WRDS skill now specifies deterministic windowed pulls. Stage 3a runs and honors a final authoritative venv-pinned `wrds_ping()` immediately before `halted_wrds_unreachable`, so a transient first probe or empty auth diagnosis cannot stop a healthy run. A Codex-like process-group teardown regression starts the final deployed service path, destroys the originating group, and proves a fresh invocation can still reach the detached daemon. OpenCode can now establish the host-wide singleton on a first/only empirical host through a long-lived launcher-owned SRT service profile: the unsandboxed control plane executes no project code or venv, a model-immutable stdlib gatekeeper runs under the privileged profile, host-wide serialization prevents cross-approval, PID/birth/group/command and host-visible PID semantics are validated before the one-shot pre-login gate opens, and credential-free deployments skip without executing project service code. Mocked concurrent first-start/reuse/empty-credential and approval-gate tests plus the opt-in real SRT Unix-socket/PID-visibility canary cover the boundary. A live v5 daemon/relay must be stopped once after update because the framing change is intentionally fail-incompatible.

## [2.24.11] — 2026-08-15

**Claude and OpenCode on Linux can reach the shared WRDS connection without granting access to every host Unix socket.** Anthropic Sandbox Runtime blocks `socket(AF_UNIX, …)` with a path-blind seccomp filter on Linux, so the v2.24.8 filesystem-visible socket was reachable in principle but could not be opened by sandboxed commands. The host prestart now adds a credential-free, query-only TCP relay on a separate loopback port; a rotating 256-bit capability in protected `~/.local/state/zeropaper/wrds` authenticates each request, the relay accepts only the bounded v5 query command set, and Claude's already-authenticated loopback HTTP proxy carries the bytes across its network namespace. The client prefers the private Unix socket, falls back only when AF_UNIX creation is syscall-blocked, never sends the capability through a non-loopback proxy, and retains no lifecycle/unblock/shutdown surface. macOS keeps the narrower path-specific Unix-socket allowlist. Live Claude-sandbox `SELECT 1`, capability/proxy/symlink/lifecycle adversarial tests, and the full transport/launcher/assembly suites cover the fix; broad `~/.cache` access is unchanged.

## [2.24.10] — 2026-08-15

**Runtime sandboxes again expose the full user cache without weakening WRDS lifecycle safety.** Claude, Codex, Grok, and OpenCode grant broad `~/.cache` writes so unlisted and future scientific/browser tools do not fail on first use; a more-specific `~/.cache/zeropaper/wrds` rule remains read-only/deny-write, and descriptor checks reject symlinked or foreign-owner roots without rejecting ordinary group-writable package caches. Codex now uses a shared permission profile for the orchestrator and un-nested workers, ignores user config in headless sessions while the higher-precedence command-line profile safely overrides legacy sandbox keys for the interactive TUI, retains project `.git` commits and open research egress, disables command egress for codex-math, denies reads of SSH/AWS/Claude credentials, and fails clearly below codex-cli 0.147.0; this closes #254 and replaces legacy `writable_roots`, which could not carve a protected child out of broad cache access. OpenCode's driver lock now follows its actual runtime-subshell parent rather than Bash's inherited `$$`, so concurrent launches cannot attach a second prompt to the same project; the visible launcher preserves its update lock through complete process-group cleanup on termination, disconnect, and terminal quit, while a Ctrl-Z/`fg` handshake safely transfers the controlling terminal between the supervisor and runtime instead of wedging the session. Empirical Codex resume prompts explicitly state that launcher-preflighted WRDS is up, preventing a repaired run from preserving stale outage workarounds. Assembly, launcher, transport, permission-profile, worker, and characterization regressions cover the restored contract.

## [2.24.9] — 2026-08-15

**WRDS v5 startup now scopes Linux network-namespace inspection to deployed runtime candidates before reading protected `/proc/<pid>/ns/net` links.** Same-user system session helpers such as systemd's `(sd-pam)` intentionally hide both cwd and namespace links; v2.24.8 treated that unrelated helper as an incomplete safety scan and refused every daemon startup before login. Processes are classified across their cwd ancestry, so ordinary system helpers are excluded while both opaque children and released clients that changed to a non-project cwd remain inside the fail-closed gate when descended from a deployed runtime. The offline transport suite carries each regression.

## [2.24.8] — 2026-08-15

**WRDS now remains reachable across runtime network sandboxes without reopening database sessions.** Empirical launches—including report and manual deployments with no pipeline-state file—establish the host-wide daemon before Claude/Codex/Grok sandbox entry, while completed and halted autonomous runs retain the no-preflight contract. The daemon exposes a v5 safety protocol on one query-only `0600` Unix-domain socket under host-owned `~/.local/state/zeropaper/wrds`; wire lifecycle commands do not exist, and the old TCP port serves only a DB-free upgrade refusal. Sandboxed commands and subagents therefore reach the same persistent connection and pay at most the existing single Duo/login attempt without gaining an endpoint that can unblock or shut down the daemon. An atomically published, read-only singleton marker—not namespace-local TCP, PID heuristics, or advisory flock that a read-only observer could hold—serializes startup across network namespaces before credentials are touched, while also preventing an intermediate v4 writer from truncating it; dead/recycled owners and durable login attempts are identified by process birth token plus boot identity, live sockets are never unlinked, stale cleanup and shutdown are replacement-identity-safe, wedged owners fail promptly, and PID publication cannot follow symlinks. Upgrade guards discover old server processes independently of network namespace, require deployed foreign network namespaces to be quiescent for the first v5 start (closing a released client paused after its old latch check), publish a `0400` active-v5 record at the exact durable latch path released v2/v3 starters already honor under a `0500` directory, rescan before login, keep a `SO_REUSEADDR` refusal listener on the old TCP port, and identity-safely migrate the intermediate plain-PID lock after its owner is dead. Every confining runtime now grants only descriptor-validated, no-symlink dependency cache roots rather than broad `~/.cache` writes. The v2-v4 cache latch and v2.22.1 runtime latch both migrate forward without spending a login; operator unblock is available only after the live daemon is stopped on the host, atomically replaces the terminal latch with a boot-aware live-attempt record only after transport/PID setup, holds the singleton across reconnect, and redirects the permanent child to the durable service log rather than abandoned pipes. Sandbox-side helpers never spawn a replacement: daemon loss halts for host repair. Socket frames, client threads, query duration, materialized result memory/rows, and response size are bounded, while `setsid` makes the daemon survive runtime/tmux teardown. Offline regressions cover transport, singleton/v4-writer races, read-only adversaries, namespace-independent legacy discovery and first-upgrade quiescence, TCP `TIME_WAIT`, fragmented/oversized frames, result caps, stale/live socket handling, lifecycle-command absence, upgrade/latch migration including crash/restart, PID symlinks, cache-root symlinks, and launcher mode/status branches; the WRDS suites run in CI against pinned `wrds==3.5.0`. OpenCode-only startup remains tracked under #261 and unconfined Gemini is excluded under #187 rather than receiving a false state-protection claim.

## [2.24.7] — 2026-08-15

**Headline replication now follows exact input changes rather than an orchestrator judgment (#247).** Every `headline-replicator` PASS embeds a SHA-256 manifest generated by a deployed deterministic utility over every regular project file under `code/` (including dynamic imports, subprocess/non-Python helpers, and executable cache payloads), the exact per-analysis verifier script, and the line-ending-normalized `## Headline claims` section of the canonical or caller-supplied versioned analysis being verified. The orchestrator atomically finalizes each PASS from one actual structured verifier run with stable pre/post inputs, then hash-checked without re-executing it; rows must exactly match the tagged IDs/text, explicit raw-unit reported value, bound fixed tolerance class, recomputed delta, agreement, and allowed path class, while hidden verifier dependencies and orphan/colliding namespaces fail closed. Canonical and versioned analyses own distinct verifier artifacts, while an all-analysis freshness gate revalidates every existing analysis against final code before and after audit, so later claims, post-pipeline edits, or code-generating execution cannot overwrite or silently stale earlier evidence. Code/headline-only repairs use the same mechanical guard; data/cache rebuilds force every analysis to re-fire because data bytes stay deliberately outside the manifest. The empiricist, replicator, empirics auditor, both data auditors, and method checker preserve `ANALYSIS_PATH`; all empirical/post-version entrypoints are audited; versioned audit outputs no longer overwrite Stage 3a defaults; same-selector updates migrate the active-analysis pointer; Stage 5 JSON-only re-exports keep the headline analysis read-only and re-check after audit; and mixed repairs serialize. Git state, mtimes, and subjective “material change” classifications no longer participate. CI regressions cover per-analysis artifacts, verifier/claim durability, orphan detection, all-analysis invalidation, canonical/versioned headlines, changes anywhere in project code, post entrypoints, prose/fences/line endings, wrong-analysis binding, traversal, manifest tampering, and symlink fail-closed behavior.

## [2.24.6] — 2026-08-15

**SSA life tables now work from cloud/datacenter deployments without network access (#248).** The empirical extension bundles the complete 2023 SSA OACT period life table used in the 2026 Trustees Report as a normalized public-domain CSV with source/vintage/schema metadata and a pinned SHA-256 digest. `ssa_period_life_table()` validates and reads that immutable bundle by default, preserving its former `pandas.read_html` list/MultiIndex interface while attaching provenance in `DataFrame.attrs`; `refresh=True` on the official URL validates headers, ages, finite values, probability/survivor consistency, and page vintage, and never overwrites the shipped snapshot. Custom URLs retain their historical raw multi-table return and URL-keyed cache rather than being misrepresented as validated SSA provenance. The bundle and provenance are replacement-owned deployment infrastructure—including safe removal when the empirical extension is cleared—the skill records the refresh procedure, the former limitation is closed, and offline plus opt-in-live regressions prevent ordinary tests from depending on SSA's Akamai-blocked endpoint while still detecting upstream drift.

## [2.24.5] — 2026-08-15

**Mode overlays now reach extension agents consistently (#249).** Both extension appliers receive the active mode's body directory, vocab overlay, and metadata slug, so theory_llm and empirical agents can replace either shared (`{id}.md`) or variant (`{id}-core.md`) bodies, inherit shared → variant → mode vocabulary, and apply mode-specific description/model/tools metadata across Claude, Codex, Gemini, and OpenCode. Modeless assembly strips metadata declarations and receives no mode-only body or vocab. A synthetic full-setup regression injects distinct body, vocab, and metadata sentinels into both extension families and verifies active-mode application plus modeless isolation in every supported extension runtime.

## [2.24.4] — 2026-08-14

**Stage 0 open-domain discovery now has a finite autonomous terminus (#252).** A run-global `loops.stage0_discovery` budget grants at most 100 physical broad-scout launch permits to an unseeded pipeline (seeded/faithful runs bypass discovery), so neither scored-question cycles, regeneration, Stage 0 re-entry, renaming/subdividing thin domains, nor crash retries can evade termination; every initial launch and retry consumes a durable permit first, and the binding check forbids launch 101. Broad results publish atomically from permit-specific staging paths, while stable gap IDs reconcile partially written archives/logs without duplicates; durable phase + substep state prevents a resume from repeating branch selection or mistaking stale canonical files for completed characterization, posing, or review. Closed/no-stake gaps feed a compact near-miss portfolio whose versioned source snapshots are isolated by unique discovery episode, and every downstream Stage 0 return increments `problem_attempt`, preventing stale candidate and artifact reuse. Before the cap, `branch-manager` may choose another domain, one corrected scan, or early promotion; at the cap it must select the strongest available near miss. Durable cap context distinguishes a downstream-return question, an incomplete permit-100 scan (whose instruction and current-episode evidence are preserved), and an active legacy update with partial artifacts, so each case has executable promotion inputs without another broad scan. Every promotion receives one final targeted gap characterization and then enters the ordinary independent question-poser/question-referee gate. The retired `halted_no_viable_question` route no longer sends ordinary research judgment to an operator or falsely implies that an open field contains no viable question. Because active legacy runs cannot prove their lifetime launch count, same-selector updates fail closed at the cap and continue through autonomous salvage; only a pristine never-started deployment receives all 100 permits. The updater inspects legacy artifacts through no-follow deployment-directory descriptors, resumes that exact legacy halt, and preserves every unrelated safety halt; a five-runtime assembly regression enforces the domain-independent cap, crash boundary, and autonomous terminal route.

## [2.24.3] — 2026-08-13

**Table legibility is now enforced at source and verified from the final render (#253).** `arpipeline.sty` uses the document class's effective `\scriptsize` boundary, fails compilation (rather than merely printing a marker) for direct undersized native tables, and measures both dimensions plus the observed source font across plain/starred `\resizebox`, `\scalebox`, command-form `adjustbox`, and semantic-table arrays; pure rotation and resized equation arrays remain legal, while ambiguous compound transforms are left to rendered inspection. Nested table transforms and table-bearing `adjustbox` environments fail closed because re-entrant/collected bodies cannot be compatibly measured without shared-state bypasses. Image-only semantic table floats are rejected while native tables may retain icons. The error itself carries `ARPIPELINE-TABLE-LEGIBILITY-FAIL`, so `tabularx` trial typesetting cannot suppress the marker. A new independent `table-auditor` rasterizes every main-paper and populated-appendix page after Stage 5 and again after final polish, catching custom alignments, image tables misclassified as figures, raster text, clipping, and source-level escape paths; its PASS is a completion precondition and REVISE enters a capped repair/rebuild/re-audit loop. `requirements.system` and the updater warning now name this autonomous `pdftoppm` dependency explicitly. CI-enforced LaTeX fixtures cover the former bypasses and false-positive controls using the deployed package order, same-selector updates backfill the new loop state, and the assembly matrix covers the new agent across five runtimes and report-mode pruning.

## [2.24.2] — 2026-08-13

**WRDS utilities now resolve project credentials independently of the caller's working directory (#229).** `wrds_client.py` and `wrds_server.py` pass their deployed project's `.env` path explicitly to `python-dotenv`, including the server's operator-approved credential reload. This closes the silent `python -c` failure outside the project root without opening a WRDS connection, and the offline regression imports each shipped module from an unrelated working directory using dummy credentials. The legacy `wrds_utils.py` call site named in the original report had already disappeared when that module became a server-backed compatibility wrapper.

## [2.24.1] — 2026-08-12

**Seeded Gate 4 no longer reopens a fixed research direction through strategic score optimization (#257).** Both `--seed` and `--faithful` still run the independent scorer pair, but their aggregate score and verdict are diagnostic: a specifically cited correctness/rigor challenge returns to its existing owning audit, and otherwise the run advances to Stage 5 while recording seed-pinned novelty, importance, surprise, fertility, scope, or format ceilings as limitations. Gate 4 skips `branch-manager`, numeric plateau waiting, deepening-for-score, and aggregate-score abandonment for seeded runs. Unseeded routing is unchanged. Faithful mode retains its independent contract-drift audit before Stage 5. The dedicated faithful Gate 4 override was deleted in favor of the shared seeded route, and a focused five-shape assembly regression guards the distinction, including faithful empirical and experimental evidence paths.

## [2.24.0] — 2026-08-10

**Deployments now assemble exclusively from the checkout containing `setup.sh` (#256).** Setup no longer clones a moving remote, performs sparse-checkout fallback, or reads `ZEROPAPER_REPO`; selecting or updating a release is an ordinary Git checkout operation outside the deployer. It captures the declared inputs into a verified private local snapshot before sourcing any build module, then executes the snapshot's isolated launcher/coordinator pair so even an atomic replacement of the live coordinator cannot mix coordinator bytes with recorded provenance. After the launcher bootstrap, all assembly consumes that snapshot, so a transient post-bootstrap build-input change restored before final verification cannot produce different output under identical provenance. Full deployments reject modified or untracked build inputs before creating the project, fail closed when Git cannot inspect cleanliness, reject build-input symlinks that could import mutable bytes from outside the checkout, and include `.env.example` because it seeds deployed configuration, while `.env` remains separate operator configuration. Cleanliness is verified by comparing the effective files and directories directly to the initially recorded source commit, bypassing index flags and Git ignore/exclude rules; a config-neutral `ls-files` read separately verifies index health without executing ambient Git helpers. Root `setup.sh` uses the absolute OS interpreter (`/usr/bin/python3 -I`) as an isolated launcher that sanitizes the environment before Bash can read `BASH_ENV`, removing startup hooks, exported functions, inherited shell/path controls, activated-environment paths, and ambient Git repository/object/index/config overrides before it starts the coordinator. Core commands resolve from a trusted system-first control path; operator-installed `uv`, `claude`, and `gh` executables are selected separately by exact safe path, excluding the checkout and active virtual/Conda environments even through symlink or case aliases. Embedded Python is isolated from caller-CWD modules and ambient import paths, while local assembler imports use a private temporary bytecode prefix so ignored checkout caches are never executed. Production Git initialization uses an empty private template and hook/filter/fsmonitor/signing-neutral commands, so ambient Git configuration cannot execute output-affecting code after verification. The old `--local` source-selection/debug flag is removed and its fast-path behavior becomes `--assemble-only`, which requires an explicit destination, permits dirty development state, validates the complete assembly, and stops before provisioning, project Git initialization, commit, or publishing; it never replaces a file, symlink, source input, or foreign non-empty directory, and containment uses filesystem identity so case-insensitive path aliases cannot evade the boundary, and only a real (non-symlink) `test_output/` owned by this checkout is disposable scratch space. Characterization tests and `update.sh` use that path. Manifests now record sanitized checkout repository identity, the full source commit, dirty state, a deterministic SHA-256 digest of effective build-input content and permission modes, a checkout update channel, and every deployment selector including faithful independently from seeded; local remotes never expose full filesystem paths. Final snapshot + live digest/recorded-commit cleanliness checks reject persistent concurrent changes. `update.sh` also enters through the same trusted absolute OS Python rather than caller `PATH` before Bash startup hooks can run, and refreshes this provenance while preserving the original deployment fingerprint/date, derives the version from the verified fresh manifest, and uses manifest-owned internal copies of dependency specifications and the dotenv guard rather than rereading the live checkout; its child setup snapshot/cache/registries stay inside the same policy-denied update control directory as the fresh assembly, and `uv` is pinned only after active-environment and project/template/temp/cache path exclusion. The updater rejects targets at/above its template checkout or inside `deploy_assets/` before creating control state, leaves no control directories during `--dry-run`, removes an empty extension-dependency staging parent when the final extension is cleared, and keeps faithful/seeded selection consistent across manifest, runtime agents, pre-launch pipeline state, and seed bootstrap paths; compatible pre-launch autonomous mode/extension overrides merge their missing state schema and output-directory skeleton, while manual/report extension refreshes skip nonexistent autonomous state; prepared seed and selector content rolls back on any later update failure, and state commits only at the final manifest boundary. Started runs reject mode/extension/seed migration; cross-variant, autonomous↔manual, and report↔autonomous changes require fresh deployment. Every supported runtime launcher keeps a shared lock on a parent-Bash-owned project-directory descriptor for its lifetime and update acquires the exclusive side before creating target paths; each trusted parent waits while its runtime/update body runs with that descriptor closed, without a pathname lock, separate holder, or readiness file, so a running agent cannot race managed replacement; arbitrary non-launcher same-UID writers remain the documented, tracked [#259](https://github.com/alejandroll10/zeropaper/issues/259) boundary. Focused source-policy tests prove there is no internal fetch, dirty production input fails before destination creation, development assembly records its dirtiness/content, and non-build docs plus `.env` do not trip the cleanliness gate. The unavoidable self-attestation limit before root `setup.sh` establishes the baseline is documented and tracked in [#258](https://github.com/alejandroll10/zeropaper/issues/258); operators must not allow concurrent writes to the template checkout during invocation. Production publication/provisioning, update ownership, all supported assembly shapes, and the deployment/editing skills were migrated to the new contract.

## [2.23.7] — 2026-08-08

**Deployment assembly now has explicit infrastructure and project ownership, with `setup.sh` reduced to a fail-fast coordinator (#255, closes #236).** A 39-shape golden characterization first captured complete local deployments (files, modes, symlinks, empty directories, manifests, and CLI contracts), then configuration, runtime documents, five-runtime agent assembly, project bootstrap, infrastructure docs, skills/utilities, extensions/injections, provisioning, and finalization moved behind sourced module interfaces. Template-owned producers now create or verify paths through hardened `infrastructure_*` helpers that register replacement ownership at the write site; mutable paper/state/seed/license content remains bootstrap-owned, while `.env` alone is explicitly merge-managed. Manifest arrays are derived structurally from the producer registries with exact historical ordering, including extension subprocess outputs, eliminating the distant candidate lists and their silent two-place failure mode. Ownership paths reject traversal, control characters, symlink components, and non-regular file targets before mutation. Venv/core/SSJ/extension dependency installation is single-sourced in provisioning order, while git initialization, initial commit, opt-in publication, and completion reporting live in finalization. CI runs configuration, cleanup, ownership/update, production provisioning/publication, and full characterization fixtures. Iterative independent GPT-SOL audits found and closed reentrant config leakage, inherited-temp cleanup, pre-validation writes, registry control-character corruption, symlink escapes, and missing production CI coverage; final fresh rounds were clean.

## [2.23.6] — 2026-08-08

**Running or resuming a deployed workflow now explicitly authorizes every prescribed subagent launch (#238).** A short, uppercase instruction at the top of every autonomous-pipeline and report-mode runtime document tells the orchestrator not to ask again for confirmation or perform the subagent's work itself. This closes the ambiguity that let Claude Code over-generalize the separate `Workflow` opt-in rule to ordinary `Agent` launches and silently stall at evaluation gates.

## [2.23.5] — 2026-08-07

**A clean-checkout CI guard now detects stale Codex-facing dev mirrors (#233).** Every pull request and push to `main` runs the canonical `sync_dev_instructions.sh`, force-stages only `AGENTS.md` and `.agents/skills`, and fails if the regenerated paths differ in type, executable mode, or bytes from the proposed commit. This avoids reimplementing the generator in the discarded index-only pre-commit checker, whose repeated false PASSes included normalized trailing newlines and partially trusted generated headers. The generator now normalizes `AGENTS.md` to a regular, non-executable copy while preserving existing read/write permission bits, stages it through an atomically created same-directory tempfile rather than a predictable path that could redirect the write through a symlink, compares symlink-target bytes without newline normalization, rejects hidden or invalid canonical skill directories, sweeps hidden mirror entries, and tests symlink support in a unique temporary directory rather than deleting a foreign fixed-name probe path. Focused regressions cover exact document bytes, type, permissions, and every header line; tempfile and probe-path safety; invalid canonical directories; and missing/new/extra/hidden/malformed skill links, including ignored generated additions and resolvable newline targets. The check becomes merge-blocking when its status is required by branch protection; until then it still reports drift on every PR and after any direct push to `main`.

## [2.23.4] — 2026-08-07

**GitHub publication is now an explicit opt-in (#234).** A normal production `setup.sh` run creates and commits only a local repository; it no longer creates a repository in `automated-papers-produced` merely because the operator is an authenticated organization member. `--publish` is the sole enablement path, prints the exact organization/name/visibility before any GitHub mutation, and retains `PUBLISH_ORG` / `PUBLISH_VISIBILITY` as configuration rather than hidden activation switches. `--no-publish` makes the safe default explicit in automation. Contradictory publish flags, `--publish --local`, empty or invalid publish configuration, and `--publish --mode report` fail before project creation. Missing GitHub CLI authentication or organization membership leaves the committed local project intact with a warning; a create/push failure preserves the local commit, surfaces `gh`'s error, and treats remote state as uncertain because repository creation may have succeeded before a later step failed. `setup.sh --help`, the deployment skill, and the README now state the contract directly.

## [2.23.3] — 2026-08-07

**Every shipped Codex skill now satisfies the complete bundled skill-authoring validator (#237).** Five rendered descriptions (`ssj`, `call-reports`, `tnic`, `trace-bonds`, and `revelio`) used ASCII arrow/comparison notation containing `<` or `>`, which Codex's bundled `skill-creator/scripts/quick_validate.py` rejects even though the current runtime loader accepts it. Their seven base/override metadata fields now use equivalent prose. A shared build-time validator single-sources the complete public contract — allowed and required fields, field types, hyphen-case name syntax, edge/doubled-hyphen rejection, 64/1024 Unicode-character caps, and the description angle-bracket ban — for both deployed-skill assembly and the dev-skill mirror; it also retains the repository's stricter non-empty-field requirement. Unit coverage exercises every rule, and an exhaustive integration assembles and validates every Codex-targeted skill metadata set while preserving the intentional `codex-math` exclusion.

## [2.23.2] — 2026-08-06

**Codex skills are validated against the real 64-character name and 1,024-character description authoring limits (#231).** The deployed-skill assembler previously counted description bytes and could reject valid multibyte punctuation while failing to check the name cap; it now enforces both limits in Unicode characters, matching Codex's bundled `skill-creator` validator. The dev-skill mirror validator now enforces the same authoring contract instead of treating runtime-loader tolerance as permission to exceed it, the canonical `edit-pipeline` guidance identifies the public Codex validator as the source of truth, and stale sync-script commentary about the removed clone-and-strip deployment architecture is gone.

## [2.23.1] — 2026-08-06

**WRDS authentication failures now stop every automated login path after one credential-bearing attempt (#224).** The v2.22.1 latch covered the obvious PAM string but still lost wrapped `EOFError`/SQLAlchemy `orig` causes, swallowed lazy authentication inside `SELECT 1`, and missed a rejection on the post-recovery retry; all three now arm the same terminal latch before another health probe can reconnect. Recovery no longer calls `wrds.Connection.connect()`, whose implementation silently swallows its first exception, prompts, and can issue a second login: the server constructs with `autoconnect=False` and invokes the pinned `wrds==3.5.0` fail-loud one-attempt engine primitive. A runtime distribution-path and SHA-256 source-contract check covers both the constructor and primitive before credentials are touched, so an ambient, shadowed, or changed package fails closed; after connection, a SQLAlchemy engine hook blocks its own transparent invalidated-connection reconnects and routes them through guarded recovery. The old Tier-3 full reconnect is gone; after rollback, exactly one pool rebuild is permitted, and any failed or ambiguous credential-bearing rebuild latches. Every startup and pool rebuild writes and directory-fsyncs a durable `LOGIN_ATTEMPT_IN_PROGRESS` record **before** touching credentials, and clears it only after a verified query; a process death during Duo or connection setup therefore leaves a restart-blocking record instead of resetting the budget. The per-user latch moved out of runtime/temp storage into `~/.cache/zeropaper/wrds`, so logout, reboot, and a new pipeline session cannot reset it; an existing v2.22.1 runtime latch is securely copied forward and retained until verified/operator-approved clear. Startup auth failure keeps the port-owning process alive in a blocked state, and the operator CLI clears a disk latch only on proven connection refusal—timeouts and resets retain it. Latch storage uses no-follow reads, owner/type/write-mode validation, `0600` atomic replace, file and directory fsync, strict clear errors, and fail-closed handling for unreadable, symlinked, or empty state. Because the daemon outlives deployment updates, every command carries a safety-protocol version: updated clients use a DB-free, versioned `safety_hello_v2` before even pinging, every DB-touching wire command has a `safe_*_v2` name an old daemon treats as unknown (closing the preflight/request race), and new daemons reject old clients before database work. Concurrent starters recognize both a pre-spawn live marker and a post-spawn singleton loser, then join the winning readiness wait without launching another process or surfacing a false failure. The deployed WRDS skill and dev scripts no longer teach or use a direct `wrds.Connection()` fallback; the skill explicitly warns that libraries, readiness loops, and supervisors may retry one apparent call internally and makes protocol mismatch operator-only; and legacy `wrds_utils` is a compatibility proxy over `wrds_client`. Client data APIs preserve terminal auth/safety failures, Stage 3a checks the latch before its one permitted restart, and `start_services.sh` retains the child PID and joins an existing startup. The offline regression covers cause/context/orig classification, lazy and post-recovery auth, ambiguous failures across 25 pings, installed/runtime/shadowed dependency contracts, real SQLAlchemy invalidation, write-ahead crash/restart and live-timeout behavior, legacy migration, old-daemon refusal, both concurrent-start races, durable/atomic/failing/empty latch storage, typed APIs, direct-path absence, and compatibility routing; Python/shell syntax, empirical `--local` assembly, shipped-file identity, and iterative independent GPT-Sol audits complete verification. No live WRDS connection or Duo prompt was used.

## [2.23.0] — 2026-08-06

**Deployment is now an allowlist: build inputs live under `deploy_assets/`, production assembles into an empty project directory, and the clone-then-strip denylist is gone (#232).** The old flow `git clone`d the whole template repo into the project and then deleted everything that must not ship — a denylist that fails open: anything new in the repo shipped into every research project unless someone remembered a removal, and real deployments were carrying `update.sh`, `victor1_postmortem.md`, and four `split_guard_audit*.md` files. Step 1 (pure move, byte-identical output): `templates/`, `extensions/`, the build half of `scripts/`, `launch.sh`, and `dashboard.html` moved under `deploy_assets/`; `scripts/sync_dev_instructions.sh` stays at the root as dev tooling; `setup.sh` splits `SRC_ROOT` (checkout/clone root, where `VERSION` lives) from `TEMPLATE_ROOT` (the build-input tree) and `update.sh` gains `ASSETS_ROOT`. Step 2 (the mechanism change): production `setup.sh` sparse-clones `deploy_assets/` in cone mode into a mktemp source tree (root files like `VERSION` and `LICENSE` come along free; full-clone fallback for old git/transports), creates the project directory **empty**, `git init`s it, and assembles outputs into it; the source tree is deleted wholesale by a single shared EXIT trap (which now also covers the tier-vocab tempfile and the manual-mode catalog dir on error exits). Deleted outright: the `rm -rf`/`rm -f` cleanup denylist, the `DEV_SKILLS` snapshot + checksum collision guard, the v2.22.2 `.agents/skills` dev-symlink early strip, and the production-only `.opencode` alias guards — the dev tree and the assembly destination never coexist anymore, so the entire hazard class those defended against is unreachable, and a forgotten copy now surfaces as a loud missing file (fail-closed) instead of dev content silently shipping (fail-open). Three behavior fixes ride along: production version stamps are real again — the tmp clone keeps its `.git`, so `template_version` records `<semver>+<hash>` where every prior production manifest said `+unknown` (the old flow ran `rm -rf .git` before stamping); mode overlays now resolve against `TEMPLATE_ROOT` instead of the invoking checkout, closing a version skew where production mixed local-checkout overlays with clone-sourced everything-else; and `LICENSE` ships via an explicit copy (deployments auto-publish and `arpipeline.sty` cites LICENSE §2) while the unintentional passengers (`update.sh`, `README.md`, `.env.example` et al.) stop shipping. A new manifest trip-wire is documented in CLAUDE.md and the `edit-pipeline` skill: a deployed path must exist **before** the manifest emission block runs, because membership is decided by live `is_file()`/`is_dir()` probes — round-1 adversarial review caught `launch.sh`/`dashboard.html` briefly being copied after that checkpoint, visible only in production manifests (`--local` copies them earlier), and the fix moved the copies to clone time. Verified: a 14-config `--local` matrix (all variants × modes × extensions × seed/faithful/manual/light/halt) byte-identical to a pre-refactor baseline after normalizing the fingerprint UUID and version hash, four true production deploys audited for leaks/completeness across all five runtimes, and the `test_opencode_setup.sh` setup+update integration suite passing. Proposal B from #232 (splitting the repo in two) is explicitly not taken: the subfolder boundary delivers the namespace separation at none of the cross-repo sync cost.

## [2.22.2] — 2026-08-05

**A Codex session started in the template repo now gets the same instructions and dev skills a Claude session does.** Codex loads `AGENTS.md` automatically and discovers repo skills under `.agents/skills`, but `AGENTS.md` here was a three-line pointer at `CLAUDE.md` and the two dev skills (`edit-pipeline`, `deploy-project`) existed only under `.claude/skills` — so Codex could begin template work having read neither. `CLAUDE.md` and `.claude/skills/` stay canonical; `scripts/sync_dev_instructions.sh` regenerates `AGENTS.md` as a copy carrying a generated-file header, and exposes each dev skill as a relative symlink at `.agents/skills/<name> -> ../../.claude/skills/<name>`. The script is idempotent, discovers skills rather than hardcoding a name list (matching the snapshot-based dev-skill handling in `setup.sh`), verifies each link actually resolves to a readable `SKILL.md`, prunes stale links, and refuses outright to overwrite a real file or directory sitting at a mirror path rather than silently clobbering it. It also checks the frontmatter against Codex's two caps, which behave differently and are both measured in **characters**, not bytes — a distinction that bites here, since every one of our descriptions uses em-dashes and `edit-pipeline`'s is 586 characters against 590 bytes. `name` > 64 is a hard failure, because `codex-rs/skills/src/parser.rs` calls `validate_len()` on it and the skill fails to parse. An over-long `description` only warns: openai/codex#29006 (merged 2026-06-19) removed length rejection at load — the parser now checks only that the description is non-empty — and moved the cap to model-visible rendering, where the catalog entry is truncated to 1021 characters plus `...` while the skill itself still loads and `$skill` injection and `skills.read` stay full-fidelity. What degrades is implicit skill selection, which routes off the truncated text. Refusing to sync would therefore be stricter than Codex is. The separate aggregate skills-metadata budget across all rendered descriptions (openai/codex#24299), which also truncates, is deliberately not checked: it is 2% of the context window in **tokens**, not characters — `skill_metadata_budget()` returns `SkillMetadataBudget::Tokens` and falls back to `Characters` only when the context window is unknown, so the `budget_limit=5440` in that issue is `272_000 × 2%` in tokens. It depends on the model and on what else is installed, so it is not knowable from this repo. The shape is a **real** `.agents/skills` directory containing **symlinked skill folders**. The real directory is a `setup.sh` requirement rather than a Codex one — Codex does follow a symlinked `.agents/skills` (per the maintainer on openai/codex#11314, with unit tests for both the global and per-project paths), but in a deployed project that path is where `assemble_codex_skills.py` writes the real Codex skills, so it must be real and writable there, and a wholesale symlink into `.claude/skills` would let a colliding `skill_id` write straight through into the meta-repo's canonical skill. Symlinking `SKILL.md` itself *is* unsupported (openai/codex#9365 — "We support symlinks to a skill directory, not the SKILL.md file itself"). The relative target is `../../.claude/skills/{name}`, and getting that depth wrong fails silently: openai/codex#11314 was closed not-planned precisely because it was never a bug, only an invalid relative target. Codex's live-reload watcher also does not fire through a symlink, so canonical `SKILL.md` edits require relaunching the Codex CLI. `AGENTS.md` is deliberately a copy rather than a symlink to `CLAUDE.md`: `setup.sh` writes `CLAUDE.md` and then `AGENTS.md` by bare filename inside the clone, so a link would be followed and would clobber the deployed `CLAUDE.md` with the Codex runtime doc. Because `.agents/skills` is tracked (a fresh clone has the skills immediately) and deployment happens by `git clone`, `setup.sh` now breaks those symlinks right after the clone, before `assemble_codex_skills.py` — which does `mkdir(exist_ok)` + `write_text` and never wipes — writes the deployed project's real skills into the same directory. That strip needs no checksum guard, unlike the `.claude/skills` one: the assembler only ever creates real directories, so a symlink at that depth is unambiguously a dev exposure. It runs at clone time rather than in the cleanup block because deferring is unsafe — `mkdir(exist_ok)` on a symlink-to-dir succeeds, and a future `skill_id` colliding with a dev-skill name would then have `write_text` write *through* the link into the meta-repo's own `.claude/skills/<name>/SKILL.md`. Both mirrors are dev-only and get no manifest entry. Nothing in git enforces that the generator ran, so the mirrors can still drift silently — a known, open gap tracked in #233. A validator was written and cut before merge: adversarial review found it wrong seven times across four rewrites of its core comparison, twice reintroducing the very false PASS the previous fix had closed, so it is filed as unsolved work rather than shipped half-right. The idempotent generator is the interim answer — running it tells you whether you were out of sync. The generator normalises the environment it inherits before anything depends on it, because each of these can only break them and several did: bash applies an exported `SHELLOPTS` *before* a script's own `set` line, so `noglob` made the mirror globs expand to literal pattern strings — the sync silently did nothing while exiting 0, and the check then reported PASS with a mirror genuinely missing — while `noclobber` turned a leftover `.tmp` into a hard failure; `CDPATH` made `cd` with a bare relative operand echo its resolved path into the command substitutions that derive the repo root, which broke `git commit` outright once the check was wired as a hook; and `GIT_DIR`/`GIT_WORK_TREE` pointed the check at an entirely different repository, reporting PASS while real drift sat unreported (`GIT_INDEX_FILE` is deliberately left alone — a pre-commit hook sets it to the index being committed, which is exactly what should be read). An `EXIT` trap removes the `AGENTS.md` staging file so an interrupted run cannot strand one. It resolves its own path before deriving the repo root, so invoking it through a symlink cannot anchor it outside the checkout. The generator also refuses when `.agents` or `.agents/skills` is itself a symlink: `mkdir -p` no-ops on a symlink-to-directory, after which every link it writes lands inside that target while its `../../` string still assumes the intended location — scattering broken links through a directory the operator never chose, then failing with an error blaming the skill rather than the hijacked path. The post-change review rule in `CLAUDE.md` now names the reviewer per client (Sonnet under Claude, GPT Sol under Codex) instead of "Sonnet-like".

## [2.22.1] — 2026-08-04

**A rejected WRDS credential no longer retries itself into an account lockout.** A PAM rejection arrives as a psycopg2 `OperationalError`, which `_is_conn_error()` classified as a recoverable dropped socket — so it was retried, though retrying a wrong password can never succeed. Because `healthcheck()` calls `_recover()` on every unhealthy ping and `_recover()`'s Tier 2 and Tier 3 each perform a fresh login, a single ping cost two failed authentications, while `start_services.sh` pings up to 120 times and `wrds_start()` another 120. One readiness run against an expired password could therefore fire hundreds of logins; WRDS locked the shared account, taking the empirical pipeline down for every project on the host. Authentication is now a third error class, distinct from connection and query: checked *before* `_is_conn_error()` (which explicitly excludes it), terminal rather than recoverable, and **latched** — the first rejection sets `WrdsState.auth_failed`, after which no code path attempts another login and every command fails fast with `error_kind: 'auth'`. `_latch_auth_failure()` fires from each recovery tier so a Tier-2 rejection cannot fall through and spend Tier 3 on the same doomed credential; `healthcheck()` answers from the latch without touching the network; the server exits 2 at startup instead of dumping a traceback whose proximate cause (`EOFError` from `wrds`'s interactive prompt fallback, under `nohup`) hid the real one. The latch persists to a host-global file beside the pid file, so restarting the server — which `start_services.sh` does at every pipeline launch — is not a free way around the gate; it clears on reboot or logout so a stale latch cannot outlive a fixed credential. Clearing it is an operator action: `python code/utils/wrds_client.py unblock` reloads `.env` with override (the fix lands in the file, while the running server holds the value it was spawned with) and spends exactly one attempt, re-latching on a second rejection and resetting the budget on success; the same command clears a persisted latch and starts the server when none is running. Both readiness loops in `start_services.sh` break on a latch and exit 2 with operator instructions rather than grinding out a generic 120s timeout, and `wrds_start()`'s wait now has three exits (ready / rejected / timeout) including detection of the child's exit code. The WRDS skill gains an escalation rule: a credential rejection is terminal, agents halt and record it in `process_log/degradation_ledger.md`, and must never call `unblock` — that is the operator's approval gate. `scripts/test_wrds_auth_latch.sh` imports the shipped module and stubs only its network edges, covering classification against a real PAM string, one login across 25 pings, zero while latched, restart non-bypass, and both unblock outcomes.

## [2.22.0] — 2026-08-04

**OpenCode Bash/task execution is now OS-confined (#220).** `./launch.sh opencode` wraps the persistent authenticated server and every attached client in Anthropic Sandbox Runtime, while `--once` wraps the whole TUI. The deployed `.opencode/sandbox.json` permits project, project-scoped OpenCode state, and approved cache/runtime writes; denies reads and writes under `~/.ssh` and `~/.aws`; protects Codex auth/config/plugin trees plus project credentials/manifest; and leaves network egress unrestricted for open-ended literature, package, and data hosts. Because SRT's CLI schema requires a finite domain allowlist, a fail-closed adapter uses its library API to request filesystem-only confinement without isolating the host network. The policy, adapter, launcher, OpenCode config, driver helper, and control state are sandbox-immutable; the narrow host driver uses isolated Python and a PATH stripped of sandbox-writable entries, and performs repository progress hashing inside SRT so Git filters/fsmonitor cannot cross the boundary. Missing Linux paths are materialized before bubblewrap resolves policy, credential/path aliases and root execution fail closed, and legacy control state is migrated; a still-live old unconfined server/group must be stopped before either launch mode proceeds. `update.sh` likewise validates managed ancestors and no-follow state/credential files before using host authority. Setup/update, manifest, mocked lifecycle, and `scripts/test_opencode_sandbox.sh` cover deployment, process ownership, allowed project/state/cache writes, protected-control immutability and hard-link denial, denied credential reads and external writes/deletes (including a nested child), and outbound HTTPS.

## [2.21.2] — 2026-08-04

**The codex driver no longer aborts healthy runs whose worker writes its report incrementally (#223).** `wait_for_workers()` decided a detached worker was finished by looking at its output file: non-empty meant done, and that test ran *before* the wrapper-pid liveness probe, so the stronger signal was unreachable for any worker that had written a byte. Several agents — the novelty-checker most visibly — stream their report search by search, so their output file is non-empty from the first result onward. The driver therefore stopped waiting immediately and re-prompted; the orchestrator, correctly obeying poll-don't-relaunch on a live sentinel, spent each turn polling a partial report without committing; five such ~15s turns tripped the fast-cycle guard. Two long finance runs died this way with their worker healthy and minutes from finishing, one of them two minutes before its verdict landed. Liveness now decides and file content only breaks ties: a live wrapper pid means pending regardless of output, and a dead wrapper always clears its sentinel — with a distinct message for the finished-but-uncleaned case, since a sentinel outliving its wrapper also parks the *orchestrator*, which will neither route the finished report nor relaunch a lost worker. Old-format sentinels carrying no wrapper pid fall back to the file, but now require it to be both non-empty and untouched for `WORKER_STALE_MTIME` (default 600s) — a still-streaming report keeps its mtime moving, which mere non-emptiness cannot distinguish. The stuck-model abort additionally prints any sentinel still present, because that fact alone redirects the post-mortem away from "the model is refusing." Both `stat` probes and `date` are digit-validated rather than trusted, since GNU `stat -f` is filesystem mode with a different format-sequence set and a literal `%m` reaching `$(( ))` would be a fatal arithmetic error under `set -e` — killing a driver that should merely have kept waiting. `scripts/test_launch_workers.sh` sources the shipped function out of `launch.sh` and covers all of it: streaming output, both dead-wrapper cases, pid reuse, cap timeout with its `WAIT_CAPPED` accounting, the mtime threshold on both sides, and a stubbed `stat` returning junk. The opencode driver is unaffected: it tracks background work through server-side quiescence, not sentinels. One assumption this leaves standing — worker liveness is inferred from the wrapper pid, so a pid-targeted kill can orphan a still-writing worker — is now recorded in `LIMITATIONS.md`.

## [2.21.1] — 2026-08-04

**OpenCode server replacement now proves whole-process-group termination (#222 follow-up).** The v2.21.0 cancellation boundary authenticated the server leader by PID/start/PGID/command, but waited only for that leader PID to exit. A TERM-resistant Bash/tool descendant in the same server process group could therefore outlive the leader and continue mutating artifacts after a replacement server and recovery baseline were published. Shutdown now authorizes the exact group while the leader identity is still valid, tracks group liveness through TERM and KILL, and clears server state only after the entire PGID is confirmed gone. KILL escalation is group-only after authorization, avoiding a PID-reuse target; startup reaping revalidates the exact PID/start token and rechecks PGID before escalation. A durable startup marker closes the pre-identity crash gap and makes later launchers fail closed if an incomplete server may remain alive. If a later launcher finds the recorded leader gone but its group still alive, it retains the identity and fails closed rather than signaling an unauthenticated group or starting a replacement. A lifecycle fixture covers a server leader that exits on TERM while its same-PGID descendant records and ignores TERM.

## [2.21.0] — 2026-08-04

**OpenCode background subagents now work in unattended pipelines (#222).** OpenCode's experimental `task(background=true)` support is viable only while the server that owns its in-memory job registry remains alive: a plain ephemeral `opencode run` exits with its client and aborts the child, while `opencode serve` plus an attached client lets the child finish, injects its result into the parent, and autowakes the parent without another client. The launcher now uses that verified architecture. It starts or reuses an authenticated localhost server, attaches every headless turn to it, and enables `OPENCODE_EXPERIMENTAL_BACKGROUND_SUBAGENTS`; older OpenCode versions whose task schema omits `background` continue through foreground calls.

The driver does not race the native wakeup. After an attached turn exits, a new stdlib-only control client follows the parent and its direct child sessions through OpenCode's HTTP API, causally pairs each launch generation with its own persisted synthetic completion/error user notification and a later completed/error parent response, discovers further background generations spawned by that response, and only then accepts two stable all-idle samples before issuing an external continuation. Generation identity matters because resuming a `task_id` reuses its child session ID. The parent-bound pending-generation ledger is reconstructed and atomically replaced from parent messages after a driver restart; an always-present parent/server epoch plus a server-instance-bound history baseline detect replacement-publication crashes and retire generations that can no longer notify, while even a reused parent with no pending generations must reach stable quiescence before another prompt. Turn timeouts kill only the attached client's process group, cancel every child and the parent, confirm status-only quiescence, and replace the server instance before advancing the baseline, so no late notification/autowake can cross the cancellation boundary. Recovery intent is durable and idempotent: a unique token remains on disk until it is observable in a native user prompt, letting restart distinguish “not dispatched” from “already dispatched” without duplication. Terminal pipeline states and signals shut the server down; nonterminal driver failures and exact-but-temporarily-unhealthy servers are preserved so a later launch can reuse in-flight work without treating transient API failures as a restart or duplicating a prompt.

A kernel-held project `flock` prevents concurrent launchers from prompting the same parent or stopping each other's server. Server cleanup validates PID, start token, process-group leadership, and the expected `opencode serve` command before group signaling. Startup traps cover partial state, server identity is published as one atomic bundle, a partial cached state is recovered through its PID/start identity, and the random server password is created atomically at mode `0600`; the launcher also fixes the Basic-auth username rather than inheriting a conflicting caller setting. All runtime state lives under ignored `process_log/` paths, malformed API/event/state shapes fail closed, and a pre-dispatch first-turn quarantine is removed only after exactly one consistent session ID is atomically cached and validated as local, preventing interrupted parent creation from duplicating. Session discovery accepts only nonempty absolute directories resolving to the physical checkout.

The upstream boundary remains explicit: background-job state is process-local, so a server crash can still interrupt an uncheckpointed child. Recovery restarts the server and instructs the parent to reconcile child transcripts and required artifact paths before resuming or relaunching once. OpenCode session/manual/report guidance now uses background work only for independent fan-outs, forbids polling and duplicate launches, and requires artifact verification at gates. Tests cover API auth, local-session filtering, a deliberately delayed child-idle → notification → parent-autowake transition, pending-child reconstruction, partial abort failure, delayed cancellation quiescence, multiple-child abort ordering, concurrent-driver rejection, interrupted startup, partial-state recovery, fresh/reused servers, timeout recovery, fail-closed first-turn reconciliation, terminal cleanup, and deployment-manifest installation.

OpenCode still has no native `/loop` command; the persistent launcher remains the unattended continuation loop.

## [2.20.0] — 2026-08-03

**OpenCode runtime.** Deployments now include `.opencode/agents/*.md` generated from the shared agent metadata and bodies, with per-agent permissions and every tier mapped to `opencode/deepseek-v4-flash`. Base, variant, mode, and extension assembly paths all participate; pruning, injections, marker resolution, and the deployment manifest cover the fifth agent tree.

OpenCode reuses the existing Claude-compatible `SKILL.md` catalog through its native on-demand `skill` tool. The launcher selects `.claude/skills` explicitly to avoid duplicate IDs from the parallel `.agents/skills` compatibility tree. Shared `AGENTS.md` guidance now dispatches OpenCode agents through foreground native `task` calls.

`./launch.sh opencode` provides a resumable non-interactive session driver with stale-session validation, terminal-state detection, and a five-turn no-progress cost guard; `--once` opens the interactive TUI. `opencode.json` pins the model and project file-tool permissions. OpenCode Bash is not kernel-sandboxed, so the security limitation is stated in README and `LIMITATIONS.md` rather than implied away.

Follow-up hardening makes unattended execution explicit: session sharing is disabled, `doom_loop` cannot block waiting for approval, every turn has a process-group watchdog, and the cost guard distinguishes completed native subagent work from empty fast turns while retaining an absolute churn ceiling. Timeout shutdown gives Bash descendants the configured grace period before killing them. Cached and reconciled sessions must belong to the current physical checkout, and reconciliation fails closed when its pre-run session snapshot is unavailable. OpenCode agents receive foreground/checkpointed Bash guidance instead of Claude's unsupported `run_in_background` argument. A mocked launcher regression suite covers interactive launch, fresh/resumed/stale/malformed and cross-project sessions, invalid reconciliation baselines, substantive-tool progress, descendant cleanup, and forced timeout recovery.

The launcher safely exports the project `.env`'s `OPENCODE_API_KEY` without evaluating the file, while preserving an already-exported value. This makes the documented per-project credential path work for both interactive and headless launches without requiring a separate shell export or global OpenCode auth state.

---

## [2.19.0] — 2026-08-03
**`--light` now means light, including the orchestrator.** v2.18.2 fixed the flag's *subagent* half on codex; the first real light run under `./launch.sh codex` immediately exposed the other half — the banner read `model: gpt-5.6-terra`, because the orchestrator is launched by `launch.sh` and inherited the CLI's session default. Every subagent was Luna; the one process doing stage routing, gate decisions, and the whole fan-out was not. Same story on claude and gemini. The flag now pins both halves.

**Two mechanisms, because the halves are pinned at different times.** Subagents are pinned at assembly time (`--model-override` through each assembler's tier table). The orchestrator is pinned at launch: `--model <tier>` for claude and gemini, `-c model="<tier>"` for codex. The codex form is deliberate — `codex exec resume` accepts only `-c`, and the driver resumes on every turn after the first, so a flag-form pin would have applied to turn 1 and silently reverted for the rest of the run.

**The launcher does not carry a fourth copy of the tier table.** `light_orchestrator_model` reads the tier *back* from the assembled agents — the only copy guaranteed current: it already went through each runtime's own `MODEL_MAP`, it survives `update.sh`, and on claude it reflects the launch-time heal that runs immediately before. The pin fires only when `.deploy_manifest.json` records `flags.light` **and** every assembled agent agrees on one model. The manifest check is what makes it correct rather than merely plausible: grok's roster is uniform (`grok-4.5`) in *every* deployment, so roster uniformity alone would have pinned a "light" tier on runs that never asked for one. Grok's branch doesn't consult the helper at all — single-model table, nothing cheaper to drop to.

Best-effort in the safe direction throughout: a pre-manifest deployment, an absent `python3`, or an unreadable agents dir yields no pin and the launch proceeds on the CLI default. Verified against three real deployments — a light one (codex `gpt-5.6-luna`, claude `sonnet`, gemini `gemini-3-flash-preview`), a non-light one, and a pre-manifest one; only the first produces a pin.

**Stated plainly in the docs rather than buried:** the orchestrator is the single process where a cheap model costs the most, so `--light` is now documented as a deliberate choice for drafts, smoke tests, and runtime shakedowns — not a default for a paper you intend to submit. That is a real trade the flag now makes on your behalf, and it should be visible before you pick it, not after.

---

## [2.18.2] — 2026-08-02
**`--light` becomes a real flag on the codex runtime.** It was a Claude-side flag wearing a cross-runtime name: `setup.sh` passed `--model-override sonnet` to the claude, gemini, and grok assemblers, but `assemble_codex_subagents.py` had no such argument, so a `--light` deployment launched under `./launch.sh codex` ran the full pinning — 7 agents on Sol, 27 on Terra, only 17 on Luna. The gap was invisible while every codex agent was a flat `gpt-5.5` and became a silent cost bug when the per-agent Sol/Terra/Luna tiering landed. It was documented as a known limitation rather than fixed; this closes it.

The codex assembler now takes `--model-override` and maps the Claude alias through its own tier table (`fable → gpt-5.6-sol`, `opus → gpt-5.6-terra`, `sonnet/haiku → gpt-5.6-luna`), so the argument is reusable for any future non-light override, not just `--light`. All five codex call sites now carry the override — `assemble_codex_{shared,variant}_agents` in `setup.sh` (via its `MODEL_OVERRIDE_ARGS` array), plus the empirical applier's shared and variant blocks and the theory_llm applier's single block (via each applier's own `MODEL_OVERRIDE_ARG`, populated from a positional arg, since they run as separate `bash` subprocesses that inherit no arrays). The three in the appliers are the ones that would otherwise have left `--ext empirical` / `--ext theory_llm` agents at full tier in an otherwise-light build.

**The override drops `model_reasoning_effort` too**, mirroring the Claude assembler dropping `effort`. The pinned levels (37 `high` / 17 `medium` / 1 `low` across the full 55-agent metadata inventory; 33 / 17 / 1 in the 51-agent finance build below, which excludes macro's own `empiricist` plus the three agents pruned unless their flag is set — `report-synthesizer` (`--mode report`), `mechanism-auditor` (`--mode empirical-first`), `faithful-drift-auditor` (`--faithful`)) are calibrated to each agent's *ideal* tier; carrying `high` onto a Luna worker keeps the token bill the flag exists to cut. `launch_agent.sh` already defaults to `medium` when the field is absent, so a light codex agent runs Luna/medium with no launcher change.

Verified by build diff: a no-`--light` finance build with both extensions is byte-identical to its pre-change baseline (the only diffs are the per-deploy random fingerprint and the version stamp, neither of which this change touches); the `--light` build changes nothing outside `.codex/agents/`, where all 51 agents now read `model = "gpt-5.6-luna"` with no effort line. `llm_cognition --light` (40 agents) and `finance --mode report --light` (18) collapse the same way.

Grok is unaffected by construction — its tier table is a single model (`grok-4.5`), so the override is already a no-op there. Untouched by design: the `codex-math` skill (pinned `gpt-5.6-sol` as a *tool*, not a subagent) and the Claude launch-time heal (which already re-decides against the `--light-model` recorded in `code/utils/model_heal/config.json`).

An existing light deployment refreshed with `update.sh` picks the fix up automatically — the flag is replayed from `.deploy_manifest.json`.

---

## [2.18.1] — 2026-08-01
**The Stage-0 domain scope becomes checkable without becoming closed (#218).** v2.18.0's `stage-0-discovery-exhausted` branch bounded itself on "which domains are already spent," but that set lived only in the free text of every prior `branch_manager_discovery_p*.md`, so a fresh `branch-manager` had to re-derive it by reading N growing reports — and two firings could describe the same domain in different words and each read the other as untried.

Fixed by moving the record to where the choice is made rather than where it is reviewed. Step 0a now appends every domain it scans to **`output/stage0/domain_log.md`** (`{domain} — fresh scan` / `{domain} — corrected re-scan: {correction}`), a run-scoped log the Stage 0 entry hook never clears — the deliberate contrast with its sibling `gap_log.md`, which is per-pass. Dedup is now an exact read of one log written by the scanning step itself.

**The issue asked for a closed `DOMAIN_LIST`; that part was declined on the merits.** A machine-readable per-variant enumeration would make the 2 × |domains| bound numeric, but it would also let the pipeline mistake "covered the enumeration" for "covered the field" and freeze each variant's domain space at whatever `setup.sh` happened to name — the failure the repo's *prefer no structured classes* principle exists to prevent. The scope stays prose and is now explicitly documented as **starting points, not an exhaustive list**; `branch-manager` may name an in-scope domain the scope does not list. The cost is stated in `LIMITATIONS.md` rather than hidden: with an open domain space, termination rests on branch-manager's judgment that nothing materially different remains, not on an enumeration running out. What the log removes is the *silent* half of the failure.

**No migration path, deliberately.** A backfill — reconstructing the log from pre-2.18.1 reports for a deployment `update.sh`-ed mid-Stage-0 — was written and then removed. Three consecutive review rounds each found a defect in it and none in the fix proper: it demanded correction wording those reports never persisted, it parsed a report section this same diff deletes from the template, and every trigger placement left an ordering hole that let a later Step 0a create the log with only the current domain and permanently satisfy the "does it exist" check. The population it serves is v2.18.0 deployments — released the same day — that are mid-Stage-0 in exhausted discovery when the refresh lands. The residual cost is one possibly-redundant re-scan in such a run, self-correcting from that point; the gap is recorded in `LIMITATIONS.md` rather than guarded.

**Net-negative on rules, as the fix should be.** Gone from `branch-manager.md`: the "Domains already spent" report section (the log is the record), the "your report is the durable record" rule, and "every prior `branch_manager_discovery_p*.md`" from the context's input list — which also stops that input growing without bound.

**`--variant macro` gained a real domain decomposition.** Its `DOMAIN_AREAS` was the bare string `"macroeconomics"`, so RESCAN-NEW-DOMAIN had nothing to name and the branch degenerated to one corrected re-scan then OPERATOR-ESCALATE. It now names monetary, fiscal/public debt, growth, labor search, international, heterogeneous-agent, expectations, macro-finance, and business-cycle measurement, with the same sufficient-not-necessary scope clause finance and llm_cognition carry.

**Two live mid-sentence `{{DOMAIN_AREAS}}` embeds fixed** — the same class v2.18.0's round-4 review caught in agent bodies, still present in `core_manual.md` (rendered a double period under `--manual` for finance and llm_cognition) and `core_report.md`. Both now point at the **Variant context** / **Submission domain** line instead of interpolating a paragraph mid-clause. Making macro's value a paragraph would otherwise have extended the bug to a third variant.

All seven configurations (`finance`/`macro`/`llm_cognition` defaults, `--mode empirical-first`, `--mode measurement-first`, `--mode report`, `--manual`) build clean with no placeholder leakage and no double periods.

---

## [2.18.0] — 2026-08-01
**The unrouted-state cluster — five issues that were one defect.** #156, #159, #160, #215, and #216 were filed separately over five weeks; tracing them found a single shape: **a lane exits or re-enters without executing the verification its output depends on.** Fixed as one pass, and four of the five closed by *subtraction* — the change set is net-negative on pipeline rules and touches no assembly logic.

**Two of the issues described the wrong fix, and the corrected scope is smaller.**
- **#216** asserted that the Stage 6 downgrade enrich-the-core lane (2a) was the only re-entry skipping Gate 4. It is not: the **Reject deepen** lane (`stage_6.md` Gate 5 Reject → branch-manager SUBSTANTIVE) returns to Stage 6 the same way, after the same `theory_version` increment and evidence re-fire. What made 2a look unique is that the *Major Revision* lane reaches Gate 4 only when it routes through the deepening playbook — which fires on structural concerns or a plateau, not on routine `[FIX]` cycles. So instead of re-verifying staleness at 2a's return point (patching one of two instances and duplicating Gate 4's logic at a second site), `stage_6.md` gained a single **evidence-currency entry precondition**: before *any* Stage 6 run, the mode's staleness pointers must equal `theory_version`. One site, every lane, including any added later.
- **#215** reported that theory-first llm_cognition figure markers go unscanned, and proposed a fourth scan arm plus an extension-keyed marker family. The root cause was upstream: **`paper-writer.md` contradicted itself** — its numerical-claims rule said to always write `[NEEDS THEORY-EXPLORER]` while its figure rule said to name the true producer. A fourth arm would have left that in place. The numerical-claims rules now name the producer by source directory, and the three near-duplicate scan arms in `stage_5.md` step 5 (`NO_MODE` / `MEASUREMENT_FIRST` / `EMPIRICAL_FIRST`) collapsed into **one generic rule** that scans every producer form, routes each to its stage's re-fire procedure and reviewer gate via a table, and returns a marker naming a non-existent producer to paper-writer to re-name. Net −2 arms, no new marker family. It also closed an unfiled sibling: under the modeless default with `--ext empirical`, the old `NO_MODE` arm scanned only for `[NEEDS THEORY-EXPLORER]`, so a legitimate `[NEEDS EMPIRICIST]` figure marker went unscanned there too.

**Stage 0 no longer abandons a project that has not run out of places to look (#156).** Exhausted discovery routed to "the orchestrator's standard abandonment/escalation path" — which never existed anywhere in the repo. Tracing the trigger showed the dead end was also *wrong*: `gate0_best_question_score == -1` is reachable only when every gap was logged `closed`/`no-stake` at Step 0c, i.e. gap-scout killed the whole scan **before `question-poser` ever ran** — evidence about the one domain Step 0a scanned, not about the field. So the terminus is now a routed decision: a new `branch-manager` context (`stage-0-discovery-exhausted`) recommends RESCAN-NEW-DOMAIN, RESCAN-CORRECTED, or OPERATOR-ESCALATE, the last setting `status = "halted_no_viable_question"`. The loop is bounded without a new counter — one fresh scan plus at most one corrected re-scan per domain, recorded in the reports themselves.

**Seeded abandons are now mechanically terminal (#160).** Six seed/faithful sites wrote `output/seed/abandon_report.md` with no `pipeline_state.json` status token, so a resumed session could not distinguish "halted, needs a human" from "paused mid-stage" and would re-enter the stage the abandon decision was meant to end. Rather than repeat a clause six times, one rule in `seed.md` and `faithful.md` binds `status = "halted_seed_abandon"` to the act of writing the report — future abandon sites inherit it. `session.md` gained a third halt class, **decision halts**, for the case where nothing is broken and no configuration is wrong: the pipeline judged the work not worth continuing.

**The scorer's Surprise guard no longer silently no-ops (#159).** Seed/faithful Gate-3 routed straight to Stage 4, so `output/stage3/implications.md` was absent and the scorer's SUPPORTED-cap / PUZZLE-CANDIDATE-floor rules — gated on that file existing — never fired, in exactly the modes where the idea is pinned and cannot be swapped. The file turned out to be consumed in three places (scorer, `paper-writer`'s Stage 5 input list, `puzzle-triager`), so the minimal fix would have meant adding three "if it exists" qualifiers. Instead the exception was closed: both Gate-3 overrides now run Stage 3 (Stage 2b stays skipped, and the limitation note narrowed to say so), seed/faithful back-fill entry at Stage 4+ carries a Stage-3 prerequisite, and the scorer's existence-conditional was **deleted** as dead.

**Five review rounds, four of which found a real defect.** Round 2 caught two fixes applied to `seed.md` and never mirrored into `faithful.md` — including a "terminal abandon" rule that omitted faithful's Gate 2 site (`faithful_overrides/` has no Gate-2 file, so faithful falls back to the shared seed one, which branches on `--faithful` internally) and would have reproduced the very bug it was written to prevent. Round 4 caught `{{DOMAIN_AREAS}}` embedded mid-sentence at 7 sites: harmless for macro's bare `"macroeconomics"` string, but finance and llm_cognition set it to a prose paragraph ending in its own period, so deployments rendered double periods and run-ons. Fixing it removed the need for the placeholder in an agent body at all — `branch-manager` already receives the domain via its injected Variant context section — which let the entire `setup.sh` vocab-plumbing change from earlier rounds be reverted. **`setup.sh` is untouched by this release.**

All ten configurations (`finance` default/`--seed`/`--faithful`/`--mode empirical-first`/`--ext theory_llm`/`--mode report`, `macro`, `llm_cognition` default/`--mode measurement-first`/`--mode report`) build clean with no placeholder or marker leakage. LIMITATIONS.md: the theory-first marker-scan entry is marked **closed** (noting the actual fix differed from the one it predicted), and one new limit is documented — the Stage-0 re-scan bound rests on `DOMAIN_AREAS` being prose rather than an enumerated list, so it degenerates for `--variant macro`, whose scope is a single opaque string.

---

## [2.17.1] — 2026-08-01
**#199 post-ship review — measurement-first coherence fixes.** An eight-round review loop (independent reviewers per round; each round reviewed the previous round's fixes) found and closed fourteen defects in the v2.17.0 measurement-first shipment. Most shared **one root cause: `THEORY_FIRST` blocks are kept under measurement-first** (the mode is theory-shaped), so every theory-first block silently assuming *Stage-2-time* audits or Stage 2b shipped into MF unchanged. Converted to `NO_MODE` with MF twins added:
- the escalation table's math-audit row told MF to **abandon the theory version** on a failed characterization — the exact inverse of `stage_2.md`'s rule that the measurements survive and the first escalation is a narrower claim class (a run would have discarded a completed, expensive Stage 3b experiment set because the post-hoc formalization failed to audit);
- `paper-writer`'s numerical-claims rule and `stage_5.md`'s marker scan both routed to `theory-explorer` + `output/stage2b/`, neither of which exists under MF — now `experiment-designer` + `output/stage3b/`;
- `idea-reviewer`'s ADVANCE handoff instructed theory-generator to prove theorems, which construct mode's own rules refuse.

Beyond that class: `puzzle-triager`'s **Theory-formality axis** was undefined under MF and systematically forced BACK-TO-IDEA — triage always fires before any characterization exists, so "audits incomplete" was literally true on every invocation, making PIVOT unreachable for exactly the Stage-3b contradictions the mode exists to surface (the axis now scores on the design gate). `experiment-reviewer`'s body and output template assumed a completed run while Gate 2 launches it at **plan time**; it now carries a `MEASUREMENT_FIRST` "Two invocations" section with its own inputs, output template, and ACCEPT semantics, and scores the plan's *commitments* rather than faulting it for artifacts it cannot yet have. `math-auditor`'s automatic-unverified rule accepted only an `output/stage2b/` citation, so under MF **every legitimately measured number** would have been listed as unverified, inverting what the `## Unverified claims` section means to the scorer — re-pointed to `output/stage3b/`. `stage2_design_version` added to the runtime doc's state JSON and field glossary; the design-gate cap corrected from "3 consecutive REVISEs" to its actual "3 consecutive non-ACCEPT verdicts" (the verdict set includes REDESIGN); the deferred-audit MF block now explicitly supersedes the contradiction-check NONE bullet it contradicts.

**The `stage3b_theory_version` re-set no longer rests on the orchestrator's reading of prose.** `theory-generator` emits a `NEW-TESTABLE-CONTENT:` line as a **mandatory output header** of every characterization, keyed on *load-bearing* in the math audit's sense (anything else depends on it) rather than on which paragraph the claim was filed under — so the conjecture paragraph is not an exemption. A characterization lacking the line is incomplete output, not a new version: it is re-fired at the same `theory_version` before being audited or committed, and because the audit-FAIL loop re-launches characterization mode on its own, that check lives at the audit itself and re-applies to every re-fire. A wrong call here ships a formal claim nothing measured past a clean-reporting H3.

**Resolver ordering fix.** Adding a second mode block at an existing site exposed a latent bug: the resolver interleaved block-removals and marker-strips by family, and the removal pattern's `\n{0,2}` would eat a blank line that a *neighbouring* block's strip had just exposed — silently gluing the empirical-first `idea-reviewer` ranked list onto its ADVANCE header. `setup.sh` now runs every removal before any strip, making output independent of family order so a new mode block cannot perturb other modes. New `test_scripts/test_marker_resolver_adjacency.sh` guards the invariant (verified non-vacuous against the old ordering).

21 new llm_cognition tripwires. `finance`/`macro`/`llm_cognition` default, `finance --mode empirical-first`, and `llm_cognition --mode report` all verified **byte-identical** to the pre-change baseline; `macro --mode report`, `llm_cognition --manual`, and MF × `--seed`/`--faithful`/`--light` verified to build clean. One pre-existing gap found and documented rather than fixed (out of scope, affects theory-first llm builds): Stage 5's marker scan has no `experiment-designer` arm there, so a correctly-named Stage-3b figure marker goes unscanned — see LIMITATIONS.md.

## [2.17.0] — 2026-07-31
**#199 — `--mode measurement-first` ships for llm_cognition.** Evidence-first pipeline shape for the modal ML cognition paper: Stage 1 sketches candidate constructs/task families (idea-generator + idea-prototyper overlays; the prototyper may run a toy-scale pilot); Stage 2 `theory-generator` runs in **construct mode** (construct definition + task family + scoring rule + measurement plan); Gate 2's binding half is a **plan-time design gate** (`experiment-reviewer` on the plan, `stage2_design_version` state field) and the **math-audit pair is deferred, not skipped** — after Stage 3b (the evidence core) completes, theory-generator re-enters in **characterization mode** to formalize what was measured and both audits fire there, with H3 gating on all three legs. Stage 2b skipped. New overlay assets: `templates/agents/llm_cognition_modes/measurement_first/vocab.json` (27 keys) + 5 body overlays under `shared_modes/measurement_first/` (including a construct-validity `referee-mechanism`). The mode-marker resolver rewritten generically over four families — `EMPIRICAL_FIRST`, `MEASUREMENT_FIRST`, `THEORY_FIRST` (any theory-shaped pipeline: default AND measurement-first), and new `NO_MODE` (strictly modeless; used where a mode block replaces the default content) — verified byte-identical across all 8 existing build configs. 17 new regression checks. The theory_llm applier's no-mode-overlay gap is documented in LIMITATIONS.md (the design-gate framing reaches experiment-reviewer via the launch instruction). Review round 1 caught and fixed three criticals before ship: the theory-first Stage 2b procedure leaking into MF builds (converted to `NO_MODE`), the characterization's `theory_version` bump tripping the Stage 3b staleness trigger + Gate 4 block (explicit `stage3b_theory_version` re-set rule with a new-testable-content exception), and puzzle-triage lacking MF routing + the load-bearing `stage2_design_version` PIVOT reset (MF mode note + inline reset added; the PIVOT/step-3 inline additions and the stage_2 step-2 parenthetical are small intended doc deltas in all variants). Also: the MF revisions bullet in stage_4 conditions the prior-audit read on file existence, and the Gate-2 seed override names the MF verdict/cap set.

## [2.16.0] — 2026-07-31
**#204 — llm_cognition `--mode report` ships.** The report-mode overlay bodies are parameterized on the byte-identical-default pattern: the report `referee-mechanism.md` reuses the base body's `MECH_*` keys (26 substitutions; zero econ residue), so the v2.9.0 ML overrides apply for free — with `MECH_EVAL_FRAME` re-anchored per variant in the `{variant}_modes/report` overlays (report mode names the math-auditor explicitly). `referee-core`/`referee-freeform` report twins gain `REFEREE_VERDICT_NOTE` (conference-cadence verdict translation now reaches report builds), `REFEREE_RESHAPE_DISCIPLINE`, and `REFEREE_TOP_OUTLET`; `MECH_PRIMITIVES_OUTPUT_GUIDANCE` also closes a previously-uncensused econ line in the *base* referee-mechanism ("preference / information / technology / market-structure choices" → construct/stimulus/scoring for ML). New `templates/agents/llm_cognition_modes/report/vocab.json` (ML venue role + report eval frame + a report-anchored `REFEREE_VERDICT_NOTE` — review caught that the base note routes through the editor agent and tier table, neither of which a report deployment has; the override re-anchors routing to the report-synthesizer); gate flipped in `setup.sh`; theory_llm auto-imply skipped under report mode (its agents get pruned there anyway); `core_report.md` triage example neutralized. The report `polish-identification` stays content-scoped by design. Finance/macro report builds byte-identical except the neutralized triage line. Tests: the llm regression test gains a 14-check report-mode section, and a new `test_scripts/test_report_mode_assembly.sh` guards the econ variants' report frames against silent overlay-vocab loss (the migration's one new degradation surface).

## [2.15.1] — 2026-07-31
**#206 — third tonal-extraction pass.** The residual econ worked examples in shared bodies are vocab-keyed with byte-identical econ defaults + ML overrides: `debugger` (context items, model-failure/data-query bullets, the V_S=V_U fix exemplar → an exact-match-scorer exemplar), `last-resort` (binding constraints, different-avenue exemplar), `style` (philosophy-opener "Economists have long debated…" → "Large language models have transformed NLP…", the power-utility "assume" exemplar), `triager` (DECORATIVE remedy + claim wording via `MECHANISM_QUALIFIER`, Berk-Green dedup exemplar, stakes row via `PP_STAKES_TERM`), and `paper-writer`/`polish-consistency` "economic content" → `{{MECHANISM_QUALIFIER}} content`. `sympy`/`codex-math` skill docs (no vocab pass) reworded domain-neutral. Second-round review caught two survivors in `paper-writer` (the results-section "Economic intuition" bullet and the throat-clearing rule's own "Economists have long…" snippet — both now keyed) and three finance-flavored defaults inappropriate for macro (PERMNO/GVKEY data-query identifiers, the Berk-Green dedup exemplar, the V_S=V_U fix exemplar — macro overrides added: FRED/SAAR identifiers, a Smets-Wouters exemplar, a HANK steady-state exemplar). Remaining labeled cross-variant examples documented as accepted in LIMITATIONS.md — #206 closed. Finance agent bodies verified byte-identical; 10 new llm regression tripwires.

## [2.15.0] — 2026-07-31
**#205 — per-variant skill gating + stale-infrastructure sweep.** `setup.sh` gains `variant_wants_skill` (llm_cognition excludes `ssj` + `nber-agenda`): the gate covers Claude/codex skill assembly, the `code/utils/{ssj,nber_agenda}` copies, the `sequence-jacobian` deps install, and the manual-mode skill catalogs, so an llm_cognition deployment no longer carries inert economics toolkits in its skills listing (finance/macro builds byte-identical; the manifest is presence-filtered so no emission change was needed). `update.sh` gains a generic **stale-infrastructure sweep**: paths recorded in the target's old manifest but absent from the fresh manifest are removed on refresh (dry-run aware, path-traversal guarded, `.env` never swept) — pre-gating llm_cognition deployments converge on their next update, and retiring any future manifested path needs no update.sh edit. `core_manual.md`'s helper list neutralized to per-variant wording; regression test extended (gated dirs absent, manifest clean, core skills kept).

## [2.14.0] — 2026-07-31
**#200 — llm_cognition paper skeleton + ML section list.** llm_cognition deployments now ship an ML-preprint skeleton (`templates/paper_skeleton/llm_cognition/{main,internet_appendix}.tex.template` — single-column 10pt, numeric `natbib`/`unsrtnat` citations, theorem environments, a post-references checklist `\input` slot; venue-neutral by design, the official venue style file remains a manual camera-ready swap, see LIMITATIONS.md). The skeleton lookup in `setup.sh` is variant-aware with root-template fallback, so future variants opt in per-file. New **generic variant markers** in the marker resolver (`<!-- VARIANT_{NAME}_START/END -->`, kept for the matching variant, removed wholesale otherwise — no resolver edit per new variant): used to add `related_work.tex`, `experiments.tex`, and `checklist.tex` to `docs/stage_5.md`'s section list and `paper-writer`'s per-section guidance for llm_cognition only (finance/macro builds verified byte-identical). Page budget vocab-keyed as `PW_LENGTH_RULE` (econ default byte-identical; ML override calibrated to the ~9–10-page single-column norm). Checklist substance grounds in `output/stage3b/experiment_results.md` scope/seed/provenance statements (re-verified by `polish-experiments` at Stage 9). Also: the v2.10.0 econ-leak tripwires in `test_scripts/test_llm_cognition_assembly.sh` silently never ran on stock macOS (bash 3.2 misparses the `declare -A` literal and dies with an `unbound variable` under `set -u`) — rewritten portably and extended with skeleton/section-list/marker-leakage checks.

## [2.13.2] — 2026-07-31
Hardening follow-ups to v2.13.1's two investigations (issues #212, #213).
**#213 — codex proxy-auth version floor:** codex-cli ≤0.144.x sends no `Proxy-Authorization` on HTTPS CONNECT tunnels, so behind an authenticated proxy every request — including the OAuth token refresh — fails transport-level with no HTTP status, masquerading as an auth problem (fixed upstream in 0.146.0, but a pin or rollback silently reintroduces it). New `code/utils/codex_preflight.sh` (deployed + manifested) warns — never blocks — when an old codex meets a credentialed proxy env; sourced at `launch.sh codex` startup, at every `launch_agent.sh` worker dispatch (codex can auto-update or roll back mid-run), and at every codex-math `codex_leaf_setup`, with the version lookup under a 10s watchdog so a hung binary can't block a launch. Full diagnosis + the header-injecting relay standby remedy recorded in LIMITATIONS.md.
**#212 — home-dir cache sweep:** audited the declared empirical deps for the `~/.edgar` pattern (a `$HOME` default cache outside the sandbox writable sets). No unfixed hits: `wrds` writes `.pgpass` only via an interactive path that env credentials bypass, `gdown`'s `~/.cache/gdown` is writable in every confining runtime, `openassetpricing` buffers downloads in memory, `fredapi`/`pandas-datareader`/`requests` keep no persistent cache. The audit record and a check-before-adding-a-dep guard now head `extensions/empirical/deps.txt`.

## [2.13.1] — 2026-07-31
Four deployment-correctness fixes: three from the 2026-07-31 EDGAR investigation (issues #209, #210, #211) plus a codex_math output-path defect found in the same day's sandboxed-codex investigation (no issue number; the companion upstream proxy-auth finding is tracked as #213).
**#211 — stale `.env` propagation:** `setup.sh`'s `.env` copy was an either/or (`cp` personal `.env`, *else* scaffold from `.env.example`), so a personal `.env` predating a key silently deployed without it — observed as fresh projects missing `SEC_EDGAR_*` entirely, with `edgar_utils.py` falling back to its placeholder identity. The copy is now a **union**: after copying `.env`, any key present in `.env.example` but absent from the copy is appended blank. The merge routine is extracted from `update.sh` into shared `scripts/merge_env_keys.sh` (build-time only) and sourced by both scripts, so the trailing-newline guards stay single-sourced instead of re-diverging (the v2.11.1 bug class).
**#210 — EDGAR cache outside the sandbox:** edgartools writes its local data store to `~/.edgar` by default, which is outside every runtime's writable set → `PermissionError` on first fetch. Rather than widening three per-runtime sandbox configs, `get_edgar()` now defaults `EDGAR_LOCAL_DATA_DIR` to `data/edgar_cache/` inside the project before the lazy `import edgar` (blank `.env` value counts as unset); the edgar skill's Setup snippet sets the same env var before `from edgar import *` for direct callers, with a new gotcha bullet; `data/edgar_cache/` is gitignored in deployments; `.env.example` documents the override, commented out.
**codex_math `/tmp` output path:** `codex_verify.sh` / `codex_write.sh` / `codex_explore.sh` wrote their `-o` result file to a hardcoded `/tmp/...`. On macOS `/tmp` is a symlink to `/private/tmp`, which sandbox write allowlists carrying the literal `/tmp` entry don't cover after resolution — so a verification that *succeeded* still exited 1 with "No output file produced", which `math-auditor` reads as a codex failure. Now `${TMPDIR:-/tmp}`, matching `codex_common.sh`'s existing scratch-dir pattern.
**#209 — undeclared empirical deps:** `linearmodels` (policy-canonical for Fama-MacBeth/panel — method-checker REVISEs hand-rolled substitutes, yet it was never installed) and `requests` (module-scope import in `edgar_utils.py`, previously present only transitively) added to `extensions/empirical/deps.txt`; the manual-install fallback hint in `apply_extension_empirical.sh` now derives its package list from `deps.txt` instead of a second hardcoded copy.

## [2.13.0] — 2026-07-31
`GENUINELY-STUCK` is no longer terminal: the abandon decision goes to the agent that owns it (issue #153).
**Problem:** `last-resort` — the strongest model in the pipeline — had two verdicts with asymmetric
verification. `FIX-PROPOSED` always re-entered the failing gate. `GENUINELY-STUCK` routed straight to
abandon/restructure with no second opinion and no re-check, so one false negative from a single call in
a single context could end an otherwise-recoverable run. The agent body already named the hazard
("a false GENUINELY-STUCK abandons salvageable work") and nothing downstream mitigated it.
**The fix is a deletion, not an addition.** The direct `GENUINELY-STUCK → abandon` edge is gone.
The verdict now re-enters `branch-manager` — the pipeline's existing "has this path ceilinged" advisor —
at a new context `last-resort-stuck`, which produces **Sections B + E only**, the same subset
`gate-5-downgrade` already emits. No new agent, no new verdict vocabulary, no new report format: §B's
existing REACHABLE/STRUCTURAL certification bar already asks the right question ("can you still name an
untried candidate?"). Both verdicts now obey one rule instead of two — neither self-executes — which
also let the asymmetry-justification paragraph in `last-resort.md` be cut.
**Two outcomes.** REACHABLE → branch-manager names the specific untried move *and the agent that owns
the artifact* (theory-generator, empiricist, paper-writer, the relevant auditor), and the move is
dispatched there — not back to `last-resort`. STRUCTURAL (certified) → restructure, or abandon **only
where the never-abandon rule permits**: post-Stage-5 a certified ceiling routes to restructure, deepen,
or ship-at-a-lower-tier, never to abandonment. The second opinion is genuinely decorrelated: different
agent, fresh context, and a lower model tier than the one that got stuck.
**Capped like every other loop.** New `loops.last_resort_stuck` (cap 2, seeded in `pipeline_state.json`).
It carries an explicit **reset override**, because this loop has a shape the generic rule mishandles:
attempting a named move *regenerates the stuck artifact*, so artifact-scoped auto-reset would zero the
counter every iteration and defeat the cap. It is scoped to the stuck **episode** and resets only when
the impasse clears or the loop exits by certification — recorded as a third documented exception
("retry-regenerates-the-artifact") in `core.md`'s auto-reset exception list.
**Impasse-agnostic bar.** `last-resort` is launched on tool and data failures too, not just theory
ceilings, so §B's journal-tier vocabulary gets two stated substitutions at this context: "core-change
candidate" → any untried candidate on the stuck artifact (a different estimator, specification, solver,
or data source), and "a contribution at the target tier" → "clears the impasse." A wedged solver has no
journal tier. The certification logic itself is unchanged.
**Also:** `--mode report` ships neither agent, so no mode divergence. Two stale enumerations removed
rather than corrected — branch-manager's "four contexts" (there were six) and the auto-reset list's
"two exceptions" — since a hard-coded count is what drifted in the first place.

## [2.12.0] — 2026-07-27
Deferrable core-bypass: a transient outage no longer parks a finished paper (issue #179).
**Problem:** any unresolved binding row blocked `status = "complete"` and forced terminal
`halted_core_bypass` awaiting manual operator sign-off. So an OpenAlex daily-budget outage —
transient, self-healing at 00:00 UTC, with a clean WebSearch fallback already in hand — could
strand a 100%-finished, submission-ready paper until a human marked a ledger row `resolved` by
hand. v2.11.0 made that outage far less likely and stopped it hanging; this closes the routing
half that made it terminal.
**Deferrable vs not.** An outage is *deferrable* when its source is down for a **stated bounded
horizon** (a rate limit or credit budget with a reset time) **and** the re-check is a **cheap
lookup**. Deferrable outages no longer halt: the run finishes, records what it owes in
`pipeline_state.json`'s new `pending_verification` array, and completes as
`status = "complete_pending_verification"`. Everything else — indefinite outage, withdrawn
record, credential failure, expensive re-check — still halts, as does **any ambiguous
classification** (the errors are asymmetric: a wrongly-deferred outage ships a status containing
the word "complete") and **every** case under `--halt-on-core-bypass`, which by design makes a
bypassed core a hard stop.
**The invariant is unchanged:** `complete_pending_verification` is not clean success. It is the
loud mark — a distinct status, an amber dashboard badge naming the outstanding cores, a driver
loop that stops and prints them, and an array saying exactly which citations went unchecked.
What was dropped is only the friction: a terminal state and a human signature for a lookup the
pipeline can simply redo.
**Self-clearing.** A session opening on `complete_pending_verification` re-probes, re-runs the
owed verification, and on a clean result resolves the ledger row, drops the entry, and sets
`complete`. Resolution authority was **narrowed, not loosened**: a session may self-clear only a
verification **it re-ran itself that came back clean** — evidence, not faith; a probe returning
200 or a fallback looking clean still cannot. A dirty re-check resets `current_stage` to the
owning stage and re-enters that stage's loop; a row may never be resolved while a known-bad
citation remains in the paper (that halts). Ledger and array must move together, and the ledger
wins if they disagree — the completion gate reads the ledger, so a corrupted array cannot force
a false `complete`.
**Consumers:** `launch.sh`'s driver `case` matched `complete)` exactly, so the new status would
have fallen through and re-prompted a finished paper until `MAX_TURNS` — it now exits cleanly and
prints the pending entries. `dashboard.html` would have rendered the badge unstyled and shown the
run as still working on "stage_10"; it now reads *Complete — verification still owed: <cores>*
(and all underscores in status badges are spaced, which also fixes `halted_core_bypass`).
**Not changed:** `core.md` stays lean per issue #27 — it gains only the `pending_verification`
schema. All three autonomous runtimes already shared `templates/runtime/claude/session.md`
(`setup.sh` sets `CODEX_SESSION="$CLAUDE_SESSION"`), so the rule reaches codex and gemini as it
always did.

## [2.11.1] — 2026-07-27
Credential documentation + a silent `.env` merge bug found while writing it.
**Bug:** `update.sh`'s env-merge read the source `.env` with `while IFS= read -r line`, which
sets the variable but returns non-zero on a final line with no trailing newline — so the loop
body skipped it and that key was **silently dropped**. The repo's own `.env` ended exactly that
way, with `OPENALEX_API_KEY` last, so the v2.11.0 key would not have propagated to any existing
deployment. Fixed with `|| [ -n "$line" ]`, plus a receiving-side guard that newline-terminates
the *target* before appending (a bare append onto an unterminated target concatenates two keys
into one corrupt line). `setup.sh` normalizes the trailing newline when copying.
**New `.env.example`** (committed; `.env` is gitignored, so a fresh clone had none and `setup.sh`
silently created no `.env` at all — contradicting the README). `setup.sh` now falls back to it,
so a deployment always lands a scaffold. Documents all 16 credential variables with empty values.
**README Step 3 rewritten**, and three of its claims were simply false: it said `NAME`/`EMAIL`/
`UNIVERSITY` appear "on the paper's title page" (nothing reads `NAME`/`UNIVERSITY`, and papers
ship an anonymized `\author` line that `paper-writer.md` forbids changing); it listed
`CENSUS_API_KEY` as optional (it is required — `bls_census_utils.py` raises without it, the
keyless tier having been retired); and it omitted `SEC_EDGAR_NAME`/`SEC_EDGAR_EMAIL` and the
`LOCAL_LLM_*` self-hosted backend entirely. `OPENALEX_API_KEY` is now documented as an
all-variants credential with the budget rationale, plus `update.sh` propagation instructions.
**Issues:** #150 (host-level OpenAlex rate limiter) closed — its per-IP premise is obsolete now
that the budget is measured per-key; the surviving shared-verdict-cache half is tracked in #207.

## [2.11.0] — 2026-07-26
OpenAlex credit-budget adaptation — the root cause of issue #179.
**Discovery:** OpenAlex replaced its per-second rate limit with a **daily credit/dollar
budget** on 2026-02-24 and now requires an API key past demo use; both utils still modeled
the old regime ("10 req/s, 100k/day") and authenticated with `mailto` only. Every deployment
was therefore running production literature work on the **keyless $0.10/day demo tier, shared
per-IP** — ~100 title searches/day for a whole host, which is why concurrent pipelines saw
sustained 429s and why single-ID lookups kept succeeding while searches failed.
**Measured costs** (from `x-ratelimit-*`): `/works/doi:{doi}` and `/works/W{id}` = **0
credits**; the `/works/https://doi.org/…` alias and `?filter=doi:` = 1; **title search = 10**;
PDF/XML = 100. Budget is **per key**, not per IP.
**Changes:** `OPENALEX_API_KEY` support in `openalex.py` and `bib_verify/openalex_check.py`
(Bearer header, so the key stays out of URLs, logs, and error text); `verify_bib.sh` now emits
each entry's `doi` (previously parsed and discarded, incl. a fallback that scrapes DOIs out of
`url`/`howpublished`/`eprint`), and `verify()` resolves by DOI first — **a bibliography whose
DOIs match their titles now verifies for 0 credits** (measured on a 4-entry .bib); an entry whose
DOI disagrees with its title still pays the usual 10 for a cross-check. Budget is now read off every response into `LAST_BUDGET` with a low-budget stderr
warning, the exhaustion error names the tier and whether a key was in use, and the bib report
prints credits spent. Skill docs (`openalex.md`, `bib-verify.md`) teach the cost model:
prefer `work` over `search` when a DOI or ID is in hand.
**Also fixes the #179 hang itself:** `openalex_check.py`'s `_backoff_sleep` slept the raw
`Retry-After`, uncapped. On budget exhaustion that value is seconds-until-midnight-UTC, so the
first entry slept for *hours* — the mechanism behind the reported "55+ min against 18 entries
with 0/18 processed, then killed." It is now capped at `BACKOFF_CAP` and a budget-exhaustion 429
raises `OpenAlexBudgetExhausted` immediately (scoped to 429; a 5xx with a long `Retry-After` is a
transient outage and still backs off normally). `openalex.py` already had both protections; this
brings the bib-verify path to parity. Consequence: budget exhaustion now surfaces as a per-entry
`api-error` with an explicit "resets 00:00 UTC" message and a finished report, instead of a hung
run with no report — which is what made the degradation unclassifiable in the first place.
**Verification integrity:** a cited DOI is trusted on its own only when it matches the cited
title at the VERIFIED bar (0.85). Below that the entry is labeled `lookup: "doi-weak"` and the
title search runs anyway, with the DOI candidate scored *alongside* the search hits (placed last,
so a stale-year DOI cannot displace a correct-year hit on a similarity tie). On that branch the
chosen match's title-similarity is therefore never worse than the pre-change search-only path. `bib-verifier.md`
and the generated report both now warn that `doi_confirmed: true` on a `doi-weak` entry means
"the DOI is a real record," not "it is the paper this entry claims" — and the label persists even
when the cross-check search itself fails, which is precisely when a silently-trusted weak DOI
would do the most damage. Each entry also reports the `credits` it actually cost, so a run that
hit failures doesn't overstate spend. DOI scraping is restricted to structural link fields
(`url`/`howpublished`/`eprint`, never the prose `note`, which routinely cites *other* papers'
DOIs) and no longer captures closing brackets.
**Not changed:** `.env` needs no scaffolding work — `setup.sh` copies it to new deployments and
`update.sh`'s env-merge appends the new key to existing ones. *(Corrected in 2.11.1: the merge
silently dropped an unterminated final line, which is exactly where `OPENALEX_API_KEY` sat, so
propagation to existing deployments did not actually work until that release.)*

## [2.10.0] — 2026-07-26
llm_cognition hardening pass (second extraction wave + calibration + experiment rigor).
**Vocab:** ~45 new keys close every load-bearing econ leak the v2.9.0 pass missed —
math-auditor-freeform's full heuristic set (a binding Gate 2 gate), polish-prose items 8–10,
idea-prototyper primitives, implications-deriver, novelty-checker search targets,
literature-scout/theory-explorer/scorer-freeform role lines, scorer cap-30 archetypes,
editor domain guard, paper-writer exemplars, referee/branch-manager load-test predicate
(now the existing `POLICY_MAP_LOAD_TEST`), core.md CARA/CRRA + numerical-verification
bullets, stage_4 "economic content", stage_6's hardcoded `top-3-fin` (also fixes a macro
tier-name bug), stage_puzzle_triage "falls out of economics". Econ defaults byte-identical
(verified by full 8-config baseline diff). **Calibration:** llm_cognition tier table rebuilt
(JMLR/ACL/EMNLP/NMI moved to a lateral `top-ml` row, nature = Nature/Science only,
`top-ml` 75+ re-anchored to confident-accept caliber, TMLR rigor-weighting note); OpenReview
visibility claims corrected (ICLR-only public submissions); baseline-comparison referee
bullet; RIGOR_80 measurement-first anchor; conference verdict-semantics note in the referee.
**theory_llm rigor:** contamination-resistant procedural ground truth + memorization probe,
50+/condition headline floor with stimulus×run error bars, temperature>0 for headline
variance, model-snapshot/decoding/access-date provenance (llm_client already returns it),
the previously-dangling `[ROLE: LOAD-BEARING|STRENGTHENING-PROBE]` schema (unblocks
puzzle-triager's PROBE-NULL path), experiment-designer's canonical output renamed to
`experiment_results.md` (the name every consumer already reads). **New agent:**
`polish-experiments` (theory_llm, Stage 9) re-verifies the rendered paper's experimental
evidence — raw-results agreement, contamination status, pinning, statistical integrity,
artifact reproducibility; wired into stage_9 via a guarded doc amendment, core-bypass
inject, and report-mode prune. **Structural:** `--variant llm_cognition` auto-implies
`--ext theory_llm`; openalex script + skill gain ML venue aliases (verified against live
OpenAlex) with an honest conference-coverage caveat; bib-verify adds openreview.net;
update.sh learns to sniff/name llm_cognition; empirical-first rejection message is
variant-aware; extension-doc sed extended to the full placeholder set (D10); dashboard
subtitle variant-corrected; README variant table updated; regression test
`test_scripts/test_llm_cognition_assembly.sh` (gates, auto-imply, 12 leak tripwires).
**LIMITATIONS:** new entries for the theory-first ordering inversion (no measurement-first
mode yet), the ML paper section-list gap, and the pre-existing Grok extension-agent gap.

## [2.9.0] — 2026-07-26
Variant vocab now layers into shared-body assembly (shared → variant → tier → mode, later
wins; extension appliers included), making shared evaluator/search/polish bodies
variant-aware. Closes the llm_cognition routing-level economics leaks: referee-mechanism's
evaluative frame and verdict definitions, the `policy_map_axes`/`acronym_carveout`/
`iar_wiki_pointer` fragments, novelty/gap/literature search-venue directives
(SSRN/NBER → arXiv/OpenReview for llm_cognition), the deepening-playbook extension menu
and DECORATIVE remedy text (`MECHANISM_QUALIFIER*` substitution in core.md + stage docs),
polish-equilibria's N/A escape (now unconditional), the theory_llm experiment-designer's
stale finance_llm test list (+ explicit model-family scope rule), and the ssj/nber-agenda
advice bullets. llm_cognition vocab quality pass: H2/THEORY_AGENTS formal-only escape
branch, H3 measurement-first wording, landmark-anchor recalibration (Nature Human
Behaviour and PNAS dropped, JMLR reconciled), exemplar diversification, WRDS/FRED
inventory fix. All-variant fix:
"knowledgeable knowledgeable" doubling; stale finance tier-band examples removed from
core.md/stage_1.md. Finance/macro assembled output verified byte-identical except those
intended fixes. New LIMITATIONS entries: econ paper skeleton, econ-only skills install.

## [2.8.1] — 2026-07-26
`setup.sh`'s tier-vocab temp file no longer bricks every future deploy on a host.

- **BSD/macOS `mktemp` randomizes only a *trailing* run of `X`s.** `tier_vocab.XXXXXX.json`
  (2.7.0) therefore produced that path **literally** — a fixed name, which defeats `mktemp`.
  Sequential deploys still worked because the cleanup removes it, so this passed unnoticed.
- **The failure mode was latent and disproportionate.** Any run that died between creating the
  file and the cleanup left it behind; from then on *every* deploy on that host aborted at that
  line under `set -e` with a bare `mkstemp failed ... File exists` naming neither `setup.sh` nor
  the tier vocab. Concurrent deploys collided identically. Reproduced, then verified fixed: with
  a stale file present the deploy now succeeds.
- The `.json` extension was decorative — the path reaches the assemblers explicitly via `--vocab`.

## [2.8.0] — 2026-07-26
Figures are readable by the agent that has to caption them, and poppler is a declared dependency.

- **The trigger.** `paper-writer` has no Bash (deliberately — the claim-grounding stack requires
  every number in the paper to trace to a *producing agent's* output, and a shell would let the
  writer compute its own). In a field run it could not open either of two figure `.pdf`s because
  `pdftoppm` was absent. Granting Bash was the wrong lever twice over: it weakens the grounding
  invariant, and with no poppler on the host it would not have fixed anything.
- **Figures now ship as a `.pdf`+`.png` pair.** New `templates/fragments/figure_dual_format.md`,
  included by all four producers (`empiricist` finance/macro, `theory-explorer`,
  `experiment-designer`). The vector `.pdf` is what the paper `\includegraphics`es; the raster
  `.png` is what `paper-writer` reads to pick the headline figure and caption what is actually
  plotted. Producers that emit PDF-only (pgfplots/TikZ, R/Stata) rasterize with `pdftoppm`.
- **A build gate that could silently invert is now fail-closed.** Stage 5 build-verify check 5
  ran `pdftotext main.pdf - | grep -c PLACEHOLDER` and required `0`. With `pdftotext` missing the
  pipe is empty and `grep -c` prints exactly that `0` — so a paper whose title page read
  `TITLE PLACEHOLDER` passed. It now probes for the binary first and treats absence as a failure.
- **`poppler-utils` is declared** in `requirements.system` with its four consumers, and `update.sh`
  warns when it is absent — `requirements.system` is build-time-only, so a refreshed deployment
  otherwise had no signal that the host needed it.
- **Report mode halts instead of fabricating.** `--mode report` on a PDF-only submission now
  verifies poppler before fanning out; an agent handed an unreadable file does not reliably report
  that it read nothing, it produces a plausible audit of a paper it never saw.
- Also: `output/stage{3a,3b}/figures/` are created at deploy (with matching report-mode cleanup —
  a bare `rmdir` on a now-non-empty parent was leaving stray `output/stage*/` trees in report
  deployments, contradicting `core_report.md`); `polish-consistency` counts a `.pdf`/`.png` pair as
  one figure; `stage_5.md` carves the figure-rasterization marker out of the versioned claim-refire
  procedure it would otherwise be misrouted through.

## [2.7.0] — 2026-07-25
New `llm_cognition` variant: papers on the science of LLM cognition & evaluation (formal
frameworks + benchmark designs; NeurIPS/ICML/ICLR target, tier ladder
`nature → top-ml → field → workshop`; pairs with `--ext theory_llm`). Economics wording
previously hardcoded in the variant-agent bodies and the editor's tier ladder is now
vocab-parameterized (finance/macro output byte-identical); `referee-mechanism` now
receives the variant-context block. `--ext empirical` and `--mode report` are gated off
for the new variant (see LIMITATIONS.md "llm_cognition variant" entry).

## [2.6.7] — 2026-07-25
Cut 2.6.6 down to the two clauses that were doing the work.

- **2.6.6 was a rule stack, not a metric swap.** `stage_2.md`'s Gate-2 loop went from 2 clauses to
  7, the seed override gained 3 more, and a `LIMITATIONS.md` entry existed only to record that one
  of the new rules was unenforceable. That accretion pattern is the thing issue #193 is *about* —
  each audit round found a hole and it got patched with more prose.
- **The class-recurrence metric is gone.** It was a judgment with no artifact behind it (no auditor
  emits a class label), it needed the hard cap as a backstop anyway, and the hard cap alone would
  have stopped the incident that motivated it — that run went ~10 versions; a cap of 3 stops it at
  3. Its only marginal benefit was firing one version earlier, which is not worth a rule.
- **What survives is what was load-bearing.** Two clauses per gate: (1) a judgment-free hard cap —
  3 consecutive math-audit failures (theory-first), 3 consecutive REVISEs (empirical-first
  mechanism), 5 audit-fix attempts (Stage 3a) — at which patching the current artifact again is not
  an option; (2) when a fix *narrows* a claim, narrow every claim of the same shape, not just the
  flagged instance. Clause (2) is the actual lesson from the field incident (one version narrowed
  the `T` axis, left `h` universal, blew up four versions later) and it needs no recurrence
  detection — it applies to any narrowing, first time or fifth.
- **Removed as scaffolding for the deleted metric:** reactive-retirement verification, the
  fires-earlier/never-defers reconciliation, the seeded core/auxiliary cut restriction and its
  never-fire-early guard (the base path no longer carries a narrowing instruction that needs
  gating; the ship-honest check's own referent test was always the right home), the verdict-keyed
  counter clause, the "or earlier, as soon as a class survives" qualifiers on three `core.md`
  escalation rows, and the `LIMITATIONS.md` entry.
- Net vs. 2.6.5: the count metric is **deleted** and replaced by a hard cap — fewer moving parts
  than before 2.6.6, not more. The `core.md` row alignment that closed #157, the new Gate-2
  mechanism REVISE row, and the Stage 3a fix all stand.

## [2.6.6] — 2026-07-25
Gate 2's revision loop now measures progress by **error classes retired**, not by the error
count falling (issue #193).
- **The count metric was the bug.** `docs/stage_2.md` told the orchestrator to keep iterating
  while the error count decreased and to escalate only on a plateau. A run can patch one
  instance of the same defect per version, watch the total tick down, and never register that
  it is hitting an identical class repeatedly. Observed in `ai-trading-breadth` (`--faithful`):
  ~10 theory versions burned on one recurring class — a universally-quantified claim inferred
  from a computation whose quantifier range was strictly narrower — while the mathematical core
  sat frozen and certified across seven consecutive diffs. Every defect was in the
  attribution/presentation layer.
- **New rule, same length: retire the class.** A class still flagged after a fix aimed at it
  means patching is not working. The response is to prove the general version or cut the claims
  it attaches to back to what was actually verified — **across every claim of that shape, not
  just the flagged instance**. Instance-scoped narrowing is precisely why the class recurred:
  one version narrowed the `T` axis and left the `h` axis universal, and it blew up four
  versions later on the paper's own census grid. Attempt-increment / `theory_version` reset is
  now the *last resort*, reached only if the class survives being retired.
- **No new mechanism, by design.** The run's own conclusion was that "a fourth ledger would fail
  the same way" — new verification machinery is new claim surface carrying the same defect. So
  this ships as a metric swap against machinery that already exists: `math-auditor` is already
  instructed to skim prior `math_audit_v*.md` for recurring error classes, `core.md`'s
  "frame honestly — never inflate" principle already licenses narrowing when the substance holds
  and only the label was inaccurate, and the seeded ship-honest check already knew how to cut an
  overclaim. Nothing was added to `pipeline_state.json` and no agent was created.
- **Empirical-first transplant made explicit rather than assumed.** `mechanism-auditor` returns
  seven fixed dimension labels, not a multiplicity of same-shaped claims, so a dimension label is
  only a coarse proxy for an error class. The empirical-first text now names both failure
  directions: the same dimension failing twice for unrelated reasons is not recurrence, and a
  defect resurfacing under a *different* dimension label after a cosmetic dodge is.
- **Seeded/faithful convergence.** `SEED_OVERRIDE_STAGE_2_GATE_2.md` superseded the base
  escalation wholesale, which under `--faithful` (where the seed pins the contribution, so
  neither attempt-increment nor sketch-swap is available) left "add another ledger" as the only
  move the docs did not forbid. It now supersedes only the base path's *last resort*; the
  retire-the-class first move is shared, and the ship-honest check gained the same
  every-claim-of-that-shape scoping. No `--faithful` branch was needed.
- **New judgment-free floors, because neither metric was self-bounding.** Class-recurrence is a
  judgment, so it is layered on top of mechanical bounds rather than replacing them — but auditing
  the change surfaced that the *old* metric had no real floor either: an error-count plateau never
  fires against a run that patches one instance per version, which is exactly how the field
  incident reached ~10 versions. Gate 2 therefore gains hard caps it never had: **3 consecutive
  math-audit failures** (theory-first) and **3 consecutive REVISEs** (empirical-first mechanism).
  At the cap, patching the current artifact again is not an option — escalate by incrementing
  `theory_attempt` or by swapping sketches. The pre-Stage-5 sketch-swap bullet is amended so
  "continue restructuring the current sketch" means continuing it under a *fresh attempt*, closing
  the loophole where a mandatory-evaluation step could be satisfied while patching forever.
- **The class trigger only ever fires *earlier*; it never defers a floor.** The seeded ship-honest
  counter is explicitly re-stated as keyed to consecutive Gate-2 *verdicts*, not to class
  judgments, so it cannot be deferred by calling every recurrence a new class. Retirement is
  verified reactively — if the next audit re-finds the class, it was not retired.
- **Seeded/faithful routing at the cap.** Both escapes the base path offers at the hard cap
  (increment `theory_attempt`, swap sketches) are forbidden under `--seed`/`--faithful`, so the
  override now states explicitly that the cap still *binds* there and routes into the ship-honest
  check — which fires at the identical 3-consecutive-failure threshold. Without this, a seeded run
  at the cap was told to take an action the override forbids, with no stated alternative.
- **Seeded/faithful safety restriction.** Retire-the-class may only cut claims that are
  `auxiliary` under the override's existing core/auxiliary referent test. A recurring class that
  attaches to a seed-pinned *core* claim must be proved, never cut — without this, the base-path
  retire instruction could have narrowed a pinned core claim before the referent check was ever
  reached. The restriction is explicitly barred from firing the ship-honest check *early*: a
  core-attached class is decided at the 3-failure cap like any other, so it cannot short-circuit a
  seeded run into `abandon_report.md` on a second recurrence.
- **Same fix applied to the Stage 3a empirics-auditor loop** (`--ext empirical`), which carried the
  identical count-based anti-pattern; its hard cap of 5 is retained as the mechanical floor.
- `core.md`'s escalation table gains a **Gate 2 mechanism REVISE** row (the empirical-first gate
  had none at all) and its **Empirics audit fails** row now states the earlier class trigger
  alongside the 5-attempt cap, matching how the math-audit row reads.
- `core.md`'s "Math audit fails" escalation row now reads "3 consecutive audit failures on the
  same theory (hard cap) — or earlier, as soon as an error class survives being retired." This
  closes #157 on both axes: the two docs previously stated different *thresholds* for the same
  event (2 vs 3), and `core.md`'s action ("Abandon this theory version") was stronger than what
  `stage_2.md` actually required (a mandatory *evaluation*, which permitted continuing). The
  Gate-2 hard cap makes the stronger action mandatory, so the row and the SOP now agree.
- **Documented, not silently accepted:** the auditors emit no class-shaped field, so recurrence is
  a prose judgment and "retire across every claim of that shape" has no demonstrated-sweep
  requirement. Both are recorded in `LIMITATIONS.md` with the reason they were not closed by
  adding a ledger (the mechanism #193 documents failing three times) and what would close them (a
  structured `class` field on audit findings — a change to what the auditor *emits*, not a new
  verification pass).

## [2.6.5] — 2026-07-23
Split dev settings from deployed settings, and fixed a silent corruption of the deployed
runtime docs in every `--ext empirical` build.
- **Runtime settings now ship from `templates/`, not from this repo's root.** `.claude/settings.json`
  and `.gemini/settings.json` at the repo root were dual-role: they configured the
  template-development session *and* were the artifact deployed into every research project
  (via the clone in production, via an explicit `cp` under `--local`). The two roles want
  opposite postures — the template repo deploys into arbitrary paths and needs write access
  there, a research project wants the sandbox on. Deployed settings moved to
  `templates/runtime/{claude,gemini}/settings.json`, installed by a new
  `install_runtime_settings` block that serves both branches and overwrites what the clone
  carried in. The repo root keeps its own `.claude/settings.json` for dev work only. Deployed
  paths and their manifest entries are unchanged, so `update.sh` still refreshes them.
- **Fixed: the grok `scorer` agent body was being spliced into deployed CLAUDE.md / AGENTS.md /
  GEMINI.md.** The empirical extension's placeholder-fill step hand-indexes its argv; when
  `.grok/agents/scorer.md` was added as the fourth scorer call site, the slice end and the
  following index were not re-counted. `scorer_files` silently dropped grok (so grok's scorer
  never got the fertility addendum) and `state_loop` read the grok scorer file instead of
  `state_loop_fields_inject.md` — splicing ~300 lines of agent prompt into the `loops` object
  of the pipeline-state spec in all three runtime docs, and dropping the empirical audit-loop
  counters entirely. Affected every `--ext empirical` deployment, theory-first included.
- **Fixed: `--mode report --ext empirical` aborted setup.** Same off-by-one: report mode prunes
  `scorer`, so the misread `open(sys.argv[14])` hit a nonexistent path and killed the run at the
  extension step. The correctly-indexed inject file always exists, so the composition now builds.

## [2.6.4] — 2026-07-21
Report-mode audit: the fan-out reused pipeline-native agent definitions that referenced
artifacts which do not exist in a report deployment. Four fixes, one new assembly layer.
- **`polish-identification` was dead-on-arrival in report mode** — its body auto-N/As when
  the pipeline design artifacts are absent, which they always are in report mode, so every
  report run silently skipped identification auditing. New report-native body overlay
  (`shared_modes/report/polish-identification.md`) audits the submission's *own stated
  design*: estimand-vs-claim, 2026-standard diagnostics, cluster-vs-variation level,
  internal coherence of the identification narrative. Scope decided by the submission's
  content, never by deployment flags
- **Report-mode context inject** (`templates/shared/report_mode_inject.md`) appended to the
  12 pipeline-native audit agents in the fan-out: prompt-passed `submission/` + `audits/`
  paths win over the bodies' pipeline paths, missing pipeline artifacts are skipped not
  fished for, PDF-only submissions get an explicit degraded-check note exactly where the
  missing source weakens the audit's tooling (and no note where it doesn't), helper
  scripts with hardcoded `output/` paths are scratch to be copied into `audits/`,
  `submission/` is read-only
- **Mode metadata overrides** — new `"modes": {"<slug>": {...}}` key in agent metadata,
  merged by all four assemblers (new `--mode` arg, `apply_mode_overrides` in the loader)
  so a mode can re-aim an agent's orchestrator-facing `description`; 16 report-mode
  descriptions added. Zero-behavior-change verified: default and empirical-first builds
  byte-identical to a HEAD baseline
- **Synthesizer coverage halt now has a defined expected set** — Step-1 triage writes a
  `planned_audits:` block into `process_log/audit_log.md`; the synthesizer halts against
  that list (it cannot see the orchestrator's fan-out table, notably under codex where
  workers deliberately do not read AGENTS.md)
- PDF-only degradation list extended from 2 to 6 audits (`math-auditor`,
  `math-auditor-freeform`, `bib-verifier`, `polish-bibliography` join `polish-formula`,
  `polish-numerics`), with the 10 full-strength audits named as explicitly un-noted;
  synthesizer no longer told to expect extension audit files that v1's install-only
  composition never produces

## [2.6.3] — 2026-07-20
Resumed Claude sessions were starting unguarded. The hourly `/loop` stall guard and
`start_services.sh` were both tied to the fresh-start path, so a session relaunched with
"continue" (`status: "running"`) got neither — no stall detection for the rest of the run,
and dead data connections whose liveness `data_inventory.md` still asserted.
- **Session preflight** (`templates/runtime/claude/session.md`) — start services, establish the hourly loop, write-or-re-verify the data inventory. Runs on every session, fresh or resumed
- Invoked from the `not_started` and `running` branches **only**: a `complete` or `halted_*` session reports and stops, and on `halted_wrds_unreachable` restarting the service is the operator-driven repair that branch forbids
- The loop is documented as session-lifetime, not Stage 0 — it lives in the Claude Code session and dies with it, so every relaunch re-establishes it; when in doubt, set it up (a duplicate stall check is harmless, a missing one is not)
- Re-verify passes correct stale ✓ rows and commit only if a row changed, rather than rewriting the inventory's research-design implications
- Claude-only: `/loop` is a Claude Code skill and the other runtimes have no session-start block

## [2.6.2] — 2026-07-20
CLAUDE.md slimmed to the always-on layer; repo-editing reference moved to a skill. Nine audit
rounds found the moved content was substantively stale, so this is a correctness pass as much
as a docs move.
- `edit-pipeline` skill — repo layout, setup.sh assembly, agent classification, model pinning/fallback, and the add-a-variant / add-a-mode procedures. CLAUDE.md 284 → 87 lines (369 at session start)
- **Corrected: "Adding a new variant"** named a per-variant metadata file `setup.sh` never reads and a body dir nothing loads (stale since the `784b01f` consolidation) — following it produced a broken variant. Variant agents are one `claude_variant_agents.json` + `{id}-core.md` bodies in `agent_bodies/shared/`, specialized by `vocab.json`
- **Corrected: vocab trip-wire** sent shared-body `{{KEY}}` defaults to the variant vocabs; shared bodies resolve against `templates/agent_bodies/shared/vocab.json`
- **Corrected: agent rosters** — 16 of 31 shared agents were undocumented (all 8 `polish-*`, `bib-verifier`, `editor`, `report-synthesizer`, `referee-mechanism`, `triager`, `puzzle-triager`, `faithful-drift-auditor`, `debugger`); `question-poser`/`question-referee` were in neither list; `headline-replicator`/`method-checker` missing from the empirical roster
- **Corrected: Grok** was absent entirely — architecture said "three runtimes"; it is a fourth assembly call site
- **Corrected: fable generative spine** was printed backwards (`question-poser` is Stage 0, `idea-generator` is Stage 1)
- **Corrected:** 4 of 6 unconditionally-installed core skills missing from the table; `extensions/empirical/skills/` path never existed; all literal `setup.sh:NNN` pointers had drifted (one by ~2200 lines) and are now grep anchors
- Enumerations that can rot are replaced by the mechanism that generates them (`scripts/list_agents_by_category.py`, grep the `prune_report_mode_agents` call sites)
- Documented gap: no written "Adding a new extension" procedure, with its failure mode

## [2.6.1] — 2026-07-19
Meta-repo dev tooling: CLAUDE.md slimmed by moving deployment docs into a skill.
- `deploy-project` skill (`.claude/skills/deploy-project/`) — all `setup.sh` flags, compositions, mutual exclusions, post-setup launch guidance, WRDS server startup. Loaded on demand instead of sitting in every session's context; CLAUDE.md 369 → 284 lines
- `.claude/skills/` is now tracked in the meta-repo; `setup.sh` snapshots the cloned dev skills after clone and strips them in the cleanup block, so they never ship into deployed projects (build-time only — no deployment-manifest entry)
- Strip is checksum-guarded: if a future `skill_id` ever collides with a dev-skill directory name, the assembled project skill is kept and a rename warning is emitted, rather than being silently deleted

## [2.6.0] — 2026-07
Production-hardened, four-runtime era. Introduces formal semantic versioning (`VERSION` file
+ `setup.sh` version stamp + this changelog).
- **Grok** runtime added — fourth runtime alongside Claude, Codex, Gemini (`cf0f112`)
- `pipeline_state.json` schema overhaul: ~17 bespoke loop counters → one generic `loops:{}` object (`7783945`) — breaking for in-flight deployments (handled by `update.sh`)
- Launch-time model heal: bidirectional tier correction at every `launch.sh claude` (`b592724`)
- Shared rule-fragment system (`templates/fragments/`, `{{> id}}` includes) (`0982043`)
- Codex retier to `gpt-5.6-{sol,terra,luna}` + isolated `codex exec` launcher replacing broken `spawn_agent` (`0d1245c`)
- macOS portability (bash 3.2 / BSD awk) + per-project `.venv/` (`6f9cdbf`)

## [2.5.0] — 2026-06-13 — `126f79e`
Resilience infrastructure.
- Subagent model-availability probe + assembly-time fallback chains (`126f79e`), prompted by the fable/mythos export-control suspension (2026-06-12)
- `--halt-on-core-bypass` guard + degradation ledger (`52a6a27`)

## [2.4.0] — 2026-05-25 — `90d501c`
`--mode report`: referee an external submission instead of generating one (one-shot, no stages).

## [2.3.0] — 2026-05-06 — `e4a133f`
`--faithful` mode: stricter `--seed` that implements the seed as a frozen contract.

## [2.2.0] — 2026-05-03 — `97ae4c5`
`--mode empirical-first`: identification-first pipeline for causal-estimate papers.

## [2.1.0] — 2026-04-25 — `7855435`
`--manual` mode (research toolkit) plus the April evaluation-topology work: editor Gate 5 aggregation, freeform scorer/referee, puzzle-pivot gate, Stage 9 polish layer.

## [2.0.0] — 2026-04-05 — `e01693b`
**Multi-runtime.** Runtime-agnostic core + per-runtime packaging; **Codex** and **Gemini** runtimes join Claude. The shift from Claude-only to three runtimes.

## [1.3.0] — 2026-03-23 — `ff49622`
Composable extensions: `theory_llm` becomes a proper `--ext` (was a variant).

## [1.2.0] — 2026-03-20 — `00df890`
Empirical extension: data skills (FRED, Ken French, WRDS, …) + calibrator/empiricist agents.

## [1.1.0] — 2026-03-19 — `00ab22b`
Multi-variant infrastructure: `templates/` split, `macro` variant, per-`--variant` assembly.

## [1.0.0] — 2026-03-17 — `1b65f05`
**Autonomous pipeline born.** `setup.sh`, orchestrator with stages/gates, `pipeline_state.json`, dashboard, and the core pipeline agents. The shift from manual toolkit to autonomous pipeline.

## [0.1.0] — 2026-02-28 — `849f7db`
Initial manual research toolkit: 3 agents (scribe, referee, style), flat `CLAUDE.md`, no pipeline.
