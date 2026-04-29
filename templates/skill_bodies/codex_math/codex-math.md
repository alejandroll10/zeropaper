## What this is

OpenAI Codex (gpt-5.5) as a mathematical co-processor. Codex runs non-interactively via `codex exec` and returns structured results. Use it for hard proof problems that resist direct attempts.

Scripts are at `code/utils/codex_math/`. Three modes: verify, write, explore.

## The erratic genius caveat

Codex is an excellent mathematician but produces a substantial fraction of false positives. It is brilliant and unreliable. Treat every output as a lead, not a verdict.

**Real catches:** concrete counterexamples, dimensional/sign errors, genuine logical gaps, missing existence arguments, incorrect domain specifications.

**False positives:** flagging standard conventions as errors, demanding unnecessary generality, over-interpreting degenerate cases, flagging stated assumptions as "unjustified," missing paper-level context.

**How to tell them apart:**
- A real catch involves a specific counterexample or points to a concrete step that doesn't follow
- A false positive involves a convention mismatch, demands regularity conditions that are standard, or flags something the paper already addresses elsewhere

**Do not accept or reject Codex output without triaging it yourself.** Read each finding. Check whether the concern is real. If Codex says a step is wrong, verify the specific algebra. If Codex says a proof is correct, still check the key steps.

## When to use

- **After a proof attempt fails.** If you tried to prove a result and got stuck, ask Codex to explore or write the proof. It may find a strategy you missed.
- **After the math auditor flags a gap.** If the auditor identified an unproved load-bearing claim, use Codex to attempt the proof before weakening the claim.
- **For hard counterexample search.** If you need to know whether a conjecture is true or false, Codex can systematically explore.
- **For independent verification.** Run Codex verify on your own proofs as a second opinion.
- **Do not use for routine algebra.** Simple FOCs, envelope conditions, and standard derivations don't need Codex. Use it for the hard problems.

## Reasoning effort

Codex supports three reasoning effort levels. **Do not limit effort on hard problems.** The cost of running high effort is small; the cost of missing a proof or counterexample is large.

| Task | Effort | When to use |
|------|--------|-------------|
| Quick sanity check | `low` | Routine sign/dimension check, already confident |
| Standard verification | `medium` | Default. Checking a proof you believe is correct |
| Hard proof, conjecture, or exploration | `high` | **Always use high for:** unproved load-bearing claims, counterexample search, writing proofs for results that resisted direct attempts, anything the math auditor flagged as Critical |

When in doubt, use `high`. There is no reason to economize on reasoning effort for important results.

## How to prompt Codex well

Codex is non-interactive — it gets one prompt and returns one response. The quality of its output depends entirely on the quality of your prompt. **Do the prep work before calling any script.**

### For verify and write modes (scripts handle the prompt, but you choose what to extract)

The scripts construct the prompt from extracted content. Your job is to give the right pattern so it extracts the right block. If the proposition references definitions or equations from elsewhere in the paper, the script grabs referenced equations automatically, but it may miss context. When verifying a hard proof:

1. Check that the extracted block includes everything Codex needs (run `extract_block.sh` first to see what it pulls)
2. If critical context is missing, use explore mode instead and construct the full prompt manually

### For explore mode (you write the prompt)

This is where prompt quality matters most. Before calling `codex_explore.sh`:

1. **State the exact claim.** Not "check the concavity" but "Prove or disprove: V(τ) is strictly concave in τ for all τ > 0, where x*(τ) is the unique fixed point of x = g(τ, x) with g defined by [equation]."
2. **Define all notation.** Codex doesn't know your paper. Spell out every variable, its domain, and its economic meaning. "where τ > 0 is the tax rate, x*(τ) is the equilibrium effort level, σ² > 0 is the noise variance, γ ∈ (0,1) is risk aversion."
3. **Say what's been tried and failed.** "Direct computation of V''(τ) via the chain rule produces a rational function whose sign depends on parameter ratios. The Hessian approach doesn't simplify because the implicit function has a non-separable second derivative."
4. **Ask for specific strategies.** "Try: (a) change of variables to make the composition separable, (b) show the composition of concave functions is concave under the monotonicity conditions that hold here, (c) find a counterexample in the region γ > 0.5, σ² < 1."
5. **Demand rigor.** "Prove every step. If you claim a function is concave, compute the second derivative and show it's negative. If you claim a counterexample, give specific parameter values and verify numerically. Do not hand-wave."

### Example: good vs. bad explore prompts

**Bad:** "Is the value function concave?"

**Good:** "Consider V(τ) = u(c*(τ)) - ψ·x*(τ)², where c*(τ) = f(x*(τ)) - τ·x*(τ) and x*(τ) solves the fixed point x = h(τ, x) with h(τ,x) = (1-τ)f'⁻¹(ψx/(1-τ)). All parameters strictly positive, f strictly concave with f(0)=0, f'(0)=∞, f'(∞)=0. Prove or disprove: V is strictly concave in τ on (0,1). If not globally concave, find the tightest sufficient condition. Approaches tried: direct Hessian (doesn't simplify due to implicit function composition), perturbation around τ=0 (works locally). Try: envelope theorem approach, monotone comparative statics, or counterexample search over standard CES production functions."

The difference: the good prompt gives Codex everything it needs to work independently — definitions, parameter domains, what's been tried, what to try next, and the standard of rigor expected.

### General rules for prompting Codex

