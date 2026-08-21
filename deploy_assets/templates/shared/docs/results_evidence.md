# Computed results, exhibits, and evidence audit

This contract applies to every paper-producing mode. It binds two separate independent checks at one paper boundary: computed evidence is audited by `evidence-auditor`, while factual characterizations of cited work are audited by `polish-bibliography` in checkpoint mode. Formal theory notation remains outside both; citation-key identity retains `bib-verifier`.

## Producer contract

Every active evidence producer writes one pre-run plan, one schema-v1 canonical bundle, and one receipt. The plan is the matching bundle stem plus `.plan.json` unless the launch supplies another exact versioned path.

| Producer | Bundle | Receipt |
|---|---|---|
| theory-explorer | `output/stage2b/results.json` initially; fresh `<exploration-stem>_aK_results.json` on re-fire | matching `*.receipt.json` sibling |
| empiricist | `empirical_feasibility_results.json` / `empirical_analysis_results.json` initially; fresh `<analysis-stem>_aK_results.json` on re-fire | matching `*results.receipt.json` sibling |
| experiment-designer | `experiment_results.json` initially; fresh `experiment_results_vN_aK_results.json` on re-fire | matching `*results.receipt.json` sibling |

The primary analysis command runs through:

```bash
python3 code/utils/results_pipeline/results_pipeline.py run \
  --plan <plan> --bundle <bundle> --receipt <receipt> -- \
  python3 <analysis-entrypoint>
```

The separate renderer runs through:

```bash
python3 code/utils/results_pipeline/results_pipeline.py render \
  --receipt <receipt> -- python3 <render-entrypoint>
```

Before `run`, copy every mutable pipeline document consumed by the computation into the fresh attempt's immutable input-snapshot directory, then create the run-plan-v1 file with exact code/snapshotted-input/artifact/exhibit paths and a `provider_credentials` array containing only the API-key variable names this producer needs (normally empty). Every result-owned plan, bundle, receipt, artifact, and exhibit stays outside the reserved audit namespace `output/evidence/`. The trusted runner imports only those selected keys from the parent environment or the project `.env`; `.env` itself never enters the isolated workspace, and exported non-empty values take precedence. The caller-supplied prose report path is a required declared artifact in both the plan and bundle; the analysis must freshly create it. Stable raw datasets may be declared in place. This prevents a later plan, implication, or report revision from staling the active receipt before its replacement can run. The utility snapshots the plan, code, inputs, and renderer code and copies only those declared sources into a fresh execution workspace. Its default-deny filesystem exposes no other project path; the project `.venv` and any external base interpreter it needs are available read-only, as are fixed system runtime roots and the already-established query-only WRDS transport. The receipt does not automatically fingerprint that interpreter/dependency closure: label a run `captured` unless a complete content-addressed environment/lock manifest is declared as an input and independently validated, in which case `exact` is appropriate; trusted automatic capture remains #271. On macOS, a project nested inside one of those system roots fails closed rather than becoming readable; use a normal project location under the user's home directory. Staged outputs must stay under `output/`. The producer gets EOF on stdin and a small allowlisted environment rather than ambient shell state. Outbound network and only the plan-selected LLM-provider credentials remain available when the computation requires them; raw WRDS credentials do not. Literal provider credentials and authenticated-proxy passwords of at least eight bytes are rejected from every staged file, but this is not a substitute for the trusted broker tracked in #267. The utility injects the staged project-relative bundle path as `RESULTS_BUNDLE_PATH` and rejects a bundle that differs from the plan. The renderer receives a separate workspace containing only the bundle, declared artifacts, and renderer code; it writes result-bearing tables/figures beneath the injected absolute `RESULTS_EXHIBIT_ROOT`, preserving each declared project-relative exhibit path. Provider credentials and network environment are removed from renderers, and macOS also denies renderer network access. The contract forbids renderers from reading raw inputs, recomputing, or querying services; filesystem isolation enforces the first two against project data, while Linux direct-network enforcement remains an explicit #267 boundary. A renderer cannot see undeclared project controls or mutate live project evidence. The trusted parent alone holds the results lock; an independent supervisor kills and waits for the ordinary sandboxed process group if the parent dies, then removes that abandoned isolated workspace so selected credentials cannot remain in host temporary storage (the hostile macOS detached-descendant edge is tracked in #268). Linux additionally runs the payload as PID 1 in its private namespace so normal completion cannot orphan background descendants. After the child exits, the parent verifies the workspace sources and outputs, then atomically publishes only the validated artifacts, bundle, receipt, and exhibits. Publication uses a phase-journaled, idempotently recoverable transaction, so a process kill during backup, commit, rollback, or cleanup either rolls back a prepared publication or finishes a recorded terminal cleanup. A raw/high-dimensional artifact may use its natural format; the JSON bundle contains its path and semantic projections. Workspace snapshots use copy-on-write cloning when available and otherwise copy current-attempt inputs; the large non-reflink case is tracked in #269. Result-bearing exhibits are never independently authored numerical sources. If shared producer code or a declared input changes, a fresh `run --supersedes <old-receipt>` may replace receipts whose only stale bytes are those shared sources. Every plan/output/receipt path remains fresh; activate, move the stage pointer, and retire the stale predecessor before any paper audit.

