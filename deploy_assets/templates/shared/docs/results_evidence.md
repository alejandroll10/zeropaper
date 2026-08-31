# Computed results, exhibits, and evidence audit

This contract applies to every paper-producing mode. It binds two separate independent checks at one paper boundary: computed evidence is audited by `evidence-auditor`, while factual characterizations of cited work are audited by `polish-bibliography` in checkpoint mode. Formal theory notation remains outside both; citation-key identity retains `bib-verifier`.

## Producer contract

<!-- MANUAL_START -->
Manual mode has no Stage 2b/3a/3b namespace and no `pipeline_state.json` pointers. The caller supplies every plan, bundle, receipt, report, code, input-snapshot, and exhibit path. In the lifecycle instructions below, “the stage's reviewer” means the caller-designated substantive reviewer, and registry activation is the durable handoff: report the accepted active receipt and report path to the caller, then retire any explicitly superseded predecessor. Never create or update a stage report/receipt pointer. Canonical stage paths shown below are autonomous examples only, not manual defaults.
<!-- MANUAL_END -->

Every active evidence producer writes one pre-run plan, one schema-v1 canonical bundle, and one receipt. The plan is the matching bundle stem plus `.plan.json` unless the launch supplies another exact versioned path. The published JSON Schemas are structural preflight aids; `results_pipeline.py` is the canonical validator for normalized paths, cross-references, plan/bundle equality, duplicate ownership, freshness, and lifecycle state.

| Producer | Bundle | Receipt |
|---|---|---|
| theory-explorer | `output/stage2b/results.json` initially; fresh `<exploration-stem>_aK_results.json` on re-fire | matching `*.receipt.json` sibling |
| empiricist | `empirical_feasibility_results.json` / `empirical_analysis_results.json` initially; fresh `<analysis-stem>_aK_results.json` on re-fire | matching `*results.receipt.json` sibling |
| experiment-designer | `experiment_results.json` initially; fresh `experiment_results_vN_aK_results.json` on re-fire | matching `*results.receipt.json` sibling |

### Empirical specification lineage

Quick-feasibility, full Stage 3a, data-first analysis, manual empirical work, and empirical repair runs use `run-empirical`; theory, LLM experiments, and offline dataset-release packaging continue to use ordinary `run`. Empirical records live at fresh versioned paths under `output/analysis_specs/`: one deliberately small reusable project baseline and one contract per evidence module. The contract's open input/sample/variable/procedure/inference/output envelopes carry stable IDs, ordered sample steps, DAG references, fixed settings or predeclared adaptive decision rules, result ownership, and exact reasons for deviations from reusable baseline definitions. Modified baseline definitions receive new `variant_of` IDs; baseline IDs never change in place.

The empirical run plan's `analyses` map binds each analysis ID to its contract, audit-only execution summary, and actual producer-input paths by input ID. Those bindings plus contract/baseline paths exactly cover all producer inputs. All analyses in one receipt share a baseline. The producer records observed periods, key uniqueness, step input/output flows, fingerprints, unit-bearing step/procedure counts, and procedure realizations in the execution summary; it does not pretend one global N describes a multi-stage or multi-sample analysis. Each bundle result has one analysis owner, and each exhibit's stable `elements` map has a duplicate-free union equal to its compatibility `result_ids`. Comparisons are ordinary producer-computed results with receipt-qualified operands, never renderer calculations. Historical operands remain eligible only through an accepted replacement chain ending in active evidence; verification follows their full nested operand closure, and retirement cannot strand an active dependent.

Set `renderer_inputs` in the plan and matching `renderer.inputs` in the bundle to the smallest presentation-safe subset of individual regular-file artifacts. Do not select directories or files containing execution summaries, row manifests, raw inputs, or sensitive counts. This subset definition governs later shorthand references to renderer-visible “declared artifacts”; the renderer does not receive every producer artifact when a subset is present. Empirical receipt v3 preserves canonical paths and semantic digests for baseline, contract, and execution summary plus owned result IDs; ordinary receipts remain v2. `verify` recomputes v3 lineage, while paper audit-input v2 freezes one receipt-qualified analysis/result/element graph and rejects multiple active empirical baseline digests. This gives exact-byte provenance and comparison-stable scientific identity without imposing estimator taxonomies.

Validate authoring records before execution, then use the empirical command:

```bash
python3 -I -S code/utils/results_pipeline/analysis_contract.py \
  <contract> --baseline <baseline>
python3 code/utils/results_pipeline/results_pipeline.py run-empirical \
  --plan <plan> --bundle <bundle> --receipt <receipt> \
  --caller-allowance-seconds <tracked-job-allowance> -- \
  python3 <analysis-entrypoint>
```

