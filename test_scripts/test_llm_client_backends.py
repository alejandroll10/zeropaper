"""Backend resolution and request construction for the theory_llm `llm_client.py`.

Two layers:
  * Offline (always runs): model-name → backend routing, key-based fallback order,
    and the per-backend request kwargs (which decoding knobs are sent to which
    model). No network, no keys.
  * Live canary (opt-in): set `LLM_CLIENT_LIVE=1` and the provider key(s); each
    configured frontier provider gets one tiny call. Skipped otherwise.

Run: python -m unittest -v test_scripts.test_llm_client_backends
"""

import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
CLIENT_DIR = REPO / "deploy_assets" / "extensions" / "theory_llm"

_ALL_KEYS = (
    "UF_API_KEY", "DEEPINFRA_TOKEN", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    "LOCAL_LLM_API_KEY", "LOCAL_LLM_BASE_URL", "LOCAL_LLM_MODEL",
)


def _load_client():
    if str(CLIENT_DIR) not in sys.path:
        sys.path.insert(0, str(CLIENT_DIR))
    # Import under a clean env so load_dotenv() cannot pull the dev checkout's
    # real keys into the fallback-order tests (dotenv never overrides a set
    # variable, so pre-setting every key to "" pins them).
    with mock.patch.dict(os.environ, {k: "" for k in _ALL_KEYS}):
        if "llm_client" in sys.modules:
            return importlib.reload(sys.modules["llm_client"])
        return importlib.import_module("llm_client")


class BackendRouting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.L = _load_client()

    def test_model_prefix_routing(self):
        d = self.L._detect_backend
        cases = {
            "claude-opus-5": "anthropic",
            "claude-haiku-4-5": "anthropic",
            "claude-sonnet-99": "anthropic",          # unknown future id still routes by prefix
            "gpt-5.6-sol": "openai",
            "gpt-5.6-luna": "openai",
            "gpt-6-preview": "openai",
            "o3-mini": "openai",
            "chatgpt-4o-latest": "openai",
            "gpt-oss-120b": "uf",                     # exact match wins over the gpt- prefix
            "gpt-oss-20b": "uf",
            "gpt-oss-safeguard-20b": "uf",            # gpt-oss prefix → UF, never OpenAI
            "openai/gpt-oss-120b": "deepinfra",       # DeepInfra hosts gpt-oss under the openai/ org
            "Qwen/QwQ-32B": "deepinfra",
            "some-org/some-model": "deepinfra",
            "llama3.1:8b": "local",
            "registry/org/model:tag": "deepinfra",    # documented: "/" beats ":"
        }
        for model, want in cases.items():
            with self.subTest(model=model):
                self.assertEqual(d(model), want)

    def test_fallback_order_by_configured_key(self):
        d = self.L._detect_backend
        base = {k: "" for k in _ALL_KEYS}
        with mock.patch.dict(os.environ, base, clear=False):
            with self.assertRaises(ValueError):
                d()
        for key, want in [
            ("UF_API_KEY", "uf"), ("DEEPINFRA_TOKEN", "deepinfra"),
            ("OPENAI_API_KEY", "openai"), ("ANTHROPIC_API_KEY", "anthropic"),
            ("LOCAL_LLM_MODEL", "local"),
        ]:
            with self.subTest(key=key), mock.patch.dict(os.environ, {**base, key: "x"}):
                self.assertEqual(d(), want)
        # Priority: UF > DeepInfra > OpenAI > Anthropic > local
        with mock.patch.dict(os.environ, {**base, "ANTHROPIC_API_KEY": "a", "OPENAI_API_KEY": "o"}):
            self.assertEqual(d(), "openai")
        with mock.patch.dict(os.environ, {**base, "ANTHROPIC_API_KEY": "a", "LOCAL_LLM_MODEL": "m"}):
            self.assertEqual(d(), "anthropic")
        with mock.patch.dict(os.environ, {**base, "DEEPINFRA_TOKEN": "d", "ANTHROPIC_API_KEY": "a"}):
            self.assertEqual(d(), "deepinfra")

    def test_get_client_requires_key(self):
        base = {k: "" for k in _ALL_KEYS}
        with mock.patch.dict(os.environ, base):
            for backend in ("openai", "anthropic"):
                with self.subTest(backend=backend), self.assertRaises(ValueError) as cm:
                    self.L.get_client(backend=backend)
                self.assertIn(self.L.BACKENDS[backend]["api_key_env"], str(cm.exception))

    def test_get_client_types(self):
        import openai
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test", "ANTHROPIC_API_KEY": "sk-ant-test"}):
            c, name = self.L.get_client(backend="openai")
            self.assertEqual(name, "openai")
            self.assertIsInstance(c, openai.OpenAI)
            self.assertEqual(str(c.base_url).rstrip("/"), "https://api.openai.com/v1")
            try:
                import anthropic
            except ImportError:  # pragma: no cover
                self.skipTest("anthropic SDK not installed")
            c, name = self.L.get_client(backend="anthropic")
            self.assertEqual(name, "anthropic")
            self.assertIsInstance(c, anthropic.Anthropic)

    def test_backends_table_consistency(self):
        for name, cfg in self.L.BACKENDS.items():
            with self.subTest(backend=name):
                self.assertIn("api_key_env", cfg)
                if cfg["default_model"]:
                    self.assertIn(cfg["default_model"], cfg["models"] or [cfg["default_model"]])
                    self.assertEqual(self.L._detect_backend(cfg["default_model"]), name)
        self.assertEqual(set(self.L._FALLBACK_ORDER), set(self.L.BACKENDS))


