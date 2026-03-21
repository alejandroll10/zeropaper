# Empirical Extension — Stages 3b/3c

## Overview

This extension adds data-driven calibration and empirical testing to the theory pipeline. It runs after Stage 3a (theoretical implications) and before Stage 4 (self-attack).

## Prerequisites

- Python 3 with pandas, numpy, statsmodels, scipy
- For FRED data: API key in `.env` as `FRED_API_KEY=your-key` (free from https://fred.stlouisfed.org/docs/api/api_key.html)
- Ken French and Chen-Zimmerman data require no authentication

Install dependencies:
```bash
pip install pandas numpy statsmodels scipy fredapi pandas-datareader python-dotenv
```

## Stage 3b: Calibration

**Agent:** `calibrator`

1. Read the theory draft and implications
2. Launch calibrator agent
3. Calibrator identifies target moments, fetches data via skills, solves for parameters
4. Save results to `output/stage3b/calibration.md`
5. Save code to `code/calibration.py`
6. Commit: `artifact: calibration — [N] moments matched`

## Stage 3c: Empirical Tests

**Agent:** `empiricist`

1. Read the theory draft, implications, and calibration results
2. Launch empiricist agent
3. Empiricist designs simple tests of the model's predictions, fetches data, runs tests
4. Save results to `output/stage3c/empirical_tests.md`
5. Save code to `code/empirical_tests.py`
6. Commit: `artifact: empirical tests — [N] predictions tested`

## Integration with pipeline

After Stages 3b/3c complete:
- Self-attacker (Stage 4) receives calibration + empirical results alongside the theory
- Scorer evaluates empirical grounding as part of Fertility dimension
- Paper-writer includes calibration table and empirical evidence sections

## Data skills

Skills are installed to `.claude/skills/` and injected into agent context via the `skills:` frontmatter field.

| Skill | What | Auth |
|-------|------|------|
| `fred` | Macro/financial time series (800K+ series) | API key (free) |
| `ken-french` | Factor returns, portfolios, breakpoints | None |
| `chen-zimmerman` | 200+ firm-level anomaly signals | None |

Researchers can add more data skills by creating `.claude/skills/{name}/SKILL.md`.