The primary analysis command runs through:

```bash
python3 code/utils/results_pipeline/results_pipeline.py run \
  --plan <plan> --bundle <bundle> --receipt <receipt> \
  --caller-allowance-seconds <tracked-job-allowance> -- \
  python3 <analysis-entrypoint>
```

The separate renderer runs through:

```bash
python3 code/utils/results_pipeline/results_pipeline.py render \
  --receipt <receipt> -- python3 <render-entrypoint>
```

Launch every `run` and `run-empirical` through your harness's tracked long-running job mechanism with a wall-clock allowance sized to the producer (data-acquisition builds routinely need 20+ minutes), then poll the tracked job — never a short synchronous shell call. Both commands enforce this mechanically: they refuse to start unless `--caller-allowance-seconds` declares the launching mechanism's real wall-clock allowance, at least 1200 seconds — so a short synchronous tool call cannot even begin a run, and the refusal text carries these launch instructions. Declare the allowance truthfully; the runner still has no wall-clock allowance of its own, so the invoking tool's timeout is the effective limit, and an interruption discards the entire isolated workspace by design: a killed call silently destroys a legitimate multi-minute acquisition with nothing published and nothing resumable. Before `run`, copy every mutable pipeline document consumed by the computation into the fresh attempt's immutable input-snapshot directory, then create the run-plan-v1 file with exact code/snapshotted-input/artifact/exhibit paths and a `provider_credentials` array containing only the API-key variable names this producer needs (normally empty). Every result-owned plan, bundle, receipt, artifact, and exhibit stays outside the reserved audit namespace `output/evidence/`. The trusted runner imports only those selected keys from the parent environment or the project `.env`; `.env` itself never enters the isolated workspace, and exported non-empty values take precedence. The caller-supplied prose report path is a required declared artifact in both the plan and bundle; the analysis must freshly create it. Stable raw datasets may be declared in place. This prevents a later plan, implication, or report revision from staling the active receipt before its replacement can run. The utility snapshots the plan, code, inputs, and renderer code and exposes only those declared sources inside a fresh execution workspace. Linux descriptor-pins declared regular files, acquires a kernel read lease, and read-only binds them without copying their bytes. If the filesystem cannot enforce the lease, or if the source is a directory or Bubblewrap is unavailable, the runner retains the reflink-first snapshot-copy path. A host writer that requests a leased file causes the attempt to kill its sandbox and fail before releasing the writer, so a transient rewrite cannot affect publishable evidence. Its default-deny filesystem exposes no other project path; the project `.venv` and any external base interpreter it needs are available read-only, as are fixed system runtime roots and the already-established query-only WRDS transport. Result-receipt v2 also records a trusted environment manifest immediately before the producer and renderer run and requires the same manifest immediately afterward: resolved launcher bytes, platform/kernel/machine/libc identity, relevant locale/numerical flags, recognized dependency manifests, and the project venv's installed distribution metadata. This static scan is capped at 64 MiB, 20,000 files, and 20,000 directory entries per snapshot and fails closed on present recognized files it cannot securely fingerprint or that alias credential-bearing project files. Agents remain free to install packages before a run; the receipt records the environment that actually reached that execution. This capture supports the default `captured` label and does not claim to identify every imported module, native library, or external subprocess. Use `exact` only when a complete content-addressed environment/lock manifest is separately declared as an input and independently validated; exact multi-language closure remains #271. On macOS, a project nested inside one of those system roots fails closed rather than becoming readable; use a normal project location under the user's home directory. Staged outputs must stay under `output/`. The producer gets EOF on stdin and a small allowlisted environment rather than ambient shell state. Outbound network and only the plan-selected LLM-provider credentials remain available when the computation requires them; raw WRDS credentials do not. Literal provider credentials and authenticated-proxy passwords of at least eight bytes are rejected from every staged file; any non-empty provider credential or proxy password is also forbidden in producer or renderer command arguments, because those arguments become immutable receipt data. This is not a substitute for the trusted broker tracked in #267. The utility injects the staged project-relative bundle path as `RESULTS_BUNDLE_PATH` and rejects a bundle that differs from the plan. The renderer receives a separate workspace containing only the bundle, declared artifacts, and renderer code; it writes result-bearing tables/figures beneath the injected absolute `RESULTS_EXHIBIT_ROOT`, preserving each declared project-relative exhibit path. Provider credentials and network environment are removed from renderers, and both Linux and macOS deny renderer network access. The contract forbids renderers from reading raw inputs, recomputing, or querying services; filesystem and network isolation enforce that boundary against project data and services. A renderer cannot see undeclared project controls or mutate live project evidence. The trusted parent alone holds the results lock; an independent supervisor kills and waits for the ordinary sandboxed process group if that parent dies, then removes that abandoned isolated workspace so selected credentials cannot remain in host temporary storage (the hostile macOS detached-descendant edge is tracked in #268). Linux additionally runs the payload as PID 1 in its private namespace so normal completion cannot orphan background descendants. After the child exits, the parent verifies the descriptor-bound live files and copied workspace directories, then atomically publishes only the validated artifacts, bundle, receipt, and exhibits. Publication uses a phase-journaled, idempotently recoverable transaction, so a process kill during backup, commit, rollback, or cleanup either rolls back a prepared publication or finishes a recorded terminal cleanup. `launch.sh` refuses to start while that journal exists; run any results utility command (for example `verify-all`) to recover it before the orchestrator can read state or registry bytes. A raw/high-dimensional artifact may use its natural format; the JSON bundle contains its path and semantic projections. Remaining large-directory and non-cloneable macOS fallbacks are tracked in #269. Result-bearing exhibits are never independently authored numerical sources. If shared producer code or a declared input changes, a fresh `run --supersedes <old-receipt>` may replace receipts whose only stale bytes are those shared sources. Every plan/output/receipt path remains fresh; activate, move the stage pointer, and retire the stale predecessor before any paper audit.

