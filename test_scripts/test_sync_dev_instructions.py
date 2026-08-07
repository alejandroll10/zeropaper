import os
import stat
import shutil
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "sync_dev_instructions.sh"
VALIDATOR = REPO_ROOT / "deploy_assets" / "scripts" / "codex_skill_validation.py"
VALID_SKILL_MD = "---\nname: demo\ndescription: Demo skill.\n---\n\n# Demo\n"


class SyncDevInstructionsTest(unittest.TestCase):
    @contextmanager
    def repo(self, skill_md=VALID_SKILL_MD, *, committed=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "deploy_assets" / "scripts").mkdir(parents=True)
            (root / ".claude" / "skills" / "demo").mkdir(parents=True)
            shutil.copy2(SCRIPT, root / "scripts" / SCRIPT.name)
            shutil.copy2(VALIDATOR, root / "deploy_assets" / "scripts" / VALIDATOR.name)
            (root / "CLAUDE.md").write_text("# Test instructions\n", encoding="utf-8")
            (root / ".claude" / "skills" / "demo" / "SKILL.md").write_text(
                skill_md,
                encoding="utf-8",
            )
            if committed:
                self.assertEqual(self.run_sync(root).returncode, 0)
                self.git(root, "init", "--quiet")
                self.commit_all(root, "baseline")
            yield root

    def run_sync(self, root, *, env=None):
        return subprocess.run(
            ["bash", str(root / "scripts" / SCRIPT.name)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

    def git(self, root, *args):
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def commit_all(self, root, message):
        self.git(root, "add", "-A")
        self.git(
            root,
            "-c",
            "user.name=Mirror Test",
            "-c",
            "user.email=mirror-test@example.invalid",
            "commit",
            "--quiet",
            "-m",
            message,
        )

    def run_ci_check(self, root):
        result = self.run_sync(root)
        if result.returncode != 0:
            return result
        self.git(root, "add", "-A", "-f", "--", "AGENTS.md", ".agents/skills")
        return subprocess.run(
            [
                "git",
                "diff",
                "--cached",
                "--exit-code",
                "HEAD",
                "--",
                "AGENTS.md",
                ".agents/skills",
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

    def add_skill(self, root, name):
        path = root / ".claude" / "skills" / name
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {name} skill.\n---\n\n# {name}\n",
            encoding="utf-8",
        )

    def test_accepts_1024_multibyte_description(self):
        description = "—" * 1024
        skill_md = f'---\nname: demo\ndescription: "{description}"\n---\n\n# Demo\n'

        with self.repo(skill_md) as root:
            result = self.run_sync(root)

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

        with self.repo(skill_md) as root:
            result = self.run_sync(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("1024-character skill-authoring limit", result.stderr)

    def test_rejects_each_angle_bracket(self):
        for bracket in ("<", ">"):
            skill_md = (
                "---\n"
                "name: demo\n"
                f'description: "before {bracket} after"\n'
                "---\n\n"
                "# Demo\n"
            )

            with self.subTest(bracket=bracket):
                with self.repo(skill_md) as root:
                    result = self.run_sync(root)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "description cannot contain angle brackets (< or >)", result.stderr
                )

    def test_ci_check_accepts_current_mirrors(self):
        with self.repo(committed=True) as root:
            result = self.run_ci_check(root)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_ci_check_rejects_stale_agents_md(self):
        with self.repo(committed=True) as root:
            with (root / "CLAUDE.md").open("a", encoding="utf-8") as canonical:
                canonical.write("New canonical rule.\n")
            self.commit_all(root, "leave AGENTS stale")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)

    def test_ci_check_rejects_every_generated_header_line(self):
        replacements = (
            ("<!-- GENERATED FILE — DO NOT EDIT.", "<!-- hand edited"),
            ("Mirror of CLAUDE.md", "Untrusted mirror of CLAUDE.md"),
            ("Edit CLAUDE.md instead", "Edit AGENTS.md instead"),
            (">\n\n# Test instructions",
             ">\nheader blank line replaced\n# Test instructions"),
        )
        for original, replacement in replacements:
            with self.subTest(original=original), self.repo(committed=True) as root:
                mirror = root / "AGENTS.md"
                mirror.write_text(
                    mirror.read_text(encoding="utf-8").replace(
                        original, replacement, 1
                    ),
                    encoding="utf-8",
                )
                self.commit_all(root, "edit generated header")

                result = self.run_ci_check(root)

                self.assertNotEqual(result.returncode, 0)

    def test_ci_check_rejects_trailing_newline_drift(self):
        with self.repo(committed=True) as root:
            mirror = root / "AGENTS.md"
            mirror.write_bytes(mirror.read_bytes() + b"\n")
            self.commit_all(root, "add trailing newline")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)

    def test_ci_check_rejects_agents_md_symlink(self):
        with self.repo(committed=True) as root:
            mirror = root / "AGENTS.md"
            target = root / "generated-copy.md"
            shutil.copy2(mirror, target)
            mirror.unlink()
            os.symlink(target.name, mirror)
            os.symlink(target.name, root / "AGENTS.md.tmp")
            self.commit_all(root, "replace AGENTS with a symlink")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)

    def test_sync_tempfile_cannot_clobber_canonical_symlink_target(self):
        with self.repo() as root:
            canonical = root / "CLAUDE.md"
            expected = canonical.read_bytes()
            os.symlink(canonical.name, root / "AGENTS.md.tmp")

            result = self.run_sync(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(canonical.read_bytes(), expected)

    def test_sync_preserves_foreign_fixed_probe_path(self):
        with self.repo() as root:
            skills = root / ".agents" / "skills"
            skills.mkdir(parents=True)
            probe = skills / ".symlink-probe"
            probe.write_text("developer content\n", encoding="utf-8")

            result = self.run_sync(root)

            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(
                probe.read_text(encoding="utf-8"), "developer content\n"
            )

    def test_ci_check_rejects_executable_agents_md(self):
        with self.repo(committed=True) as root:
            mirror = root / "AGENTS.md"
            mirror.chmod(0o755)
            self.commit_all(root, "make AGENTS executable")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)

    def test_ci_check_rejects_missing_mirror_link(self):
        with self.repo(committed=True) as root:
            (root / ".agents" / "skills" / "demo").unlink()
            self.commit_all(root, "delete mirror link")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)

    def test_ci_check_rejects_new_skill_without_mirror(self):
        with self.repo(committed=True) as root:
            self.add_skill(root, "extra")
            self.commit_all(root, "add canonical skill only")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)

    def test_ci_check_rejects_hidden_canonical_skill(self):
        with self.repo(committed=True) as root:
            hidden = root / ".claude" / "skills" / ".hidden"
            hidden.mkdir()
            (hidden / "SKILL.md").write_text(
                "---\nname: hidden\ndescription: Hidden skill.\n---\n",
                encoding="utf-8",
            )
            self.commit_all(root, "add hidden canonical skill")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a valid Codex skill name", result.stderr)

    def test_sync_rejects_uppercase_skill_under_inherited_nocasematch(self):
        with self.repo() as root:
            uppercase = root / ".claude" / "skills" / "Upper"
            uppercase.mkdir()
            (uppercase / "SKILL.md").write_text(
                "---\nname: upper\ndescription: Upper skill.\n---\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["BASHOPTS"] = "nocasematch"

            result = self.run_sync(root, env=env)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a valid Codex skill name", result.stderr)

    def test_ci_check_rejects_resolvable_newline_link_target(self):
        with self.repo(committed=True) as root:
            newline_skill = root / ".claude" / "skills" / "demo\n"
            newline_skill.mkdir()
            (newline_skill / "SKILL.md").write_text(
                VALID_SKILL_MD, encoding="utf-8"
            )
            mirror = root / ".agents" / "skills" / "demo"
            mirror.unlink()
            os.symlink(
                "../../.claude/skills/demo\n", mirror, target_is_directory=True
            )
            self.commit_all(root, "add resolvable newline target")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)

    def test_sync_preserves_permissions_when_content_changes(self):
        with self.repo() as root:
            self.assertEqual(self.run_sync(root).returncode, 0)
            mirror = root / "AGENTS.md"
            mirror.chmod(0o670)
            with (root / "CLAUDE.md").open("a", encoding="utf-8") as canonical:
                canonical.write("Changed.\n")

            result = self.run_sync(root)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(stat.S_IMODE(mirror.stat().st_mode), 0o660)

    def test_ci_check_force_adds_ignored_mirror(self):
        with self.repo(committed=True) as root:
            self.add_skill(root, "extra")
            (root / ".gitignore").write_text(
                ".agents/skills/extra\n", encoding="utf-8"
            )
            self.commit_all(root, "ignore missing mirror")

            result = self.run_ci_check(root)
            staged = self.git(root, "diff", "--cached", "--name-only", "HEAD")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(".agents/skills/extra", staged.stdout)

    def test_ci_check_rejects_extra_stale_link(self):
        with self.repo(committed=True) as root:
            os.symlink(
                "../../.claude/skills/stale",
                root / ".agents" / "skills" / "stale",
                target_is_directory=True,
            )
            self.commit_all(root, "add stale mirror link")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)

    def test_ci_check_rejects_hidden_stale_link(self):
        with self.repo(committed=True) as root:
            os.symlink(
                "../../.claude/skills/.stale",
                root / ".agents" / "skills" / ".stale",
                target_is_directory=True,
            )
            self.commit_all(root, "add hidden stale mirror link")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)

    def test_ci_check_rejects_malformed_link_target(self):
        with self.repo(committed=True) as root:
            mirror = root / ".agents" / "skills" / "demo"
            mirror.unlink()
            os.symlink(
                "../../.claude/skills/demo\n", mirror, target_is_directory=True
            )
            self.commit_all(root, "add newline to link target")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a generated mirror entry", result.stderr)

    def test_ci_check_rejects_skill_directory_without_skill_md(self):
        with self.repo(committed=True) as root:
            broken = root / ".claude" / "skills" / "broken"
            broken.mkdir()
            (broken / "README.md").write_text("incomplete\n", encoding="utf-8")
            self.commit_all(root, "add incomplete skill")

            result = self.run_ci_check(root)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("has no SKILL.md", result.stderr)


if __name__ == "__main__":
    unittest.main()