The process supervisor performs immediate cleanup on parent death, and a separate lock-free workspace guardian remains until validation and publication leave the isolated-workspace context, closing the post-process kill window too.

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

`process_log/results_registry.json` is the durable inventory of pending, active, and explicitly retired receipts. It stores an external expected fingerprint for every pending/active receipt, updates that fingerprint transactionally when pending render metadata is added, and moves it into immutable retired history; a receipt cannot bless edits to its own assertions. `run` validates the lifecycle plan and records every result as pending; the immutable receipt also records its exact `supersedes` relation. `render` records exhibits but leaves the receipt pending. Explicit `activate`, after substantive acceptance, adds the new receipt to the active set but deliberately leaves every receipt named by `--supersedes` active. This makes the cross-file handoff crash-safe: atomically update the stage's report/receipt pointers to the new active receipt, then explicitly retire each replaced receipt with `retire --receipt <old> --reason "superseded by <new>" --superseded-by <new>`. A crash before the pointer update leaves the old pointer valid and the replacement relation recoverable; a crash before retirement leaves both receipts recorded, and paper audit fails closed until handoff completes. A failed or rejected attempt never displaces the prior active lifecycle entry. Pending receipts block every paper audit until activated or explicitly retired with a non-empty reason, and a second run cannot begin while one is pending. Never delete a receipt to remove it from an audit. Every attempt uses fresh versioned plan, bundle, artifact, exhibit, and receipt paths disjoint from all active and historical attempt evidence. Prefer versioned analysis/renderer entrypoints too; genuinely shared code may keep its path, but changing it requires one fresh explicitly superseding attempt for every affected active receipt. A paper audit remains blocked until those stale predecessors are retired. An active rerender is only a deterministic regeneration with the exact recorded command and exact recorded bytes. Retire a failed pending attempt before allocating another fresh namespace. When evidence is withdrawn without replacement, use `results_pipeline.py retire --receipt <old> --reason <why>`. For combined versioned coverage, omit `--supersedes` and keep both receipts active. A missing active or retired receipt, altered retired history, an undeclared receipt, a pending receipt, an incomplete activated handoff, or a missing/malformed registry is a hard failure. Autonomous setup/update creates the registry; a manual project must explicitly run `results_pipeline.py init-registry` before its first result and may not reconstruct a deleted registry after receipts exist.

## Paper evidence gate

Run this gate after every operation that can change paper prose, captions, tables, figures, or appendix content: initial Stage 5 writing and marker repair; each Stage 6 paper revision; Stage 7 style and operator follow-up edits; each Stage 8 bibliography repair; each Stage 9 paper-writer pass, style re-pass, and table-legibility repair. The final run immediately before Stage 10 is mandatory even if an earlier checkpoint passed.

