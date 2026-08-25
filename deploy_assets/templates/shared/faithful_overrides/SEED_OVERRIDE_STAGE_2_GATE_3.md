### Faithful-mode override (applies because `faithful: true` in `pipeline_state.json`; supersedes the seeded-mode override)

<!-- DATA_FIRST_START -->
**Data-first reading of this override.** "Gate 2's math audit has already established" reads as "Gate 2's dataset-specification audit has already established" — the expensive pass foregone is the same, and the trade holds for the same reason (the contract-pinned dataset's correctness is owned by the spec audit plus the Stage 3a audit chain, not by exploration). Everything else applies verbatim: document the novelty concern, run Stage 3 (the fact portfolio), proceed; additions on top of the contract (an extra adjudication, a new-fact candidate) are allowed and encouraged, but may not replace the contract's stated contribution as the headline.
<!-- DATA_FIRST_END -->
**Note:** the normal Gate 3 KNOWN routing above (abandon the theory / return with a new approach) is **superseded** in faithful mode — faithful never abandons on KNOWN, it documents and proceeds.

**Gate 3 KNOWN/INCREMENTAL**: document the novelty concern in `output/seed/limitations.md`, then **run Stage 3 (implications) and proceed to Stage 4** with the contract intact. Stage 2b (exploration) stays skipped — the expensive computational pass buys little on a contract-pinned result that Gate 2's math audit has already established — but Stage 3 is not optional: `output/stage3/implications.md` is a hard input to the scorer's Surprise cap/floor rules at Gate 4, to `paper-writer` at Stage 5, and to `puzzle-triager`. Do NOT instruct theory-generator to "find a result the existing literature does not imply" or to "escape the obvious version" — those instructions in the normal Gate 3 routing are designed to produce a different result than the seed described, which is a substitution and forbidden in faithful mode.

The KNOWN/INCREMENTAL verdict is honest information about the seed's contribution: it is already in the literature, or it is incremental over the literature. That is a fact about the seed and the literature, not a problem the pipeline can fix by deviating from the seed. The faithful response is to document the concern (so the paper's contribution claim is honest) and ship.

If theory-generator wants to **add** a non-obvious extension of the contract's mechanism on top of the faithfully-implemented contract — an additional theorem, comparative static, or characterization — that is allowed and encouraged. What is not allowed is letting the additional result *replace* the contract's stated contribution as the paper's headline.

Append a row to `process_log/pivot_log.md` recording the verdict, classification (`[DOCUMENT-AND-PROCEED]`), and rationale.
