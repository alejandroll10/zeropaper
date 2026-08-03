#!/usr/bin/env python3
import unittest
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from assemble_opencode_agents import OPENCODE_DEFAULT_MODEL, render_agent


class OpenCodeAssemblerTest(unittest.TestCase):
    def test_project_config_is_unattended_safe(self):
        config = json.loads(
            (Path(__file__).parent.parent / "templates/runtime/opencode/opencode.json").read_text()
        )
        self.assertEqual(config["share"], "disabled")
        self.assertEqual(config["permission"]["question"], "deny")
        self.assertEqual(config["permission"]["doom_loop"], "allow")
        self.assertEqual(config["skills"]["paths"], [".claude/skills"])

    def test_frontmatter_model_tools_skills_and_leaf_policy(self):
        rendered = render_agent(
            {
                "name": "reviewer",
                "description": 'Review "carefully"',
                "model": "opus",
                "tools": "Read, Grep, WebSearch",
                "skills": ["sympy"],
            },
            "Review the artifact.",
        )
        self.assertIn(f'model: "{OPENCODE_DEFAULT_MODEL}"', rendered)
        self.assertIn('description: "Review \\"carefully\\""', rendered)
        self.assertIn("  read: allow", rendered)
        self.assertIn("  grep: allow", rendered)
        self.assertIn("  websearch: allow", rendered)
        self.assertIn("  edit: deny", rendered)
        self.assertIn("  task: deny", rendered)
        self.assertIn('    "sympy": allow', rendered)
        self.assertTrue(rendered.endswith("Review the artifact.\n"))

    def test_runtime_model_override(self):
        rendered = render_agent(
            {
                "name": "worker",
                "description": "Works",
                "model": "sonnet",
                "tools": "Read",
                "opencode": {"model": "vendor/special", "steps": 12},
            },
            "Work.",
        )
        self.assertIn('model: "vendor/special"', rendered)
        self.assertIn("steps: 12", rendered)

    def test_comma_separated_extension_skills(self):
        rendered = render_agent(
            {
                "name": "worker",
                "description": "Works",
                "model": "sonnet",
                "tools": "Read",
                "skills": "fred, openalex",
            },
            "Work.",
        )
        self.assertIn('    "fred": allow', rendered)
        self.assertIn('    "openalex": allow', rendered)


if __name__ == "__main__":
    unittest.main()
