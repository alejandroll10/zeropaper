"""
LLM client for theory_llm papers. Supports multiple backends:
  - UF NaviGator (gpt-oss models, free for UF researchers)
  - DeepInfra (Llama, Qwen, Gemma, etc.)
  - Local (Ollama, llama.cpp, LM Studio, vLLM — any OpenAI-compatible server)

Setup:
  1. pip install openai python-dotenv
  2. Create .env with one or more:
     UF_API_KEY=your-key       # https://api.ai.it.ufl.edu
     DEEPINFRA_TOKEN=your-key  # https://deepinfra.com
     LOCAL_LLM_BASE_URL=http://localhost:11434/v1   # optional; defaults to Ollama
     LOCAL_LLM_MODEL=llama3.1:8b                    # required for local backend (any tag you pulled)
     LOCAL_LLM_API_KEY=ollama                       # optional; most local servers ignore it
"""

import os
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
        "base_url": "https://api.deepinfra.com/v1/openai",
        "api_key_env": "DEEPINFRA_TOKEN",
        "default_model": "Qwen/QwQ-32B",
        "models": [
            # Reasoning models
            "Qwen/QwQ-32B",
            "deepseek-ai/DeepSeek-R1",
            "deepseek-ai/DeepSeek-R1-0528",
            "moonshotai/Kimi-K2-Thinking",
            # Large instruction / frontier
            "deepseek-ai/DeepSeek-V3.2",
            "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
            "meta-llama/Meta-Llama-3.1-405B-Instruct",
            "meta-llama/Meta-Llama-3.1-70B-Instruct",
            "Qwen/Qwen3-235B-A22B",
            "Qwen/Qwen2.5-72B-Instruct",
            # Also available: gpt-oss-120B on DeepInfra
            "gpt-oss-120B",
            # Smaller / cheaper
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "google/gemma-2-27b-it",
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


@dataclass
class LLMResponse:
    content: Optional[str]
    reasoning: Optional[str]
    model: str
    backend: str
    usage: dict = field(default_factory=dict)
    elapsed: float = 0.0


def _detect_backend(model: Optional[str] = None) -> str:
    """Auto-detect which backend to use based on model name or available keys.

    Routing priority (when `model` is given):
      1. Exact match against any backend's `models` list or `default_model`
      2. "/" in name → DeepInfra (org/model format)
      3. ":" in name → local (Ollama-style "name:tag")
    Note: a name with both "/" and ":" (e.g. "registry/org/model:tag") routes to
    DeepInfra; pass `backend="local"` explicitly to override.

    Fallback priority (when `model` is None): UF → DeepInfra → local.
    Cloud backends win if both a cloud key and LOCAL_LLM_* are set; force the
    local backend with `backend="local"` if you want it.
    """
    if model:
        for name, cfg in BACKENDS.items():
            if model in cfg["models"] or model == cfg["default_model"]:
                return name
        if "/" in model:
            return "deepinfra"
        if ":" in model:
            return "local"

    if os.getenv("UF_API_KEY"):
        return "uf"
    if os.getenv("DEEPINFRA_TOKEN"):
        return "deepinfra"
    if os.getenv("LOCAL_LLM_BASE_URL") or os.getenv("LOCAL_LLM_MODEL"):
        return "local"

    raise ValueError(
        "No LLM backend configured. Set UF_API_KEY, DEEPINFRA_TOKEN, "
        "or LOCAL_LLM_BASE_URL/LOCAL_LLM_MODEL in .env"
    )


def get_client(backend: Optional[str] = None, model: Optional[str] = None) -> tuple[OpenAI, str]:
    """Get an OpenAI-compatible client for the specified or auto-detected backend.

    Returns:
        (client, backend_name)
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

    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        timeout=300.0,
    )
    return client, backend


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
        backend: Force a specific backend ("uf", "deepinfra", or "local")
        max_tokens: Maximum response tokens
        temperature: Sampling temperature
        reasoning_effort: "low", "medium", "high" (UF gpt-oss only)
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

    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    # UF gpt-oss supports reasoning_effort
    if backend_name == "uf":
        kwargs["extra_body"] = {"reasoning_effort": reasoning_effort}

    t0 = time.time()
    completion = client.chat.completions.create(**kwargs)
    elapsed = time.time() - t0

    msg = completion.choices[0].message
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

    return LLMResponse(
        content=content,
        reasoning=reasoning,
        model=completion.model,
        backend=backend_name,
        usage={
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens,
        },
        elapsed=elapsed,
    )


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
            max_tokens=100,
            reasoning_effort="low",
        )
        print(f"Backend: {r.backend}")
        print(f"Model: {r.model}")
        print(f"Content: {r.content}")
        if r.reasoning:
            print(f"Reasoning: {r.reasoning[:200]}")
        print(f"Usage: {r.usage}")
        print(f"Time: {r.elapsed:.1f}s")
    except ValueError as e:
        print(f"Error: {e}")
        print("Available backends:", list(BACKENDS.keys()))