The process supervisor performs immediate cleanup on parent death, and a separate lock-free workspace guardian remains until validation and publication leave the isolated-workspace context, closing the post-process kill window too.

**Dataset release boundary.** An analysis intended to pair with a public release sets `requires_dataset_release: true`, which prevents its receipt from using ordinary activation even before the release exists. A producer that declares an artifact beneath `output/dataset/` must set `network_access: false`, select no provider credentials, and include the strict `dataset_release` contract in its run plan; bundle, receipt, and exhibit paths are always forbidden from that namespace, including case aliases on case-folding filesystems. That contract binds one fresh versioned release directory, its checksummed `manifest.json`, the accepted machine-readable rights inventory, an input-provenance map, the current dataset version, the fully rendered pending analysis receipt it pairs with, and its own release receipt path. Its `rights_authority` is `gate2-state` in autonomous dataset-release deployments or `manual-caller` in manual dataset-release deployments; the trusted runner cross-checks that choice against `.deploy_manifest.json`. Autonomous authority requires the exact path/hash/version currently accepted in `pipeline_state.json`. Manual authority uses the exact caller-supplied path/hash/version and rejects an invented `pipeline_state.json`; manual substantive acceptance replaces only Gate-2 sequencing, not any mechanical release check. Every non-manifest data input must map to one or more source IDs classified `open`; restricted source IDs are rejected. The trusted parent parses and fingerprints each authorization file from the same bytes, binds those bytes to the producer input snapshot, requires the manifest to package a byte-exact and path-preserved closure of all declared producer code, and validates every staged release file before publication, so the ordinary networked analysis run cannot place bytes in the public dataset tree. This paired release is the sole exception to the one-pending-receipt run rule; no unrelated producer can start while evidence is pending. Neither member may use ordinary `activate`: `activate-pair` verifies both and moves both registry entries in one crash-recoverable transaction. Pair identity is derived from receipt-bound plans and cross-checked against both the registry and the complete on-disk receipt inventory on every load; cross-kind supersession and one-sided retirement are rejected, and `retire-pair` atomically handles either a pending pair or an active pair. This mechanical boundary enforces the selected rights classification and declared code closure; arbitrary undeclared runtime dependencies, the substantive classification of a source's license, and the semantic accuracy of provenance remain independent audit questions.

After either producer returns, run:

```bash
python3 code/utils/results_pipeline/results_pipeline.py verify \
  --receipt <receipt> --rerender
```

A nonzero exit is a producer-stage failure. Re-fire the producer and its existing substantive reviewer/auditor; do not defer the failure to paper writing.

Verification does not make a pending attempt current. After the stage's substantive reviewer/auditor accepts it, activate it explicitly:

```bash
python3 code/utils/results_pipeline/results_pipeline.py activate --receipt <receipt>
```

