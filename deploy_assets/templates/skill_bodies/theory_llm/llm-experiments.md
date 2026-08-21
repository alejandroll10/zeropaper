## Source
- UF NaviGator: https://api.ai.it.ufl.edu (free for UF researchers)
- DeepInfra: https://deepinfra.com (pay-per-token, open-weight families)
- OpenAI: https://platform.openai.com (pay-per-token, GPT-5.x frontier tier)
- Anthropic: https://platform.claude.com (pay-per-token, Claude frontier tier — native Messages API)
- Local: any OpenAI-compatible server (Ollama, LM Studio, vLLM) — no key
- Client: `llm_client.py` in project root

## How to use

```python
from llm_client import call, list_models

# Auto-detect backend (uses whichever key is in .env: UF → DeepInfra → OpenAI → Anthropic → local)
r = call(
    system="You are a careful reasoner. Answer with a single number.",
    user="A list contains the numbers 3, 41, 17, 8, 29. What is the median?",
    max_tokens=500,
)
print(r.content)         # response text
print(r.reasoning)       # reasoning tokens / thinking summary (if the model exposes it, else None)
print(r.model)           # exact model snapshot the API returned — pin this in the paper
print(r.backend)         # "uf", "deepinfra", "openai", "anthropic", or "local"
print(r.usage)           # token counts (OpenAI reasoning models add hidden "reasoning_tokens")
print(r.finish_reason)   # "stop"/"end_turn" normal; "length"/"max_tokens" truncated; "refusal" (Claude)
print(r.request_params)  # decoding parameters ACTUALLY sent after per-model gating — log verbatim

# Specify a model (backend auto-detected from model name)
r = call(system="...", user="...", model="moonshotai/Kimi-K3")           # "/" → DeepInfra
r = call(system="...", user="...", model="gpt-oss-120b")                  # gpt-oss* → UF
r = call(system="...", user="...", model="gpt-5.6-sol")                   # gpt-*/o* → OpenAI
r = call(system="...", user="...", model="claude-opus-5")                 # claude-* → Anthropic
r = call(system="...", user="...", model="llama3.1:8b")                   # "name:tag" → local

# Force a backend
r = call(system="...", user="...", backend="deepinfra", model="deepseek-ai/DeepSeek-V4-Pro-0813")

# Reasoning effort: UF gpt-oss and DeepInfra (low/medium/high — on DeepInfra it is the DeepSeek V4 thinking
# toggle); OpenAI gpt-5.x (none/minimal/low/medium/high/xhigh/max, per-model subset); Anthropic Claude 4.6+
# (mapped to output_config.effort; none/minimal → low). Not forwarded to local servers.
r = call(system="...", user="...", model="gpt-oss-120b", reasoning_effort="high")

# List the catalog baked into the client (DeepInfra retires snapshot IDs — verify against
# GET https://api.deepinfra.com/v1/openai/models before a long run)
print(list_models())
```

## Available models

### Reasoning models (produce chain-of-thought)
| Model | Backend | Notes |
|-------|---------|-------|
| `gpt-oss-120b` | UF | Free. Supports `reasoning_effort` (low/medium/high) |
| `gpt-oss-20b` | UF | Free. Smaller, faster |
| `deepseek-ai/DeepSeek-V4-Flash-0731` | DeepInfra | Default DeepInfra model. Hybrid: thinking is ON only when `reasoning_effort` is forwarded (the client always forwards it); reasoning in a separate field |
| `deepseek-ai/DeepSeek-V4-Pro-0813` | DeepInfra | Larger V4; same thinking toggle |
| `deepseek-ai/DeepSeek-R1-0528` | DeepInfra | Classic R1. Reasoning in `<think>` tags |
| `moonshotai/Kimi-K3` | DeepInfra | Always-on reasoning in a separate field |
| `Qwen/Qwen3-Max-Thinking`, `zai-org/GLM-5.2` | DeepInfra | Reasoning models; the trace is not returned over the API |
| `openai/gpt-oss-120b` / `openai/gpt-oss-20b` | DeepInfra | Same weights as UF's, paid — useful when UF is down |
| `gpt-5.6-sol` / `gpt-5.6-terra` / `gpt-5.6-luna` | OpenAI | Frontier tier ($4/$20, $2/$12, $0.20/$1.20 per MTok in/out as of 2026-08). Chain of thought is hidden; only `usage["reasoning_tokens"]` is returned. `temperature` is rejected unless `reasoning_effort="none"` |
| `gpt-5.5`, `gpt-5.4` | OpenAI | Previous frontier snapshots |
| `claude-opus-5` / `claude-sonnet-5` / `claude-fable-5` | Anthropic | Frontier tier ($5/$25, $2/$10, $10/$50 per MTok as of 2026-08). Adaptive thinking; `r.reasoning` is a thinking *summary*. `temperature` is rejected (not sent). Fable 5 needs 30-day data retention on the org |
| `claude-opus-4-8` | Anthropic | Previous Opus; same rules as Opus 5 (`temperature` rejected, effort low…max) |
| `claude-sonnet-4-6`, `claude-opus-4-6` | Anthropic | The 4.6 family is the one modern exception that still accepts `temperature`; effort tops out at `max` (the client caps `xhigh` → `high`) |

