## What this is

SymPy is Python's symbolic math library. It is preinstalled (`uv pip install sympy` runs at setup). Any agent with the `Bash` tool can invoke it via `python3 -c "import sympy as sp; ..."`.

This is the **first line** of mathematical verification. It is fast, deterministic, and free — there is no excuse for hand-derivation when SymPy can do it. Use it before falling back to codex-math.

## Two-tier escalation

| Layer | When |
|-------|------|
| **SymPy (this skill)** | Concrete symbolic computation — derivatives, simplification, solving, substitution. Anything mechanical. |
| **codex-math** | Reasoning problems — existence/uniqueness arguments, counterexample construction, proof strategy, multi-step arguments where SymPy returns a mess you can't interpret. |

If you are about to invoke `codex-math` for something that is just algebra, stop and try SymPy first.

## When to use SymPy (must-do, not optional)

You **must** invoke SymPy for these:

- **Sign of a derivative.** Any claim of monotonicity, concavity, or comparative-statics direction. Compute the derivative, then check the sign on the relevant domain.
- **Second-order conditions.** Any claim that an interior FOC root is a maximum (not a minimum or saddle). Compute the second derivative and check sign.
- **Equality of two expressions.** Before claiming two algebraic expressions are equal (e.g., the paper's formula vs. your re-derivation), compute `sp.simplify(a - b)` and confirm it returns `0`.
- **Solving for closed-form roots.** Equilibria, fixed points, first-order-condition roots. Use `sp.solve` or `sp.solveset`.
- **Comparative statics via implicit differentiation.** When a result depends on $\partial x^* / \partial \theta$, derive it symbolically.
- **Numerical sanity check at calibration.** Substitute calibration values into both the paper's formula and your derivation and compare the numbers.
- **Limits and Taylor expansions.** When a result is "for small $\epsilon$" or "as $\theta \to 0$", use `sp.limit` or `sp.series`.

## How to invoke

**Inline one-liner** (preferred for short checks):

```bash
python3 -c "
import sympy as sp
x, gamma = sp.symbols('x gamma', positive=True)
U = (x**(1-gamma) - 1) / (1 - gamma)
print('U\'\'(x) =', sp.simplify(sp.diff(U, x, 2)))
print('Sign for x>0, gamma>1:', sp.simplify(sp.diff(U, x, 2)).subs({gamma: 2}))
"
```

**Multi-line script** (for anything more than ~3 lines): write a temp file and run it.

```bash
cat > /tmp/sympy_check.py << 'EOF'
import sympy as sp
# ... full script ...
EOF
python3 /tmp/sympy_check.py
```

## Reporting protocol (mandatory)

When you use SymPy to verify or check a claim, **paste the exact command and the exact output** into your report. Do not write "I verified with SymPy and it checks out." That is not auditable and you do not get credit for it.

Correct form:

> Verified $\partial \pi^* / \partial c < 0$ via:
> ```
> python3 -c "import sympy as sp; c, alpha = sp.symbols('c alpha', positive=True); pi = (alpha - c)**2 / 4; print(sp.diff(pi, c))"
> ```
> Output: `-alpha/2 + c/2`. For $c < \alpha$ (the relevant region), this is negative. ✓

Incorrect form:

> Checked with SymPy. ✓

## Critical gotchas

1. **Symbol assumptions matter for sign reasoning.** `sp.Symbol('x')` is complex by default. Use `sp.Symbol('x', positive=True)` (or `real=True`, `nonnegative=True`) when the sign of the result depends on the sign of the input. Without assumptions, SymPy will refuse to simplify $\sqrt{x^2}$ to $x$, and `sp.solve` may return spurious complex roots.

2. **`==` is structural, not mathematical.** `sp.sin(x)**2 + sp.cos(x)**2 == 1` returns `False` because the structures differ. Use `sp.simplify(a - b) == 0`, or `sp.Eq(a, b).simplify()`, to test mathematical equality.

3. **`sp.simplify` is not omniscient.** If `simplify` returns a mess, try `expand`, `factor`, `together`, `apart`, `trigsimp`, `radsimp`, or `cancel` — each targets a different kind of expression. If none work, the expression may genuinely not simplify, OR you may need a substitution before simplifying.

4. **`sp.solve` returns a list; check what you got.** It may return complex roots, multiple roots, or `[]` (no closed form). For real-only roots, use `sp.solveset(eq, x, domain=sp.S.Reals)`. For numerical roots when no closed form exists, use `sp.nsolve(eq, x, x0)`.

5. **Use `sp.Rational(1, 3)` not `1/3` for exact arithmetic.** Python's `1/3` is `0.333...` (a float), which propagates floating-point error through symbolic computation. `sp.Rational(1, 3)` is exact.

6. **`sp.Sum` and `sp.Product` need closed-form-able indices.** They will not crunch numerically — use `sp.summation` for closed-form, or compute the sum in a Python loop if you need a number.

## Compact examples

### 1. Sign of second derivative (SOC check)

```python
import sympy as sp
q, c, a = sp.symbols('q c a', positive=True)
profit = (a - q) * q - c * q          # monopoly profit, linear demand
foc = sp.diff(profit, q)
soc = sp.diff(profit, q, 2)
q_star = sp.solve(foc, q)[0]
print('q* =', q_star, '  SOC =', soc)  # SOC = -2 < 0 → maximum ✓
```

### 2. Comparative statics

```python
import sympy as sp
p, c, alpha = sp.symbols('p c alpha', positive=True)
demand = alpha - p
profit = (p - c) * demand
p_star = sp.solve(sp.diff(profit, p), p)[0]
print('p* =', p_star)
print('dp*/dc =', sp.diff(p_star, c))   # should be 1/2 > 0
```

### 3. Verifying claimed identity

```python
import sympy as sp
gamma, x = sp.symbols('gamma x', positive=True)
form_a = (x**(1 - gamma) - 1) / (1 - gamma)         # paper's stated form
form_b = -(x**(1 - gamma) - 1) / (gamma - 1)        # your rearrangement
diff = sp.simplify(form_a - form_b)
assert diff == 0, f'MISMATCH: {diff}'                # raises if forms disagree
print('OK')
```

Note: avoid using `sp.integrate` for re-derivation when the integrand has parameter-dependent branches (e.g., $x^{-\gamma}$ branches at $\gamma = 1$) — SymPy returns a `Piecewise` that won't simplify against a closed-form expression. Write the antiderivative directly and verify equality.

### 4. Numerical sanity at calibration

```python
import sympy as sp
gamma, x = sp.symbols('gamma x', positive=True)
crra = (x**(1 - gamma) - 1) / (1 - gamma)
print(float(crra.subs({gamma: 2, x: 4})))            # → 0.75
```

## When SymPy fails — escalate, don't fudge

If SymPy cannot produce a clean answer (returns an unsimplified blob, `[]` from solve, or hangs), **do not** fall back to hand-algebra and call it good. Two routes:

1. **Restate the problem** with stronger assumptions (positive symbols, specific functional forms) and try again — the issue is often missing constraints.
2. **Escalate to codex-math** with explore mode if the problem requires a proof strategy or counterexample, not raw computation. Pass codex the SymPy output so it knows what was tried.

A SymPy failure that you "work around" by hand is exactly the case the math-auditor is supposed to catch.
