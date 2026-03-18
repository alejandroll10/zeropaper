"""
LLM client for theory_llm papers. Calls UF NaviGator gpt-oss models.

Setup:
  1. pip install openai python-dotenv (or: uv add openai python-dotenv)
  2. Create .env with: UF_API_KEY=your-key-here
  3. Get key from https://api.ai.it.ufl.edu
"""

import os
import time
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = "https://api.ai.it.ufl.edu/v1"
DEFAULT_MODEL = "gpt-oss-120b"


@dataclass
class LLMResponse:
    content: Optional[str]
    reasoning: Optional[str]
    model: str
    usage: dict = field(default_factory=dict)
    elapsed: float = 0.0


def get_client() -> OpenAI:
    return OpenAI(
        base_url=BASE_URL,
        api_key=os.getenv("UF_API_KEY") or os.getenv("OPENAI_API_KEY"),
        timeout=300.0,
    )


def call(
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    reasoning_effort: str = "medium",
) -> LLMResponse:
    """Call gpt-oss via UF API. Returns content and reasoning separately."""
    client = get_client()

    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "extra_body": {"reasoning_effort": reasoning_effort},
    }

    t0 = time.time()
    completion = client.chat.completions.create(**kwargs)
    elapsed = time.time() - t0

    msg = completion.choices[0].message
    content = msg.content
    reasoning = getattr(msg, "reasoning_content", None) or getattr(msg, "reasoning", None)

    # content can be None for reasoning models — fall back
    if content is None:
        msg_dict = msg.model_dump() if hasattr(msg, "model_dump") else {}
        content = msg_dict.get("reasoning_content", "")

    return LLMResponse(
        content=content,
        reasoning=reasoning,
        model=completion.model,
        usage={
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens,
        },
        elapsed=elapsed,
    )


if __name__ == "__main__":
    print("Testing UF NaviGator connection...")
    r = call(
        system="You are a helpful assistant.",
        user="Say 'Hello from gpt-oss-120b!' and nothing else.",
        max_tokens=50,
        reasoning_effort="low",
    )
    print(f"Model: {r.model}")
    print(f"Content: {r.content}")
    print(f"Reasoning: {r.reasoning[:200] if r.reasoning else None}")
    print(f"Usage: {r.usage}")
    print(f"Time: {r.elapsed:.1f}s")
