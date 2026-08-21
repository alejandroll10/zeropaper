"""
LLM client for theory_llm papers. Supports multiple backends:
  - UF NaviGator (gpt-oss models, free for UF researchers)
  - DeepInfra (Llama, Qwen, Gemma, etc.)
  - OpenAI (GPT-5.x frontier models — pay-per-token)
  - Anthropic (Claude frontier models — pay-per-token, native Messages API)
  - Local (Ollama, llama.cpp, LM Studio, vLLM — any OpenAI-compatible server)

Setup:
  1. pip install openai anthropic python-dotenv
  2. Create .env with one or more:
     UF_API_KEY=your-key         # https://api.ai.it.ufl.edu
     DEEPINFRA_TOKEN=your-key    # https://deepinfra.com
     OPENAI_API_KEY=your-key     # https://platform.openai.com/api-keys
     ANTHROPIC_API_KEY=your-key  # https://platform.claude.com/settings/keys
     LOCAL_LLM_BASE_URL=http://localhost:11434/v1   # optional; defaults to Ollama
     LOCAL_LLM_MODEL=llama3.1:8b                    # required for local backend (any tag you pulled)
     LOCAL_LLM_API_KEY=ollama                       # optional; most local servers ignore it

Decoding-parameter honesty: frontier reasoning models reject or ignore some
sampling knobs (OpenAI gpt-5.x / o-series reject `temperature`; Claude 4.6+
except Opus/Sonnet 4.6 reject `temperature`; Claude 4.6+ use adaptive thinking
with an `effort` level instead of a token budget). `call()` sends only what the
target model accepts and records exactly what it sent in
`LLMResponse.request_params` — log that alongside `LLMResponse.model` so the
paper's decoding disclosure is provable, not inferred.
"""

import os
import re
import time
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ── Backend configuration ──
BACKENDS = {
    "uf": {
        "base_url": "https://api.ai.it.ufl.edu/v1",
        "api_key_env": "UF_API_KEY",
        "default_model": "gpt-oss-120b",
        "models": ["gpt-oss-120b", "gpt-oss-20b"],
    },
    "deepinfra": {
        # Catalog checked against GET /v1/openai/models on 2026-08-21; DeepInfra
        # retires snapshots, so re-check before a long run. `reasoning_effort`
        # is forwarded (extra_body) — it is what switches DeepSeek V4 / gpt-oss
        # into thinking mode; models without the knob accept and ignore it.
        "base_url": "https://api.deepinfra.com/v1/openai",
        "api_key_env": "DEEPINFRA_TOKEN",
        "default_model": "deepseek-ai/DeepSeek-V4-Flash-0731",
        "models": [
            # Reasoning / hybrid-thinking models
            "deepseek-ai/DeepSeek-V4-Flash-0731",
            "deepseek-ai/DeepSeek-V4-Pro-0813",
            "deepseek-ai/DeepSeek-R1-0528",
            "moonshotai/Kimi-K3",
            "Qwen/Qwen3-Max-Thinking",
            "zai-org/GLM-5.2",
            # Large instruction / frontier-class open weights
            "deepseek-ai/DeepSeek-V3.2",
            "Qwen/Qwen3.8-Max",
            "Qwen/Qwen3.5-397B-A17B",
            "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            # gpt-oss on DeepInfra (org-prefixed, unlike the bare UF ids)
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            # Smaller / cheaper
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "google/gemma-3-27b-it",
            "Qwen/Qwen3.6-27B",
        ],
    },
    "openai": {
        # OpenAI first-party API (Chat Completions). Pay-per-token.
        # Model IDs and prices as of 2026-08: gpt-5.6-sol ($4/$20 per MTok in/out),
        # gpt-5.6-terra ($2/$12), gpt-5.6-luna ($0.20/$1.20). Every gpt-5.x / o-series
        # model is a reasoning model: `temperature` is rejected, `reasoning_effort`
        # takes none|minimal|low|medium|high|xhigh|max (per-model subset), and the
        # output cap is `max_completion_tokens`.
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "default_model": "gpt-5.6-sol",
        "models": [
            "gpt-5.6-sol",
            "gpt-5.6-terra",
            "gpt-5.6-luna",
            "gpt-5.5",
            "gpt-5.4",
        ],
    },
    "anthropic": {
        # Anthropic first-party Messages API via the `anthropic` SDK (NOT the
        # OpenAI-compatibility shim — that layer drops thinking/effort control and
        # is documented as a migration aid, not a production surface). Pay-per-token.
        # Model IDs and prices as of 2026-08: claude-opus-5 ($5/$25 per MTok in/out),
        # claude-sonnet-5 ($2/$10 intro, $3/$15 list), claude-haiku-4-5 ($1/$5),
        # claude-fable-5 ($10/$50; requires 30-day data retention on the org).
        "base_url": None,  # native SDK; not an OpenAI-compatible endpoint
        "api_key_env": "ANTHROPIC_API_KEY",
        "default_model": "claude-opus-5",
        "models": [
            "claude-opus-5",
            "claude-sonnet-5",
            "claude-fable-5",
            "claude-haiku-4-5",
            "claude-opus-4-8",
            "claude-sonnet-4-6",
        ],
    },
    "local": {
        # Any OpenAI-compatible local server: Ollama, LM Studio, llama.cpp, vLLM, etc.
        # base_url + default_model are overridable via env vars (resolved in get_client).
        "base_url": "http://localhost:11434/v1",  # Ollama default; override with LOCAL_LLM_BASE_URL
        "api_key_env": "LOCAL_LLM_API_KEY",       # most local servers ignore the key
        "default_model": None,                    # must be set via LOCAL_LLM_MODEL or model= arg
        # Models on a local server are whatever you've pulled — this list is purely illustrative.
        "models": [],
    },
}

