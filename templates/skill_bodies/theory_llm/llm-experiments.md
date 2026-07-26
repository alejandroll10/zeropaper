## Source
- UF NaviGator: https://api.ai.it.ufl.edu (free for UF researchers)
- DeepInfra: https://deepinfra.com (pay-per-token)
- Client: `llm_client.py` in project root

## How to use

```python
from llm_client import call, list_models

# Auto-detect backend (uses whichever key is in .env)
r = call(
    system="You are a careful reasoner. Answer with a single number.",
    user="A list contains the numbers 3, 41, 17, 8, 29. What is the median?",
    max_tokens=500,
)
print(r.content)       # response text
print(r.reasoning)     # reasoning tokens (if model supports it, else None)
print(r.model)         # model used
print(r.backend)       # "uf" or "deepinfra"
print(r.usage)         # token counts

# Specify a model (backend auto-detected from model name)
r = call(system="...", user="...", model="deepseek-ai/DeepSeek-R1")
r = call(system="...", user="...", model="moonshotai/Kimi-K2-Thinking")
r = call(system="...", user="...", model="gpt-oss-120b")

# Force a backend
r = call(system="...", user="...", backend="deepinfra", model="Qwen/QwQ-32B")

# UF-specific: set reasoning effort
r = call(system="...", user="...", model="gpt-oss-120b", reasoning_effort="high")

# List all available models
print(list_models())
```

## Available models

### Reasoning models (produce chain-of-thought)
| Model | Backend | Notes |
|-------|---------|-------|
| `gpt-oss-120b` | UF | Free. Supports `reasoning_effort` (low/medium/high) |
| `gpt-oss-20b` | UF | Free. Smaller, faster |
| `moonshotai/Kimi-K2-Thinking` | DeepInfra | SOTA reasoning. Reasoning in separate field |
| `deepseek-ai/DeepSeek-R1` | DeepInfra | Strong reasoning. Reasoning in `<think>` tags |
| `deepseek-ai/DeepSeek-R1-0528` | DeepInfra | Updated R1 |
| `Qwen/QwQ-32B` | DeepInfra | Efficient reasoning |

### Non-reasoning models (direct answers)
| Model | Backend | Notes |
|-------|---------|-------|
| `deepseek-ai/DeepSeek-V3.2` | DeepInfra | Frontier, GPT-5 class |
| `Qwen/Qwen3-235B-A22B` | DeepInfra | Large MoE |
| `meta-llama/Meta-Llama-3.1-405B-Instruct` | DeepInfra | Largest open Llama |
| `meta-llama/Meta-Llama-3.1-70B-Instruct` | DeepInfra | Good balance |
| `meta-llama/Meta-Llama-3.1-8B-Instruct` | DeepInfra | Fast, cheap |

## Credentials
In `.env`:
```
UF_API_KEY=your-key          # UF NaviGator
DEEPINFRA_TOKEN=your-key     # DeepInfra
```
Set one or both. The client auto-detects which is available.

## Experiment design tips
- **Reasoning vs non-reasoning:** Compare the same task across reasoning (QwQ, DeepSeek-R1) and non-reasoning (Llama-70B) models to test whether chain-of-thought changes the result.
- **Model size:** Compare 8B vs 70B vs 405B to test scaling predictions.
- **Ground truth:** Use tasks with known answers to measure error rates — procedurally generated (random instances of a solvable problem class), not textbook or public-benchmark items the models trained on.
- **Sample size:** Run 50+ stimuli per condition for headline contrasts (20-30 only for secondary probes).
- **Determinism vs variance:** Reserve `temperature=0` for determinism checks and exact reproduction; sample headline conditions at `temperature > 0` with multiple runs per stimulus so error bars capture run-to-run variance.

## Rules
- **Save all raw outputs.** Write responses to `output/stage3b/raw_results/` as JSON.
- **Log every call.** Record model, prompt, response, tokens, time — and the exact snapshot identifier the API returns (`r.model`), the decoding parameters, and the access date. A paper whose evidence is model calls must pin which snapshot the claims are about.
- **Set seeds where possible.** `temperature=0` is for determinism checks — headline error bars come from sampled runs.