class RequestConstruction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.L = _load_client()

    def _chat(self, backend, model, **over):
        args = dict(system="S", user="U", max_tokens=123, temperature=0.3, reasoning_effort="high")
        args.update(over)
        return self.L._chat_request_kwargs(backend, model, **args)

    def test_openai_reasoning_model_kwargs(self):
        kw = self._chat("openai", "gpt-5.6-sol")
        self.assertEqual(kw["max_completion_tokens"], 123)
        self.assertNotIn("max_tokens", kw)
        self.assertEqual(kw["reasoning_effort"], "high")
        self.assertNotIn("temperature", kw)            # rejected by gpt-5.x / o-series
        self.assertNotIn("extra_body", kw)
        self.assertEqual([m["role"] for m in kw["messages"]], ["system", "user"])

    def test_openai_reasoning_none_reenables_temperature(self):
        kw = self._chat("openai", "gpt-5.6-luna", reasoning_effort="none")
        self.assertEqual(kw["reasoning_effort"], "none")
        self.assertEqual(kw["temperature"], 0.3)

    def test_openai_non_reasoning_model_kwargs(self):
        kw = self._chat("openai", "gpt-4.1-mini")
        self.assertEqual(kw["temperature"], 0.3)
        self.assertNotIn("reasoning_effort", kw)
        self.assertEqual(kw["max_completion_tokens"], 123)

    def test_uf_deepinfra_local_kwargs(self):
        for backend, model in (("uf", "gpt-oss-120b"), ("deepinfra", "deepseek-ai/DeepSeek-V4-Flash-0731")):
            with self.subTest(backend=backend):
                kw = self._chat(backend, model)
                self.assertEqual(kw["max_tokens"], 123)
                self.assertEqual(kw["temperature"], 0.3)
                self.assertEqual(kw["extra_body"], {"reasoning_effort": "high"})
                self.assertNotIn("reasoning_effort", kw)   # only inside extra_body
        kw = self._chat("local", "llama3.1:8b")
        self.assertEqual(kw["max_tokens"], 123)
        self.assertNotIn("extra_body", kw)

    def test_anthropic_modern_model_kwargs(self):
        for model in ("claude-opus-5", "claude-sonnet-5", "claude-fable-5", "claude-opus-4-8", "claude-opus-4-7"):
            with self.subTest(model=model):
                kw = self.L._anthropic_request_kwargs(model, "S", "U", 123, 0.3, "high")
                self.assertEqual(kw["system"], "S")
                self.assertEqual(kw["messages"], [{"role": "user", "content": "U"}])
                self.assertEqual(kw["max_tokens"], 123)
                self.assertEqual(kw["thinking"], {"type": "adaptive", "display": "summarized"})
                self.assertEqual(kw["output_config"], {"effort": "high"})
                self.assertNotIn("temperature", kw)    # sampling params rejected on 4.7+
                self.assertNotIn("budget_tokens", str(kw))

    def test_anthropic_46_keeps_temperature_and_caps_effort(self):
        for model in ("claude-opus-4-6", "claude-sonnet-4-6"):
            with self.subTest(model=model):
                kw = self.L._anthropic_request_kwargs(model, "S", "U", 123, 0.3, "medium")
                self.assertEqual(kw["thinking"]["type"], "adaptive")
                self.assertEqual(kw["temperature"], 0.3)
                self.assertEqual(kw["output_config"], {"effort": "medium"})
                # 4.6 has low/medium/high/max only — xhigh is capped, max passes through
                kw = self.L._anthropic_request_kwargs(model, "S", "U", 123, 0.3, "xhigh")
                self.assertEqual(kw["output_config"], {"effort": "high"})
                kw = self.L._anthropic_request_kwargs(model, "S", "U", 123, 0.3, "max")
                self.assertEqual(kw["output_config"], {"effort": "max"})
        kw = self.L._anthropic_request_kwargs("claude-opus-4-7", "S", "U", 123, 0.3, "xhigh")
        self.assertEqual(kw["output_config"], {"effort": "xhigh"})

    def test_anthropic_legacy_model_kwargs(self):
        for model in ("claude-haiku-4-5", "claude-haiku-4-5-20251001", "claude-sonnet-4-5-20250929",
                      "claude-opus-4-5", "claude-opus-4-1", "claude-3-5-haiku-latest"):
            with self.subTest(model=model):
                kw = self.L._anthropic_request_kwargs(model, "S", "U", 123, 0.3, "high")
                self.assertEqual(kw["temperature"], 0.3)
                self.assertNotIn("thinking", kw)
                self.assertNotIn("output_config", kw)

    def test_anthropic_effort_mapping(self):
        for eff, want in [("none", "low"), ("minimal", "low"), ("low", "low"), ("medium", "medium"),
                          ("high", "high"), ("xhigh", "xhigh"), ("max", "max"), ("bogus", "medium")]:
            with self.subTest(effort=eff):
                kw = self.L._anthropic_request_kwargs("claude-opus-5", "S", "U", 10, 0.0, eff)
                self.assertEqual(kw["output_config"]["effort"], want)

    def test_request_params_record(self):
        rec = self.L._request_params_record(self._chat("uf", "gpt-oss-120b"))
        self.assertEqual(rec, {"temperature": 0.3, "max_tokens": 123, "reasoning_effort": "high"})
        rec = self.L._request_params_record(self._chat("local", "llama3.1:8b"))
        self.assertEqual(rec, {"temperature": 0.3, "max_tokens": 123})
        rec = self.L._request_params_record(self._chat("openai", "gpt-5.6-sol"))
        self.assertEqual(rec, {"temperature": None, "max_completion_tokens": 123, "reasoning_effort": "high"})

    def test_temperature_fallback_retries_without_the_knob(self):
        class Rejected(Exception):
            pass
        calls = []

        def create(**kw):
            calls.append(kw)
            if "temperature" in kw:
                raise Rejected("400: `temperature` is not supported on this model")
            return "ok"

        out, sent = self.L._create_with_temperature_fallback(create, {"model": "m", "temperature": 0.7}, (Rejected,))
        self.assertEqual(out, "ok")
        self.assertNotIn("temperature", sent)
        self.assertEqual(len(calls), 2)
        # Unrelated 400s propagate untouched.
        def create_other(**kw):
            raise Rejected("400: max_tokens too large")
        with self.assertRaises(Rejected):
            self.L._create_with_temperature_fallback(create_other, {"model": "m", "temperature": 0.7}, (Rejected,))

    def test_response_dataclass_fields(self):
        r = self.L.LLMResponse(content="c", reasoning=None, model="m", backend="openai")
        self.assertIsNone(r.finish_reason)
        self.assertEqual(r.request_params, {})


