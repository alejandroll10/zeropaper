import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "sync_dev_instructions.sh"


class SyncDevInstructionsTest(unittest.TestCase):
    def run_sync(self, skill_md):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / ".claude" / "skills" / "demo").mkdir(parents=True)
            shutil.copy2(SCRIPT, root / "scripts" / SCRIPT.name)
            (root / "CLAUDE.md").write_text("# Test instructions\n", encoding="utf-8")
            (root / ".claude" / "skills" / "demo" / "SKILL.md").write_text(
                skill_md,
                encoding="utf-8",
            )
            return subprocess.run(
                ["bash", str(root / "scripts" / SCRIPT.name)],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )

    def test_accepts_1024_multibyte_description(self):
        description = "—" * 1024
        skill_md = f'---\nname: demo\ndescription: "{description}"\n---\n\n# Demo\n'

        result = self.run_sync(skill_md)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("description 1024/1024 chars", result.stdout)

    def test_rejects_overlong_literal_block_description(self):
        skill_md = (
            "---\n"
            "name: demo\n"
            "description: |\n"
            "  a\n"
            + ("\n" * 1023)
            + "  b\n"
            "---\n\n"
            "# Demo\n"
        )
        frontmatter = skill_md.split("---\n", 2)[1]
        description = yaml.safe_load(frontmatter)["description"].strip()
        self.assertGreater(len(description), 1024)

        result = self.run_sync(skill_md)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skill-authoring validator", result.stderr)
        self.assertIn("over 1024", result.stderr)


if __name__ == "__main__":
    unittest.main()