# Cloud backends are tried in this order when no model is given and `backend`
# is not forced. Free (UF) → cheap open-weights (DeepInfra) → frontier paid
# (OpenAI, Anthropic) → local. Local loses to any configured cloud key.
_FALLBACK_ORDER = ["uf", "deepinfra", "openai", "anthropic", "local"]

# OpenAI reasoning families (reject `temperature`, take `reasoning_effort`).
_OPENAI_REASONING_RE = re.compile(r"^(gpt-5|o\d)")

# Claude models that predate adaptive thinking (Claude 4.5 and earlier, incl.
# Haiku 4.5 and the dated Opus/Sonnet 4 snapshots). This set is closed — every
# model released after it takes the adaptive-thinking + effort path — so an
# unrecognized `claude-*` id defaults to the modern rules.
_ANTHROPIC_LEGACY_RE = re.compile(
    r"^claude-(3|.*-4-5|opus-4-1|opus-4-2|sonnet-4-2|opus-4$|sonnet-4$)"
)
# Claude 4.6 models: adaptive thinking AND sampling parameters both accepted;
# effort tops out at "max" (no "xhigh" — that level arrived with Opus 4.7).
_ANTHROPIC_SAMPLING_OK_RE = re.compile(r"^claude-(opus|sonnet)-4-6")

_ANTHROPIC_EFFORT_MAP = {
    "none": "low", "minimal": "low",
    "low": "low", "medium": "medium", "high": "high", "xhigh": "xhigh", "max": "max",
}


@dataclass
class LLMResponse:
    content: Optional[str]
    reasoning: Optional[str]
    model: str
    backend: str
    usage: dict = field(default_factory=dict)
    elapsed: float = 0.0
    # Why generation stopped, in the provider's own vocabulary ("stop", "length",
    # "end_turn", "max_tokens", "refusal", ...). Record it: a truncated or refused
    # answer scored as "wrong" is a measurement error, not a model error.
    finish_reason: Optional[str] = None
    # Decoding parameters actually sent (after per-model gating) — log verbatim.
    request_params: dict = field(default_factory=dict)


