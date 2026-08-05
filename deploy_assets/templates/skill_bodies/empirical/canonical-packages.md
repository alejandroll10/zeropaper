## When invoked by the user

If you received an argument (method name, package name, or paper citation), respond with a concise three-part answer: (1) whether a canonical package exists for this method in Python / R / Stata — use your training knowledge first, then PyPI / CRAN / SSC lookups via Bash curl (`curl -s https://pypi.org/pypi/<name>/json | jq '.info.summary, .info.author, .info.version, .urls[-1].upload_time'`) to verify; (2) the package name(s) and the discovery path you used (training knowledge / PyPI / CRAN / SSC / WebSearch); (3) current maintenance status (last upload date if available, author-maintained vs community-maintained). If no canonical exists in the working language, name the closest cross-language canonical and the subprocess wrapper recipe.

If no argument was provided, the rest of this skill is a policy reference — read it before writing code for any named econometric method.

## Purpose

Policy + procedure for not reimplementing econometric methods that have canonical, author-maintained packages. Field-tier finance referees (JF / JFE / RFS) reject custom Python (or R / Stata) code that re-derives well-known estimators — they expect canonical implementations from canonical references. Custom code reproduces by definition but routinely disagrees with canonical defaults on small-sample corrections, bias adjustments, and edge cases. See [issue #36](https://github.com/alejandroll10/zeropaper/issues/36) for the motivating examples.

This skill **does not catalog packages.** It tells you (a) when to look one up, (b) where to look, and (c) how to document a deviation. The catalog of which package is canonical for which method is a moving target (new ports appear, old ones go unmaintained); you discover the current state on demand.

## When to consult — before writing, not after

Before you author code for any **named econometric method**, look up whether a canonical package exists in your working language. Named methods are the ones that come with a paper attribution: "we apply HonestDiD bounds (Rambachan-Roth 2023)", "we use the Callaway-Sant'Anna estimator (CS 2021)", "we report Shanken-corrected standard errors", "we use the wild cluster bootstrap (CGM 2008)". If you find yourself writing `np.linalg.solve(...)` or `scipy.optimize.minimize(...)` to implement a named method, stop and check the canonical first.

If the canonical exists in your working language, **use it**. Do not hand-roll.

## Where to look — search recipes

Try these in order; stop at the first credible hit.

1. **Method author's own page.** The original method authors increasingly maintain reference packages. Search `<lead author> github` or `<lead author> packages` or the author's faculty website. Author-maintained packages are the highest authority — they encode the authors' own defaults and corrections. Examples of the discovery pattern: Cinelli maintains `sensemakr`; the Cattaneo group maintains the `rdrobust` / `rddensity` / `rdlocrand` / `rdmulti` suite; Callaway and Sant'Anna maintain R `did`; Roodman maintains Stata `boottest` and `xtabond2`.

2. **PyPI.** For Python, `curl -s https://pypi.org/pypi/<name>/json | jq .info.summary` confirms a package exists and shows its description; or browse `https://pypi.org/project/<name>/`. Search PyPI for the method's common name (e.g., "honestdid", "sensemakr", "rdrobust", "synthdid"). Many R packages have community Python ports; verify maintenance is recent (last upload within ~2 years) before relying.

3. **CRAN.** For R, `https://cran.r-project.org/web/packages/<name>/` confirms a CRAN listing; or use `https://cran.r-project.org/search.html`. Many canonicals are R-first because the method paper's replication code is in R.

4. **Stata SSC.** For Stata, `ssc describe <cmd>` in a Stata session, or browse `https://ideas.repec.org/s/boc/bocode.html`. Many finance canonicals (event studies, dynamic panel GMM, wild cluster bootstrap) are Stata-native.

5. **WebSearch** with the method name + "canonical package" or + "official implementation" if the first four don't resolve. Cross-check against the method paper's published code link (most journal pages list a replication archive — that's authoritative).

6. **The `method-checker` agent's report** — if you are reading this skill *after* the method-checker has already flagged your code, the report names the package it expects you to use. Use that.

If none of these surfaces a maintained package after a reasonable search, the method is in genuine gap territory and you may implement it carefully — but document the search you did in the script docstring so the method-checker doesn't have to repeat it.

## Justification taxonomy for legitimate deviation

If you must write custom code for a method that has a canonical package, the script docstring AND the relevant `output/stage3a/*.json` output must include one of the following four labels, verbatim. Missing the justification entirely (neither location) is a REVISE from `method-checker`. Carrying the justification in only one location (docstring without the JSON mirror, or vice versa) is a Minor flag on otherwise-PASS — non-blocking, but `method-checker` will direct you to add the missing mirror; full alignment requires both locations.

- **(a) Genuinely novel.** The method is new to this paper, not in any canonical package, not a wrapper around an existing canonical method. Cite the working paper where the method is first developed (typically your own).
- **(b) Canonical lacks a needed feature.** The canonical exists but does not support the specific variant required (e.g., staggered treatment, multi-way clustering, your data's specific edge case). Name the missing feature; link to the package's open issue / feature-request thread if one exists.
- **(c) Canonical unavailable in working language.** The canonical exists only in R or Stata and the subprocess path (`rpy2`, `subprocess` invoking R / Stata) is genuinely infeasible — not just inconvenient. **Subprocess-first rule:** if Python is your working language and the canonical is R-only or Stata-only, the first preference is to call it via `rpy2` or a `subprocess` wrapper; that counts as canonical use. (c) is acceptable only when the wrapper truly cannot work (e.g., paid-license Stata unavailable on the runner; `rpy2` cannot link against the installed R for environmental reasons).
- **(d) Operator-directed deviation.** The operator (orchestrator or human user) explicitly requested a custom implementation — for pedagogical, replication-of-method-paper, or research-comparison reasons. Quote the directive verbatim in the docstring.

## How `method-checker` uses this skill

The `method-checker` agent fires at Stage 3a step 7.5 in parallel with `data-integrity-auditor` and `data-selection-auditor`. It scans `code/empirical.py` and `output/stage3a/empirical_analysis.md` for named econometric methods, looks each one up using the search recipes above (its own training knowledge + WebSearch + PyPI / CRAN queries via Bash), and flags any custom implementation of a method whose canonical package the empiricist could have used. For each flag, the agent verifies the script docstring carries an (a)–(d) justification; missing or implausible justifications become REVISE.

The agent does not check the math correctness of the custom code — that is the `empirics-auditor`'s reproducibility check. The agent checks canonical-availability + justification only.

## Output format expected by `method-checker`

When you implement a named method, your script should look like this (Python example for a method with a canonical Python package):

```python
"""Estimates [method name] from [paper citation].

Canonical: <package name> (PyPI / CRAN / SSC), <author> maintained.
This script uses the canonical via `import <package>` — no custom math.
"""
from <package> import <function>
result = <function>(...)
```

If you must deviate, the docstring carries the justification:

```python
"""Custom implementation of [method name] from [paper citation].

Canonical: <package name> in <language>; not available in Python.
Justification: (c) canonical unavailable in working language.
Subprocess path attempted: <yes/no, with reason>.
Implementation notes: <key defaults you chose; any small-sample correction;
any edge-case handling>.
"""
```

The corresponding entry in `output/stage3a/*.json` should mirror the justification under a `method_notes` or `justification` key so `method-checker` can verify mechanically.

## Coverage scope

This skill is finance-focused (JF / JFE / RFS empirical work). Macro-identification methods (SVAR, HFI, narrative shocks, DSGE-aware estimators) and labor / IO methods are partially covered — most have canonical packages in the same way, but the agent's lookup may be less reliable. If you are working in those domains, give the method-checker's flags extra scrutiny and don't treat absence-of-flag as confirmation that no canonical exists.