- **Be explicit about rigor.** Say "prove every step" or "show all algebra." Codex will hand-wave if you let it.
- **Include parameter domains.** Codex needs to know whether parameters are positive, bounded, in (0,1), etc.
- **State the standard of proof.** "A valid proof must handle all boundary cases" or "a counterexample must give specific numerical parameter values."
- **Ask for multiple strategies when exploring.** Codex may fail with one approach but succeed with another.
- **Pipe content inline; do not have Codex read files itself.** On a properly configured host Codex *can* `cat` files in the workspace, but reading from inside the sandbox is fragile (depends on `bwrap` being functional — see Sandbox model below) and adds a tool call. The scripts already pre-extract content; for ad-hoc prompts, paste the content into the prompt yourself.

## Mode 1: Verify a proof

Check whether a proof is correct step by step.

```bash
# Basic usage — extract block by pattern, verify at medium effort
code/utils/codex_math/codex_verify.sh paper/sections/model.tex "Theorem 1"

# Hard proof — use high effort
code/utils/codex_math/codex_verify.sh paper/sections/model.tex "prop:concavity" high

# Custom output directory
code/utils/codex_math/codex_verify.sh paper/sections/model.tex "Lemma 3" high output/codex_audits
```

The script extracts the proposition + proof + referenced equations automatically. Result saved to `output/codex_audits/`.

**After running:** Read the output. For each FAIL finding, check whether it's a real error or a false positive. Report only confirmed errors.

## Mode 2: Write a proof

Ask Codex to write a complete proof of a stated result.

```bash
# From inline theorem statement
code/utils/codex_math/codex_write.sh "Prove: the equilibrium is unique for all parameter values satisfying Assumption 1" high

# From a file containing the theorem
code/utils/codex_math/codex_write.sh theorem_statement.tex high

# From specific lines of a file
code/utils/codex_math/codex_write.sh paper/model.tex:200-210 high
```

Result saved to `output/codex_proofs/`.

**After running:** Do not blindly paste the proof into the paper. Verify every step. Run Mode 1 (verify) on Codex's own proof. Codex may produce a proof that looks complete but has a subtle gap.

## Mode 3: Explore a conjecture

Investigate whether a claim is true, find conditions, construct counterexamples.

```bash
# Plain question
code/utils/codex_math/codex_explore.sh "Is V(τ) globally concave for all γ > 0, or can it have multiple local maxima?" high

# With context file (definitions, notation, setup)
code/utils/codex_math/codex_explore.sh "Under what conditions on risk aversion and noise variance is the equilibrium unique?" paper/model.tex high
```

Result saved to `output/codex_explorations/`.

**This is the most valuable mode for the pipeline.** When a proof attempt fails and you're unsure whether the result is even true, exploration can:
- Find a counterexample (→ characterize the boundary instead)
- Find a sufficient condition (→ prove under that condition)
- Suggest a proof strategy you haven't tried
- Confirm the result is likely true but hard to prove (→ try harder, or restrict the parameter space)

## Sandbox model

Codex with `--full-auto` runs in the `workspace-write` sandbox:

- **Shell + Python available.** `cat`, `grep`, `sed`, `python3` (including `sympy`) all work.
- **Read access everywhere** the user can read.
- **Write access only** in `workdir`, `/tmp`, `$TMPDIR`, and `~/.codex/memories`. Writes outside those zones fail with `Read-only file system`.

**Ubuntu 24.04 host gotcha.** The sandbox uses bubblewrap, which needs unprivileged user namespaces. Ubuntu 24.04's default AppArmor policy blocks this for unconfined binaries — every codex shell command then fails with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`. One-time fix:

```bash
sudo sysctl kernel.apparmor_restrict_unprivileged_userns=0
echo 'kernel.apparmor_restrict_unprivileged_userns = 0' | sudo tee /etc/sysctl.d/60-apparmor-namespace.conf
sudo sysctl --system
# sanity: bwrap --unshare-all --bind / / true && echo OK
```

**Our scripts don't depend on the sandbox shell.** They use `-o "$TMP"` so the Codex CLI (running outside the sandbox) captures the model's final message regardless, and they pre-extract file content via `extract_block.sh` rather than asking codex to `cat` files. So `codex_verify.sh`, `codex_write.sh`, and `codex_explore.sh` work identically whether or not bwrap can start. If you write ad-hoc codex prompts, you can rely on shell + python on a working host; on a broken one, pass content inline.

## Dual audit pattern

For maximum confidence on critical results, run Codex AND a Claude verification in parallel:

```bash
# Codex audit
code/utils/codex_math/codex_verify.sh paper/model.tex "Proposition 3" high

# Claude math-auditor (runs separately as an agent)
```

- Both PASS → high confidence
- Both FAIL on same step → real error
- Disagreement → investigate the specific step manually

## Runtime behavior and output capture

Hard proofs at `high` effort routinely run 1–5 minutes; do not assume a hang. The terminal shows a session header, then a short progress paragraph mid-thinking ("I'm thinking about..."), then the final answer streams once reasoning completes. Those middle paragraphs are the model summarizing its own reasoning — not the answer. Do not paste them into the paper.

**What gets saved to disk:** only the final answer (with a header prefix), in the directory below. Reasoning summaries appear in the terminal but are not captured.

**To capture the full session** (e.g., for debugging or to record what codex was thinking), pipe the script output through `tee`:

```bash
bash code/utils/codex_math/codex_verify.sh paper/sections/model.tex "Proposition 7" high 2>&1 | tee output/codex_logs/prop7.log
```

## Output locations

| Mode | Default output directory |
|------|------------------------|
| Verify | `output/codex_audits/` |
| Write | `output/codex_proofs/` |
| Explore | `output/codex_explorations/` |