def _detect_backend(model: Optional[str] = None) -> str:
    """Auto-detect which backend to use based on model name or available keys.

    Routing priority (when `model` is given):
      1. Exact match against any backend's `models` list or `default_model`
      2. "claude-*"                → anthropic
      3. "gpt-oss*"                → UF (free; OpenAI does not host gpt-oss)
      4. "gpt-*", "o<digit>*", "chatgpt-*" → openai
      5. "/" in name → DeepInfra (org/model format)
      6. ":" in name → local (Ollama-style "name:tag")
    Note: a name with both "/" and ":" (e.g. "registry/org/model:tag") routes to
    DeepInfra; pass `backend="local"` explicitly to override.

    Fallback priority (when `model` is None): UF → DeepInfra → OpenAI → Anthropic → local.
    Cloud backends win if both a cloud key and LOCAL_LLM_* are set; force the
    local backend with `backend="local"` if you want it.
    """
    if model:
        for name, cfg in BACKENDS.items():
            if model in cfg["models"] or model == cfg["default_model"]:
                return name
        if model.startswith("claude-"):
            return "anthropic"
        if model.startswith("gpt-oss"):
            return "uf"
        if re.match(r"^(gpt-|o\d|chatgpt-)", model):
            return "openai"
        if "/" in model:
            return "deepinfra"
        if ":" in model:
            return "local"

    for name in _FALLBACK_ORDER:
        if name == "local":
            if os.getenv("LOCAL_LLM_BASE_URL") or os.getenv("LOCAL_LLM_MODEL"):
                return "local"
        elif os.getenv(BACKENDS[name]["api_key_env"]):
            return name

    raise ValueError(
        "No LLM backend configured. Set UF_API_KEY, DEEPINFRA_TOKEN, OPENAI_API_KEY, "
        "ANTHROPIC_API_KEY, or LOCAL_LLM_BASE_URL/LOCAL_LLM_MODEL in .env"
    )


def get_client(backend: Optional[str] = None, model: Optional[str] = None):
    """Get a client for the specified or auto-detected backend.

    Returns:
        (client, backend_name) — an `openai.OpenAI` client for every backend
        except "anthropic", which returns an `anthropic.Anthropic` client.
    """
    if backend is None:
        backend = _detect_backend(model)

    cfg = BACKENDS[backend]

    if backend == "local":
        # Local servers usually don't authenticate; allow override but default to a placeholder.
        base_url = os.getenv("LOCAL_LLM_BASE_URL", cfg["base_url"])
        api_key = os.getenv(cfg["api_key_env"], "ollama")
    else:
        base_url = cfg["base_url"]
        api_key = os.getenv(cfg["api_key_env"])
        if not api_key:
            raise ValueError(f"Missing {cfg['api_key_env']} in .env for backend '{backend}'")

    if backend == "anthropic":
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover - exercised only on a broken venv
            raise ImportError(
                "The anthropic backend needs the `anthropic` package: pip install anthropic"
            ) from e
        # Frontier Claude turns can run for minutes at high effort; 10 min is the SDK default.
        client = anthropic.Anthropic(api_key=api_key, timeout=600.0)
        return client, backend

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=300.0,
    )
    return client, backend


# ── Per-backend request construction (pure functions; unit-tested without network) ──

def _chat_request_kwargs(
    backend: str, model: str, system: str, user: str,
    max_tokens: int, temperature: float, reasoning_effort: str,
) -> dict:
    """Chat Completions kwargs for the OpenAI-compatible backends (uf, deepinfra, openai, local)."""
    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    if backend == "openai":
        # `max_tokens` is deprecated on the first-party API; reasoning models reject it.
        kwargs["max_completion_tokens"] = max_tokens
        if _OPENAI_REASONING_RE.match(model):
            kwargs["reasoning_effort"] = reasoning_effort
            # gpt-5.x / o-series reject non-default temperature. With reasoning
            # disabled ("none") the knob is live again — send it and let the
            # 400-retry below drop it if this snapshot disagrees.
            if reasoning_effort == "none":
                kwargs["temperature"] = temperature
        else:
            kwargs["temperature"] = temperature
        return kwargs

    kwargs["max_tokens"] = max_tokens
    kwargs["temperature"] = temperature
    # UF gpt-oss and DeepInfra (DeepSeek V4 / gpt-oss thinking toggle) take
    # reasoning_effort; local servers vary, so it is not forwarded there.
    if backend in ("uf", "deepinfra"):
        kwargs["extra_body"] = {"reasoning_effort": reasoning_effort}
    return kwargs