### Non-reasoning models (direct answers)
| Model | Backend | Notes |
|-------|---------|-------|
| `deepseek-ai/DeepSeek-V3.2` | DeepInfra | Frontier-class open weights |
| `Qwen/Qwen3.8-Max`, `Qwen/Qwen3.5-397B-A17B` | DeepInfra | Large MoE |
| `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | DeepInfra | Llama 4 MoE |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | DeepInfra | Good balance |
| `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`, `google/gemma-3-27b-it`, `Qwen/Qwen3.6-27B` | DeepInfra | Fast, cheap |
| `claude-haiku-4-5` | Anthropic | Cheap frontier-lab small model ($1/$5). No adaptive thinking; accepts `temperature` |

## Credentials
In `.env`:
```
UF_API_KEY=your-key          # UF NaviGator (free)
DEEPINFRA_TOKEN=your-key     # DeepInfra
OPENAI_API_KEY=your-key      # OpenAI GPT-5.x
ANTHROPIC_API_KEY=your-key   # Anthropic Claude
LOCAL_LLM_MODEL=llama3.1:8b  # local server (optional LOCAL_LLM_BASE_URL, LOCAL_LLM_API_KEY)
```
Set any subset. The client auto-detects which is available; in the run plan, declare only the `provider_credentials` the declared experiment actually uses.

## Experiment design tips
- **Reasoning vs non-reasoning:** Compare the same task across reasoning (DeepSeek V4, Kimi K3, gpt-5.x, Claude 4.6+) and non-reasoning (Llama-70B, Haiku 4.5) models to test whether chain-of-thought changes the result.
- **Model size:** Compare 8B vs 70B vs 405B to test scaling predictions.
- **Cross-family replication:** Replicate the headline contrast on a second family. Open-weight families via DeepInfra are the cheap default; the frontier tiers (GPT-5.x, Claude) are the families readers care most about — size that replication to the headline contrast, not the whole battery, and write the expected token spend into the design document first. Within-vendor tier contrasts (`gpt-5.6-luna` vs `-sol`, `claude-haiku-4-5` vs `claude-opus-5`) are cheap scale probes.
- **Ground truth:** Use tasks with known answers to measure error rates — procedurally generated (random instances of a solvable problem class), not textbook or public-benchmark items the models trained on.
- **Sample size:** Run 50+ stimuli per condition for headline contrasts (20-30 only for secondary probes).
- **Determinism vs variance:** Reserve `temperature=0` for determinism checks and exact reproduction; sample headline conditions at `temperature > 0` with multiple runs per stimulus so error bars capture run-to-run variance. Frontier reasoning models do not expose `temperature` at all (gpt-5.x unless `reasoning_effort="none"`; Claude 4.7+ and Claude 5 — the 4.6 family is the exception) — for those, run-to-run variance comes from repeated sampled calls, and the paper must say the knob was unavailable, not that it was 0.7. Read `r.request_params` to know which it was.
- **Size `max_tokens` for the thinking:** on OpenAI and Anthropic reasoning models the cap covers reasoning + visible output; a `finish_reason` of `length`/`max_tokens` means the answer was cut off — score it as truncated, not wrong.

## Rules
- **Save all raw outputs.** Write responses as JSON beneath the fresh attempt-specific artifact paths supplied by the launch, and declare every path in the run plan and result bundle. Never write a retry into the first attempt's `output/stage3b/raw_results/` namespace.
- **Log every call.** Record model, prompt, response, tokens, time — and the exact snapshot identifier the API returns (`r.model`), the decoding parameters as sent (`r.request_params`), the `finish_reason`, and the access date. A paper whose evidence is model calls must pin which snapshot the claims are about.
- **Set seeds where possible.** `temperature=0` is for determinism checks — headline error bars come from sampled runs.
- **Refusals are data, not errors.** A Claude `finish_reason == "refusal"` (category in `r.request_params["refusal"]`) or an empty answer is a distinct outcome class; never fold it into "incorrect".
