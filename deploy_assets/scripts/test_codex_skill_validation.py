import unittest

from codex_skill_validation import CodexSkillValidationError
from codex_skill_validation import validate_codex_skill_frontmatter


class CodexSkillValidationTest(unittest.TestCase):
    def assert_invalid(self, frontmatter, message):
        with self.assertRaisesRegex(CodexSkillValidationError, message):
            validate_codex_skill_frontmatter(frontmatter)

    def test_accepts_complete_bundled_contract(self):
        fields = {
            "name": "demo-skill-2",
            "description": "A valid description with Unicode punctuation — safely.",
            "license": "MIT",
            "allowed-tools": "Bash, Read",
            "metadata": {"short-description": "Demo"},
        }

        name, description = validate_codex_skill_frontmatter(fields)

        self.assertEqual(name, "demo-skill-2")
        self.assertEqual(description, fields["description"])

    def test_rejects_unexpected_frontmatter_keys(self):
        self.assert_invalid(
            {"name": "demo", "description": "Demo", "tools": "Bash"},
            r"unexpected frontmatter key\(s\): tools",
        )

    def test_requires_name_and_description(self):
        for fields, missing in (
            ({"description": "Demo"}, "name"),
            ({"name": "demo"}, "description"),
        ):
            with self.subTest(missing=missing):
                self.assert_invalid(fields, f"missing frontmatter field '{missing}'")

    def test_requires_string_fields(self):
        for field in ("name", "description"):
            fields = {"name": "demo", "description": "Demo"}
            fields[field] = 1
            with self.subTest(field=field):
                self.assert_invalid(fields, f"field '{field}' must be a string")

    def test_requires_nonempty_runtime_fields(self):
        for field in ("name", "description"):
            fields = {"name": "demo", "description": "Demo"}
            fields[field] = "  "
            with self.subTest(field=field):
                self.assert_invalid(fields, f"field '{field}' must be non-empty")

    def test_rejects_non_hyphen_case_names(self):
        for name in ("Demo", "demo_skill", "demo skill"):
            with self.subTest(name=name):
                self.assert_invalid(
                    {"name": name, "description": "Demo"},
                    "must be hyphen-case",
                )

    def test_rejects_bad_hyphen_placement(self):
        for name in ("-demo", "demo-", "demo--skill"):
            with self.subTest(name=name):
                self.assert_invalid(
                    {"name": name, "description": "Demo"},
                    "cannot start or end with a hyphen or contain consecutive hyphens",
                )

    def test_name_limit_counts_characters(self):
        validate_codex_skill_frontmatter(
            {"name": "x" * 64, "description": "Demo"}
        )
        self.assert_invalid(
            {"name": "x" * 65, "description": "Demo"},
            "name is 65 characters",
        )

    def test_description_limit_counts_characters(self):
        validate_codex_skill_frontmatter(
            {"name": "demo", "description": "—" * 1024}
        )
        self.assert_invalid(
            {"name": "demo", "description": "—" * 1025},
            "description is 1025 characters",
        )

    def test_rejects_each_angle_bracket(self):
        for bracket in ("<", ">"):
            with self.subTest(bracket=bracket):
                self.assert_invalid(
                    {"name": "demo", "description": f"before {bracket} after"},
                    r"cannot contain angle brackets \(< or >\)",
                )


if __name__ == "__main__":
    unittest.main()