`process_log/results_registry.json` is the durable inventory of pending, active, and explicitly retired receipts. It stores an external expected fingerprint for every pending/active receipt, updates that fingerprint transactionally when pending render metadata is added, and moves it into immutable retired history; a receipt cannot bless edits to its own assertions. `run` validates the lifecycle plan and records every result as pending; the immutable receipt also records its exact `supersedes` relation. `render` records exhibits but leaves the receipt pending. Explicit `activate`, after substantive acceptance, adds the new receipt to the active set but deliberately leaves every receipt named by `--supersedes` active.
<!-- AUTONOMOUS_START -->
This makes the cross-file handoff crash-safe: atomically update the stage's report/receipt pointers to the new active receipt, then explicitly retire each replaced ordinary receipt with `retire --receipt <old> --reason "superseded by <new>" --superseded-by <new>`. Dataset-release pairs instead use one `retire-pair` call with both old members and both `--superseded-by-*` replacement members. A crash before the pointer update leaves the old pointer valid and the replacement relation recoverable.
<!-- AUTONOMOUS_END -->
<!-- MANUAL_START -->
In manual mode, the registry is the handoff: after activation, return the new receipt/report path to the caller, then explicitly retire each replaced receipt. There is no pointer update and no `pipeline_state.json`.
<!-- MANUAL_END -->
A crash before retirement leaves both receipts recorded, and paper audit fails closed until handoff completes. A failed or rejected attempt never displaces the prior active lifecycle entry. Pending receipts block every paper audit until activated or explicitly retired with a non-empty reason, and an unrelated second run cannot begin while one is pending; the only exception is the dataset release explicitly bound to its sole pending analysis receipt by the contract above. Never delete a receipt to remove it from an audit. Every attempt uses fresh versioned plan, bundle, artifact, exhibit, and receipt paths disjoint from all active and historical attempt evidence. Prefer versioned analysis/renderer entrypoints too; genuinely shared code may keep its path, but changing it requires one fresh explicitly superseding attempt for every affected active receipt. A paper audit remains blocked until those stale predecessors are retired. An active rerender is only a deterministic regeneration with the exact recorded command and exact recorded bytes. Retire a failed pending attempt before allocating another fresh namespace. When evidence is withdrawn without replacement, use `results_pipeline.py retire --receipt <old> --reason <why>`. For combined versioned coverage, omit `--supersedes` and keep both receipts active. A missing active or retired receipt, altered retired history, an undeclared receipt, a pending receipt, an incomplete activated handoff, or a missing/malformed registry is a hard failure. Setup creates the registry in every paper-producing mode. Update requires the complete same-version registry and never reconstructs deleted or historical evidence state.

## Paper evidence gate

Run this gate after every operation that can change paper prose, captions, tables, figures, or appendix content: initial Stage 5 writing and marker repair; each Stage 6 paper revision; Stage 7 style and operator follow-up edits; each Stage 8 bibliography repair; each Stage 9 paper-writer pass, style re-pass, and table-legibility repair. The final run immediately before Stage 10 is mandatory even if an earlier checkpoint passed.

1. Choose a filesystem-safe `CHECKPOINT` slug that identifies the mutation, for example `stage5-initial`, `stage6-r3`, `stage7-style`, `stage8-bib-r1`, `stage9-r1-p1`, or `stage9-final`.
2. Read `loops.evidence` from `process_log/pipeline_state.json` in autonomous mode or `process_log/manual_evidence_state.json` in manual mode. Set audit attempt `A = loops.evidence.round + 1`, then freeze the exact common input before either auditor launches:

   ```bash
   python3 code/utils/results_pipeline/results_pipeline.py prepare-audit \
     --output output/evidence/audit_input_<CHECKPOINT>_a<A>.json \
     --checkpoint <CHECKPOINT>
   ```

   Read the returned `digest`. The audit input records the recursively discovered graph for supported static LaTeX source/asset/data syntax (including local classes/packages and common listing, CSV, and pgfplots inputs), the exact included active result exhibits, and every citation-command occurrence with its normalized paragraph. Known dynamic readers, custom graphics-extension ordering, and common user-defined citation aliases fail closed; paper authors use supported citation commands directly. Arbitrary TeX macros/primitives cannot be made complete by static parsing, so recorder-backed canonical-build closure remains tracked in #270. Launch these two auditors in parallel on that same `AUDIT_INPUT_PATH`, `AUDIT_INPUT_DIGEST`, current paper, and `CHECKPOINT`:
   - `evidence-auditor`, with all active result bundles/receipts, rendered tables/figures, producer and renderer code; it reconciles every result-bearing table cell and plotted series to declared bundle result IDs/artifact selectors before auditing prose, and writes:
     - `output/evidence/evidence_audit_<CHECKPOINT>_a<A>.md`
     - `output/evidence/evidence_audit_<CHECKPOINT>_a<A>.json`
   - `polish-bibliography` in **checkpoint citation-provenance mode**, with the bibliography, exact Markdown/JSON output paths below, and the prior bound paper receipt when one exists:
     - `output/evidence/citation_audit_<CHECKPOINT>_a<A>.md`
     - `output/evidence/citation_audit_<CHECKPOINT>_a<A>.json`