@unittest.skipUnless(os.getenv("LLM_CLIENT_LIVE") == "1", "set LLM_CLIENT_LIVE=1 for the live canary")
class LiveCanary(unittest.TestCase):
    """One tiny call per configured frontier provider. Costs a fraction of a cent."""

    @classmethod
    def setUpClass(cls):
        if str(CLIENT_DIR) not in sys.path:
            sys.path.insert(0, str(CLIENT_DIR))
        cls.L = importlib.reload(sys.modules["llm_client"]) if "llm_client" in sys.modules \
            else importlib.import_module("llm_client")

    def _probe(self, model):
        r = self.L.call(system="Answer tersely.", user="What is 17*23? Reply with the number only.",
                        model=model, max_tokens=3000, reasoning_effort="low")
        self.assertIn("391", r.content or "")
        self.assertTrue(r.model)
        self.assertIn(r.finish_reason, ("stop", "end_turn"))
        self.assertIn("temperature", r.request_params)
        self.assertGreater(r.usage["completion_tokens"], 0)
        return r

    def test_openai(self):
        if not os.getenv("OPENAI_API_KEY"):
            self.skipTest("OPENAI_API_KEY not set")
        r = self._probe("gpt-5.6-luna")
        self.assertEqual(r.backend, "openai")
        self.assertIsNone(r.request_params["temperature"])
        self.assertIn("reasoning_tokens", r.usage)

    def test_anthropic(self):
        if not os.getenv("ANTHROPIC_API_KEY"):
            self.skipTest("ANTHROPIC_API_KEY not set")
        r = self._probe("claude-haiku-4-5")
        self.assertEqual(r.backend, "anthropic")
        self.assertEqual(r.request_params["temperature"], 0.7)
        r = self._probe("claude-sonnet-5")
        self.assertIsNone(r.request_params["temperature"])
        self.assertEqual(r.request_params["output_config"], {"effort": "low"})


if __name__ == "__main__":
    unittest.main()
