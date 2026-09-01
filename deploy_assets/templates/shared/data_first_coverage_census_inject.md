## Special launch override: coverage census (data-first Gate 2)

When the launch explicitly says **coverage-census-only**, stop before the ordinary analysis workflow. Read the exact dataset specification, exact rights inventory, Stage 1 pilot report, and prompt-supplied `COVERAGE_CERTIFICATE_PATH = output/stage2/coverage_certificate_c{dataset_coverage_certificate_serial}_s{dataset_spec_serial}_vN.json`. This is a narrow Gate 2 acquisition census, not an analysis plan, Stage 3a build, result bundle, or release: create none of those artifacts.

Enumerate the **entire** finite universe for every commitment in `## Exact coverage commitments`, using the spec's authoritative enumerator and unique event key. For every event, attempt the exact qualifying-evidence predicate and all spec-named fallback sources. Do not stop after the first gap: one firing must surface every gap it can, so a mutation responds to the whole residue rather than discovering one event per pipeline cycle. Record `verified` only when the qualifying evidence was actually acquired; record `gap` only after the complete named search protocol ran and found no qualifying evidence; record `error` for rate limits, authentication failures, outages, parser failures, or any other condition that prevented the search from completing. An operational error is not evidence that the event is unsatisfiable.

Write exactly this machine-readable shape (replace symbolic values; sort commitments by `commitment_id` and events lexicographically by their canonical JSON event key):

```json
{
  "schema_version": 1,
  "dataset_version": 1,
  "dataset_spec": {"path": "output/stage2/theory_draft_v1.md", "sha256": "sha256:<64 lowercase hex>"},
  "rights_inventory": {"path": "output/stage2/source_rights_s1_v1.json", "sha256": "sha256:<64 lowercase hex>"},
  "commitments": [
    {
      "commitment_id": "stable_lowercase_id",
      "universe_definition": "the binding spec text, faithfully transcribed",
      "enumerator": "exact source/query/archive used",
      "event_key_fields": ["field_a", "field_b"],
      "qualifying_evidence_predicate": "the binding spec text, faithfully transcribed",
      "enumeration_evidence": [{"source_id": "source_id", "locator": "exact terminal page/count/archive member", "checked_at": "YYYY-MM-DD", "content_sha256": "sha256:<64 lowercase hex>", "terminal": true}],
      "enumeration_status": "complete",
      "enumeration_error": null,
      "enumerated_count": 1,
      "status_counts": {"verified": 1, "gap": 0, "error": 0},
      "events": [
        {"event_key": {"field_a": "value", "field_b": "value"}, "status": "verified", "evidence": [{"source_id": "source_id", "locator": "exact URL/query/archive member", "checked_at": "YYYY-MM-DD", "content_sha256": "sha256:<64 lowercase hex>", "outcome": "predicate-satisfied", "diagnostic": null}], "reason": "predicate satisfied"}
      ]
    }
  ],
  "status": "PASS"
}
```

The commitment IDs must equal the launch-supplied routed set exactly, and each `event_key_fields` array must exactly equal its spec subsection's machine-readable array. Every event key object must contain exactly those fields, with no missing or extra key. `enumeration_status` is `complete` only after the spec's authoritative enumerator terminal condition was actually observed and recorded in a non-empty `enumeration_evidence` array containing at least one `terminal: true` row with a re-queryable locator and digest; this proof is required even for an empty universe. Its `enumeration_error` must then be null. Any pagination, parser, authentication, rate, outage, or other failure before that proof makes enumeration status `error` with a non-empty `enumeration_error`, even when zero event keys or only a prefix are known. Thus `enumeration_status: complete` iff `enumeration_error` is null and terminal proof is valid; `enumeration_status: error` iff `enumeration_error` is a non-empty diagnostic. Keep the commitment row and every known event row in the error case.

Every event row must have a non-empty `evidence` array. Each evidence record has non-empty `source_id`, re-queryable `locator`, and `checked_at`; `outcome` is exactly `predicate-satisfied`, `predicate-not-satisfied`, or `operational-error`; and `diagnostic` is null only for `predicate-satisfied` and otherwise a non-empty string. A `verified` row requires at least one `predicate-satisfied` evidence record with a lowercase `sha256:<64 hex>` `content_sha256`. A `gap` row requires evidence for every source in the completed named search protocol, every record must be `predicate-not-satisfied` with a content digest, and `reason` must be a non-empty diagnostic. An `error` row requires at least one `operational-error` evidence record and a non-empty diagnostic `reason`; its `content_sha256` may be null only when the failed attempt returned no content bytes. Evidence locators must be independently re-queryable and content digests must describe the bytes actually observed; do not persist restricted payloads merely to make the certificate self-contained.

Each `enumerated_count` must equal the event-row count; each `status_counts` value must equal the actual number of rows with that status, and their sum must equal the count. `PASS` is legal only when every commitment's enumeration is complete and every event is `verified`; `GAPS` requires complete enumeration for every commitment, at least one `gap`, and no row error; any enumeration or row error makes the top-level status `ERROR`. Before returning, parse the JSON you wrote and check all of these invariants yourself.