3. Each auditor first and last runs `results_pipeline.py verify-audit-input --input <AUDIT_INPUT_PATH> --checkpoint <CHECKPOINT>` and returns REVISE if the frozen bytes changed while it worked. `evidence-auditor` also runs `verify-all --rerender`, then checks the semantic chain from result-bearing exhibits to prose/captions. A paper with no computed evidence may have zero active receipts, but every computed exhibit without an active receipt is REVISE. `polish-bibliography` inventories every citation-bearing factual characterization in prose, captions, footnotes, tables, and appendices. It copies the mechanical occurrence ID as its anchor and the mechanical paragraph as claim text, and freshly checks every occurrence against a primary/OpenAlex source at every checkpoint. Project-local prior receipts cannot authenticate themselves, so unchanged uses are not exempt. Neither auditor edits the paper. Both Markdown reports begin with exact `VERDICT: PASS|REVISE`, `CHECKPOINT: <CHECKPOINT>`, and `AUDIT_INPUT_DIGEST: <AUDIT_INPUT_DIGEST>` lines; both JSON summaries echo the audit-input path and digest.
4. On `REVISE`, increment `loops.evidence.round` and route each finding to its owner:
   - stale/missing bundle, artifact, receipt, or renderer; a result-bearing exhibit not generated from a bundle; renderer recomputation/raw-input access → the producing agent, followed by that stage's existing substantive review and a fresh render receipt;
   - prose/caption misreading, unsupported comparison, or ordinary computed prose that should be exposed in an exhibit → paper-writer;
   - a genuinely exceptional computed prose fact that would make no useful table/figure → the producer registers it in the bundle, then paper-writer restates it; the auditor checks it directly against the bundle and explains why the exception is appropriate.
   - a mischaracterized, decorative-as-evidence, or unverifiable citation use → paper-writer deletes/corrects it or replaces it with a verified source; then the citation audit re-runs. A derived prose report or model memory is never citation evidence.

   These retries regenerate the audited paper/evidence chain and therefore use the retry-regenerates-artifact exception: do not reset `loops.evidence.round` between attempts. At `loops.evidence.round >= loops.evidence.cap`, halt for operator routing rather than advancing with an ungrounded paper.
5. On `PASS`, run the binding command with the exact audit paths:

```bash
python3 code/utils/results_pipeline/results_pipeline.py bind-paper \
  --audit-input output/evidence/audit_input_<CHECKPOINT>_a<A>.json \
  --summary output/evidence/evidence_audit_<CHECKPOINT>_a<A>.json \
  --report output/evidence/evidence_audit_<CHECKPOINT>_a<A>.md \
  --citation-summary output/evidence/citation_audit_<CHECKPOINT>_a<A>.json \
  --citation-report output/evidence/citation_audit_<CHECKPOINT>_a<A>.md \
  --receipt process_log/paper_evidence.receipt.json \
  --checkpoint <CHECKPOINT>
python3 code/utils/results_pipeline/results_pipeline.py verify-paper \
  --receipt process_log/paper_evidence.receipt.json --rerender
```

   Only the utility may create `process_log/paper_evidence.receipt.json`. Paper-receipt v4 binds the audit input's registry/paper/result inventories; verification re-runs the audit semantics, cannot substitute a shorter receipt inventory, and requires every citation occurrence to have a fresh check. Commit the paper mutation, PASS audit artifacts, receipt, and reset of `loops.evidence.round` to 0 in the same stage boundary. Any later paper/result/renderer change makes the receipt stale and requires a new checkpoint.

## Reader-facing rule

The writer reads and describes rendered exhibits, not JSON. It writes ordinary scholarly prose and does not expose result IDs or pipeline paths. Abstract/conclusion headline values may restate a displayed result without a local table reference when normal journal style calls for it; the auditor still traces them to the exhibit. The JSON bundle is reproducibility infrastructure, not a reader-facing citation system.

Purely expository tables/figures with no computed evidence — for example a conceptual taxonomy or mechanism DAG — do not need result records. The auditor must affirm that the exhibit is genuinely expository rather than accepting that label as an escape hatch for numerical evidence.
