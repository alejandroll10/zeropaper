"""Self-contained tests for the fragment-include mechanism in agent_body_loader.

Run: python3 test_loader_includes.py  (from anywhere; adjusts sys.path)
"""
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import agent_body_loader as L  # noqa: E402


def setup_dirs(tmp):
    bodies = tmp / "bodies"
    frags = tmp / "frags"
    bodies.mkdir()
    frags.mkdir()
    return bodies, frags


def run():
    passed = 0
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        bodies, frags = setup_dirs(tmp)

        # 1. Basic include
        (frags / "archetype.md").write_text("JUDGE BY SUBSTANCE.\n")
        (bodies / "a1.md").write_text("Intro.\n\n{{> archetype }}\n\nOutro.\n")
        out = L.load_body("a1", str(bodies), fragments_dir=str(frags))
        assert out == "Intro.\n\nJUDGE BY SUBSTANCE.\n\nOutro.\n", repr(out)
        passed += 1

        # 2. Include + vocab: fragment carries a vocab key, resolved with caller vocab
        (frags / "mech.md").write_text("The {{MECHANISM_TERM}} must deliver.\n")
        (bodies / "a2.md").write_text("{{> mech }}")
        out = L.load_body("a2", str(bodies), fragments_dir=str(frags),
                          vocab={"MECHANISM_TERM": "mechanism"})
        assert out == "The mechanism must deliver.", repr(out)
        passed += 1

        # 3. Nested include (fragment includes another)
        (frags / "outer.md").write_text("OUTER[ {{> inner }} ]")
        (frags / "inner.md").write_text("INNER")
        (bodies / "a3.md").write_text("{{> outer }}")
        out = L.load_body("a3", str(bodies), fragments_dir=str(frags))
        assert out == "OUTER[ INNER ]", repr(out)
        passed += 1

        # 4. Body with NO includes is unchanged (byte-identical, no vocab)
        (bodies / "a4.md").write_text("Plain body, no directives.\n")
        out = L.load_body("a4", str(bodies), fragments_dir=str(frags))
        assert out == "Plain body, no directives.\n", repr(out)
        passed += 1

        # 5. Missing fragment fails loud
        (bodies / "a5.md").write_text("{{> nonexistent }}")
        try:
            L.load_body("a5", str(bodies), fragments_dir=str(frags))
            assert False, "expected FileNotFoundError"
        except FileNotFoundError as e:
            assert "nonexistent" in str(e)
            passed += 1

        # 6. Cycle detection
        (frags / "loopa.md").write_text("A {{> loopb }}")
        (frags / "loopb.md").write_text("B {{> loopa }}")
        (bodies / "a6.md").write_text("{{> loopa }}")
        try:
            L.load_body("a6", str(bodies), fragments_dir=str(frags))
            assert False, "expected RecursionError"
        except RecursionError:
            passed += 1

        # 7. Uppercase {{KEY}} is NOT treated as an include (stays for vocab)
        (bodies / "a7.md").write_text("{{SOME_KEY}} and {{> archetype }}")
        out = L.load_body("a7", str(bodies), fragments_dir=str(frags),
                          vocab={"SOME_KEY": "X"})
        assert out == "X and JUDGE BY SUBSTANCE.", repr(out)
        passed += 1

        # 8. Default fragments dir resolves to templates/fragments (real repo)
        assert L.DEFAULT_FRAGMENTS_DIR == REPO / "templates" / "fragments", \
            L.DEFAULT_FRAGMENTS_DIR
        passed += 1

    print(f"OK — {passed}/8 tests passed")


if __name__ == "__main__":
    run()