def _anthropic_request_kwargs(
    model: str, system: str, user: str,
    max_tokens: int, temperature: float, reasoning_effort: str,
) -> dict:
    """Messages API kwargs for the anthropic backend."""
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    if _ANTHROPIC_LEGACY_RE.match(model):
        # Claude ≤4.5: no adaptive thinking / effort; sampling parameters accepted.
        # Thinking is left off (a `budget_tokens` run would need max_tokens > 1024
        # headroom); pass `backend="anthropic"` with a 4.6+ model for reasoning traces.
        kwargs["temperature"] = temperature
        return kwargs
    # Claude 4.6+: adaptive thinking with an effort level; `display: "summarized"`
    # returns a readable reasoning summary (the default on 4.7+ is an empty string).
    kwargs["thinking"] = {"type": "adaptive", "display": "summarized"}
    effort = _ANTHROPIC_EFFORT_MAP.get(reasoning_effort, "medium")
    if _ANTHROPIC_SAMPLING_OK_RE.match(model):
        kwargs["temperature"] = temperature
        if effort == "xhigh":
            effort = "high"  # 4.6 family has no xhigh level
    kwargs["output_config"] = {"effort": effort}
    return kwargs


def _request_params_record(kwargs: dict) -> dict:
    """The decoding-relevant subset of a request, for LLMResponse.request_params."""
    rec = {"temperature": kwargs.get("temperature")}
    for key in ("max_tokens", "max_completion_tokens", "reasoning_effort", "thinking", "output_config"):
        if key in kwargs:
            rec[key] = kwargs[key]
    if "extra_body" in kwargs:
        rec.update(kwargs["extra_body"])
    return rec


def _create_with_temperature_fallback(create, kwargs: dict, bad_request_types: tuple):
    """Call `create(**kwargs)`; if the provider rejects `temperature` (400 naming it), retry without.

    Returns (response, kwargs_actually_sent). Keeps the model-gating above from
    having to be perfect for every future snapshot: a dropped knob is recorded in
    request_params rather than silently assumed.
    """
    try:
        return create(**kwargs), kwargs
    except bad_request_types as e:
        if "temperature" in kwargs and "temperature" in str(e).lower():
            retry = {k: v for k, v in kwargs.items() if k != "temperature"}
            return create(**retry), retry
        raise


def _call_anthropic(client, kwargs: dict) -> LLMResponse:
    import anthropic

    t0 = time.time()
    response, sent = _create_with_temperature_fallback(
        client.messages.create, kwargs, (anthropic.BadRequestError,)
    )
    elapsed = time.time() - t0

    text_parts, thinking_parts = [], []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
        elif block.type == "thinking" and getattr(block, "thinking", ""):
            thinking_parts.append(block.thinking)
    content = "".join(text_parts)
    reasoning = "\n".join(thinking_parts) or None

    params = _request_params_record(sent)
    stop_details = getattr(response, "stop_details", None)
    if response.stop_reason == "refusal" and stop_details is not None:
        # Safety-classifier refusal (HTTP 200). Surface the category so a refused
        # stimulus is scored as "refused", never as a wrong answer.
        params["refusal"] = {
            "category": getattr(stop_details, "category", None),
            "explanation": getattr(stop_details, "explanation", None),
        }

    usage = response.usage
    return LLMResponse(
        content=content,
        reasoning=reasoning,
        model=response.model,
        backend="anthropic",
        usage={
            "prompt_tokens": usage.input_tokens,
            "completion_tokens": usage.output_tokens,
            "total_tokens": usage.input_tokens + usage.output_tokens,
        },
        elapsed=elapsed,
        finish_reason=response.stop_reason,
        request_params=params,
    )


def _call_chat(client, backend_name: str, kwargs: dict) -> LLMResponse:
    import openai

    t0 = time.time()
    completion, sent = _create_with_temperature_fallback(
        client.chat.completions.create, kwargs, (openai.BadRequestError,)
    )
    elapsed = time.time() - t0

    choice = completion.choices[0]
    msg = choice.message
    content = msg.content
    reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None)

    # Reasoning models can return content="" (Ollama) or None (DeepInfra) — fall back to reasoning.
    if not content:
        msg_dict = msg.model_dump() if hasattr(msg, "model_dump") else {}
        content = (
            msg_dict.get("reasoning_content")
            or msg_dict.get("reasoning")
            or reasoning
            or ""
        )

    usage = {
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens": completion.usage.total_tokens,
    }
    # OpenAI reasoning models do not return their chain of thought over Chat
    # Completions, but they do bill it — keep the count so cost/length analyses
    # can separate visible from hidden output.
    details = getattr(completion.usage, "completion_tokens_details", None)
    reasoning_tokens = getattr(details, "reasoning_tokens", None) if details else None
    if reasoning_tokens is not None:
        usage["reasoning_tokens"] = reasoning_tokens

    return LLMResponse(
        content=content,
        reasoning=reasoning,
        model=completion.model,
        backend=backend_name,
        usage=usage,
        elapsed=elapsed,
        finish_reason=getattr(choice, "finish_reason", None),
        request_params=_request_params_record(sent),
    )


