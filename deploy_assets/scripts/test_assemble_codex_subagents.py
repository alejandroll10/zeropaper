#!/usr/bin/env python3
import os
import subprocess
import tomllib
import unittest
from pathlib import Path

from assemble_codex_subagents import render_agent


ROOT = Path(__file__).resolve().parents[2]


class RenderCodexAgentTests(unittest.TestCase):
    def test_native_role_is_clean_leaf_with_pinned_tier(self):
        rendered = render_agent(
            {
                "name": "scorer",
                "description": "Adversarial scorer.",
                "codex": {
                    "model": "gpt-5.6-terra",
                    "model_reasoning_effort": "high",
                },
            },
            "You are the quality gate.",
        )
        parsed = tomllib.loads(rendered)

        self.assertEqual(parsed["name"], "scorer")
        self.assertEqual(parsed["model"], "gpt-5.6-terra")
        self.assertEqual(parsed["model_reasoning_effort"], "high")
        self.assertEqual(parsed["project_doc_max_bytes"], 0)
        self.assertEqual(parsed["features"]["multi_agent_v2"], {"enabled": False})
        self.assertEqual(parsed["agents"], {"enabled": False})
        self.assertIn("quality gate", parsed["developer_instructions"])

    def test_light_role_uses_luna_default_effort(self):
        rendered = render_agent(
            {
                "name": "scorer",
                "description": "Adversarial scorer.",
                "codex": {
                    "model": "gpt-5.6-terra",
                    "model_reasoning_effort": "high",
                },
            },
            "Score it.",
            model_override="sonnet",
        )
        parsed = tomllib.loads(rendered)

        self.assertEqual(parsed["model"], "gpt-5.6-luna")
        self.assertNotIn("model_reasoning_effort", parsed)
        self.assertEqual(parsed["project_doc_max_bytes"], 0)
        self.assertEqual(parsed["features"]["multi_agent_v2"], {"enabled": False})
        self.assertEqual(parsed["agents"], {"enabled": False})

    def test_runtime_uses_native_same_turn_protocol_only(self):
        session = (ROOT / "deploy_assets/templates/runtime/codex/session.md").read_text()
        launcher = (ROOT / "deploy_assets/launch.sh").read_text()
        manual = (
            ROOT / "deploy_assets/templates/runtime/codex/session_manual.md"
        ).read_text()
        report = (
            ROOT / "deploy_assets/templates/runtime/codex/session_report.md"
        ).read_text()
        report_core = (
            ROOT / "deploy_assets/templates/shared/core_report.md"
        ).read_text()
        finalization = (
            ROOT / "deploy_assets/scripts/setup/finalization.sh"
        ).read_text()
        utilities = (
            ROOT / "deploy_assets/scripts/setup/skills_and_utilities.sh"
        ).read_text()

        for required in (
            "native `spawn_agent` tool",
            "`agent_type`",
            '`fork_turns="none"`',
            "unique `task_name`",
            "keep this parent turn alive",
            "wait/status tools",
            "interrupts live children",
            "Preserve the current stage's exact commit boundary",
            "task-owned uncommitted diff",
            "at most three children live",
        ):
            self.assertIn(required, session)

        self.assertIn("at most three children live", manual)
        self.assertIn("at most three children live", report)
        self.assertIn("post-terminal audit-plus-ledger commit", report)
        self.assertIn("triage plus that ledger together as the run baseline", report)
        self.assertIn("never use a broad add", report)
        self.assertIn("does not apply to Codex", report)
        self.assertIn('agent_type="report-reviewer"', report)
        self.assertIn('fork_turns="none"', report)
        self.assertIn("process_log/report_self_review_r{N}.md", report)
        self.assertIn("committed `CLEAN` round", report)
        self.assertIn("Codex native roles never use file growth as liveness", report_core)
        self.assertIn('echo "  ./launch.sh codex --once', finalization)
        self.assertIn('trust_level=\\"trusted\\"', launcher)
        self.assertIn("-c 'features.multi_agent_v2=true'", launcher)
        self.assertIn("stage-defined durable commit boundary", launcher)
        self.assertIn("codex_toml_basic_string", launcher)
        preflight = ROOT / "deploy_assets/templates/utils/codex_preflight.sh"
        for unicode_root in ("/tmp/📄 project", "/tmp/paper-\x7f"):
            encoded_root = subprocess.check_output(
                [
                    "bash",
                    "-c",
                    '. "$1"; codex_toml_basic_string "$2"',
                    "bash",
                    str(preflight),
                    unicode_root,
                ],
                text=True,
            )
            parsed_trust = tomllib.loads(
                f"[projects.{encoded_root}]\ntrust_level = \"trusted\"\n"
            )
            self.assertEqual(
                parsed_trust["projects"][unicode_root]["trust_level"], "trusted"
            )
        non_utf8_root = os.fsdecode(b"/tmp/non-utf8-\xff")
        rejected = subprocess.run(
            [
                "bash",
                "-c",
                '. "$1"; codex_toml_basic_string "$2"',
                "bash",
                str(preflight),
                non_utf8_root,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("non-UTF-8 filesystem path", rejected.stderr)
        self.assertIn("task-owned uncommitted diff is incomplete", launcher)
        self.assertIn("private control/liveness pipe", launcher)
        self.assertIn('CODEX_STATE_HOME="${CODEX_HOME:-$HOME/.codex}"', launcher)
        self.assertIn('payload = json.loads(handle.readline(1 << 20))', launcher)
        self.assertNotIn("wait_for_workers", launcher)
        self.assertNotIn("agent_launcher", utilities)
        self.assertFalse(
            (
                ROOT
                / "deploy_assets/templates/utils/agent_launcher/launch_agent.sh"
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