1. Choose a filesystem-safe `CHECKPOINT` slug that identifies the mutation, for example `stage5-initial`, `stage6-r3`, `stage7-style`, `stage8-bib-r1`, `stage9-r1-p1`, or `stage9-final`.
2. Set audit attempt `A = loops.evidence.round + 1`, then freeze the exact common input before either auditor launches:

   ```bash
   python3 code/utils/results_pipeline/results_pipeline.py prepare-audit \
     --output output/evidence/audit_input_<CHECKPOINT>_a<A>.json \
     --checkpoint <CHECKPOINT>
   ```

   Read the returned `digest`. The audit input records the recursively discovered graph for supported static LaTeX source/asset/data syntax (including local classes/packages and common listing, CSV, and pgfplots inputs), the exact included active result exhibits, and every citation-command occurrence with its normalized paragraph. Known dynamic readers fail closed; arbitrary TeX macros/primitives cannot be made complete by static parsing, so recorder-backed canonical-build closure remains tracked in #270. Launch these two auditors in parallel on that same `AUDIT_INPUT_PATH`, `AUDIT_INPUT_DIGEST`, current paper, and `CHECKPOINT`:
   - `evidence-auditor`, with all active result bundles/receipts, rendered tables/figures, producer and renderer code; it reconciles every result-bearing table cell and plotted series to declared bundle result IDs/artifact selectors before auditing prose, and writes:
     - `output/evidence/evidence_audit_<CHECKPOINT>_a<A>.md`
     - `output/evidence/evidence_audit_<CHECKPOINT>_a<A>.json`
   - `polish-bibliography` in **checkpoint citation-provenance mode**, with the bibliography, exact Markdown/JSON output paths below, and the prior bound paper receipt when one exists:
     - `output/evidence/citation_audit_<CHECKPOINT>_a<A>.md`
     - `output/evidence/citation_audit_<CHECKPOINT>_a<A>.json`
3. Each auditor first and last runs `results_pipeline.py verify-audit-input --input <AUDIT_INPUT_PATH> --checkpoint <CHECKPOINT>` and returns REVISE if the frozen bytes changed while it worked. `evidence-auditor` also runs `verify-all --rerender`, then checks the semantic chain from result-bearing exhibits to prose/captions. A paper with no computed evidence may have zero active receipts, but every computed exhibit without an active receipt is REVISE. `polish-bibliography` inventories every citation-bearing factual characterization in prose, captions, footnotes, tables, and appendices. It copies the mechanical occurrence ID as its anchor and the mechanical paragraph as claim text. It may label a use `reused` only when the same claim text, cite keys, status, and exact source pointers occur in the prior citation summary whose fingerprint is bound in `process_log/paper_evidence.receipt.json`; all others require a fresh primary-source/OpenAlex check. Neither auditor edits the paper. Both Markdown reports begin with exact `VERDICT: PASS|REVISE`, `CHECKPOINT: <CHECKPOINT>`, and `AUDIT_INPUT_DIGEST: <AUDIT_INPUT_DIGEST>` lines; both JSON summaries echo the audit-input path and digest.
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

   Only the utility may create `process_log/paper_evidence.receipt.json`. Commit the paper mutation, PASS audit artifacts, receipt, and reset of `loops.evidence.round` to 0 in the same stage boundary. Any later paper/result/renderer change makes the receipt stale and requires a new checkpoint.

## Reader-facing rule

The writer reads and describes rendered exhibits, not JSON. It writes ordinary scholarly prose and does not expose result IDs or pipeline paths. Abstract/conclusion headline values may restate a displayed result without a local table reference when normal journal style calls for it; the auditor still traces them to the exhibit. The JSON bundle is reproducibility infrastructure, not a reader-facing citation system.

Purely expository tables/figures with no computed evidence — for example a conceptual taxonomy or mechanism DAG — do not need result records. The auditor must affirm that the exhibit is genuinely expository rather than accepting that label as an escape hatch for numerical evidence.
