#!/usr/bin/env python3
"""Regression test for openalex_check._surname_tokens (issue #105).

The author-overlap gate demotes a DOI-confirmed cite to MISS when
doi_author_overlap == 0.0 (openalex_check.py). _surname_tokens must therefore
extract the *surname* — not the given name — regardless of whether the author
string is "Lastname, Firstname" (BibTeX default) or "Firstname Lastname".

Run: python3 test_scripts/test_bib_verify_surname.py
"""
import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "templates", "utils", "bib_verify")
)
from openalex_check import _surname_tokens as s  # noqa: E402

# (author string, expected surname token set) — both name orderings, plus
# hyphenated/multiword surnames, particles, short surnames, and initials.
CASES = [
    ("Smith, John", {"smith"}),
    ("John Smith", {"smith"}),
    ("Lopez-Lira, Alejandro", {"lopez", "lira"}),
    ("Alejandro Lopez-Lira", {"lopez", "lira"}),
    ("Fama, Eugene F.", {"fama"}),
    ("Eugene F. Fama", {"fama"}),
    ("van Binsbergen, Jules", {"binsbergen"}),
    ("Jules van Binsbergen", {"binsbergen"}),
    ("Li, Wei", {"li"}),       # short real surname (issue #54) preserved
    ("Wei Li", {"li"}),
    ("Fama, E. F.", {"fama"}),                 # inverted with initials
    ("King, Robert G., Jr.", {"king"}),        # generational suffix after 2nd comma — must not leak
    ("Smith, John, III", {"smith"}),
    ("da Silva, Maria", {"silva"}),            # particle in inverted surname segment
    ("", set()),                               # empty
    (",", set()),                              # comma only
    ("Smith", {"smith"}),                      # single token
]


def main() -> int:
    failures = []
    for name, expected in CASES:
        got = s(name)
        status = "ok" if got == expected else "FAIL"
        if got != expected:
            failures.append((name, sorted(got), sorted(expected)))
        print(f"  [{status}] {name!r:28} -> {sorted(got)}  (expect {sorted(expected)})")
    if failures:
        print(f"\n{len(failures)} FAILED:")
        for name, got, exp in failures:
            print(f"  {name!r}: got {got}, expected {exp}")
        return 1
    print(f"\nAll {len(CASES)} cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