def call(
    system: str,
    user: str,
    model: Optional[str] = None,
    backend: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    reasoning_effort: str = "medium",
) -> LLMResponse:
    """Call an LLM via the appropriate backend. Returns content and reasoning separately.

    Args:
        system: System prompt
        user: User message
        model: Model name (auto-detects backend if not specified)
        backend: Force a specific backend ("uf", "deepinfra", "openai", "anthropic", or "local")
        max_tokens: Maximum response tokens (includes reasoning tokens on OpenAI/Anthropic
            reasoning models — size it for the thinking, not just the visible answer)
        temperature: Sampling temperature. Sent only where the model accepts it
            (dropped for OpenAI gpt-5.x/o-series unless reasoning_effort="none", and for
            Claude 4.6+ other than Opus/Sonnet 4.6); check `LLMResponse.request_params`.
        reasoning_effort: "low", "medium", "high" everywhere it applies (UF gpt-oss;
            DeepInfra — toggles thinking on DeepSeek V4 / gpt-oss, ignored by models
            without the knob; OpenAI also takes "none"/"minimal"/"xhigh"/"max" per model;
            Anthropic maps it to `output_config.effort`, with "none"/"minimal" → "low").
            Not forwarded to local servers.
    """
    client, backend_name = get_client(backend, model)

    if model is None:
        if backend_name == "local":
            model = os.getenv("LOCAL_LLM_MODEL") or BACKENDS["local"]["default_model"]
            if not model:
                raise ValueError(
                    "Local backend requires a model. Pass model=... or set LOCAL_LLM_MODEL "
                    "in .env (e.g. 'llama3.1:8b', 'gemma3:27b', 'qwen2.5:32b' for Ollama)."
                )
        else:
            model = BACKENDS[backend_name]["default_model"]

    if backend_name == "anthropic":
        kwargs = _anthropic_request_kwargs(model, system, user, max_tokens, temperature, reasoning_effort)
        return _call_anthropic(client, kwargs)

    kwargs = _chat_request_kwargs(backend_name, model, system, user, max_tokens, temperature, reasoning_effort)
    return _call_chat(client, backend_name, kwargs)


def list_models(backend: Optional[str] = None) -> dict:
    """List available models per backend."""
    if backend:
        return {backend: BACKENDS[backend]["models"]}
    return {name: cfg["models"] for name, cfg in BACKENDS.items()}


if __name__ == "__main__":
    import sys

    # Auto-detect or use CLI arg
    backend = sys.argv[1] if len(sys.argv) > 1 else None

    try:
        client, detected = get_client(backend)
        if detected == "local":
            model = os.getenv("LOCAL_LLM_MODEL") or BACKENDS["local"]["default_model"]
            if not model:
                raise ValueError(
                    "Local backend requires a model. Set LOCAL_LLM_MODEL in .env."
                )
        else:
            model = BACKENDS[detected]["default_model"]
        print(f"Testing {detected} backend with {model}...")

        r = call(
            system="You are a helpful assistant.",
            user="Say 'Hello!' and name the model you are.",
            model=model,
            backend=detected,
            max_tokens=2000,
            reasoning_effort="low",
        )
        print(f"Backend: {r.backend}")
        print(f"Model: {r.model}")
        print(f"Content: {r.content}")
        if r.reasoning:
            print(f"Reasoning: {r.reasoning[:200]}")
        print(f"Usage: {r.usage}")
        print(f"Finish: {r.finish_reason}")
        print(f"Params: {r.request_params}")
        print(f"Time: {r.elapsed:.1f}s")
    except ValueError as e:
        print(f"Error: {e}")
        print("Available backends:", list(BACKENDS.keys()))
