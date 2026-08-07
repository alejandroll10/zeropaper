import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("assemble_codex_skills.py")
VALIDATOR = Path(__file__).with_name("codex_skill_validation.py")
REPO_ROOT = Path(__file__).resolve().parents[2]


class AssembleCodexSkillsTest(unittest.TestCase):
    def run_assembler(self, description, name="demo"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "metadata.json"
            bodies = root / "bodies"
            output = root / "output"
            bodies.mkdir()
            metadata.write_text(
                json.dumps({"demo": {"name": name, "description": description}}),
                encoding="utf-8",
            )
            (bodies / "demo.md").write_text("# Demo\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--metadata",
                    str(metadata),
                    "--bodies-dir",
                    str(bodies),
                    "--output-dir",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            rendered = (
                (output / "demo" / "SKILL.md").read_text(encoding="utf-8")
                if result.returncode == 0
                else None
            )
            return result, rendered

    def test_accepts_1024_multibyte_characters(self):
        description = "—" * 1024

        result, rendered = self.run_assembler(description)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(description, rendered)

    def test_ignores_surrounding_description_whitespace_at_limit(self):
        description = f"  {'—' * 1024}  "

        result, rendered = self.run_assembler(description)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(description, rendered)

    def test_rejects_1025_characters(self):
        result, rendered = self.run_assembler("x" * 1025)

        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(rendered)
        self.assertIn("1025 characters", result.stderr)
        self.assertIn("1024-character skill-authoring limit", result.stderr)

    def test_accepts_64_character_name(self):
        name = "x" * 64

        result, rendered = self.run_assembler("Demo skill", name=name)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'name: "{name}"', rendered)

    def test_ignores_surrounding_name_whitespace_at_limit(self):
        name = f"  {'x' * 64}  "

        result, rendered = self.run_assembler("Demo skill", name=name)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'name: "{name}"', rendered)

    def test_rejects_65_character_name(self):
        result, rendered = self.run_assembler("Demo skill", name="x" * 65)

        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(rendered)
        self.assertIn("65 characters", result.stderr)
        self.assertIn("64-character skill-authoring limit", result.stderr)

    def test_rejects_angle_brackets(self):
        for bracket in ("<", ">"):
            with self.subTest(bracket=bracket):
                result, rendered = self.run_assembler(f"before {bracket} after")

                self.assertNotEqual(result.returncode, 0)
                self.assertIsNone(rendered)
                self.assertIn(
                    "description cannot contain angle brackets (< or >)", result.stderr
                )

    def test_all_shipped_codex_skills_pass_full_validator(self):
        metadata_root = REPO_ROOT / "deploy_assets" / "templates" / "skill_metadata"
        bodies_root = REPO_ROOT / "deploy_assets" / "templates" / "skill_bodies"
        metadata_files = sorted(metadata_root.glob("*_skills.json"))
        metadata_files = [
            path for path in metadata_files if path.name != "codex_math_skills.json"
        ]

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "skills"
            expected = set()
            for metadata in metadata_files:
                group = metadata.stem.removesuffix("_skills")
                bodies = bodies_root / group
                self.assertTrue(bodies.is_dir(), f"missing bodies directory for {metadata}")
                skill_ids = set(json.loads(metadata.read_text(encoding="utf-8")))
                self.assertTrue(
                    expected.isdisjoint(skill_ids),
                    f"duplicate skill ids in {metadata}: {expected & skill_ids}",
                )
                expected.update(skill_ids)
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--metadata",
                        str(metadata),
                        "--bodies-dir",
                        str(bodies),
                        "--output-dir",
                        str(output),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

            assembled = {path.name for path in output.iterdir()}
            self.assertEqual(assembled, expected)
            self.assertNotIn("codex-math", assembled)
            for skill_id in sorted(assembled):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        str(output / skill_id / "SKILL.md"),
                        "--label",
                        skill_id,
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
