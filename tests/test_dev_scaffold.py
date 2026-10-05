"""Unit tests for DevScaffold. Run with:  python -m unittest discover -s tests"""

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import dev_scaffold as ds  # noqa: E402


def quiet(*_args, **_kwargs):
    pass


class CreateProjectTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_php_template_layout(self):
        root = ds.create_project("MyApp", base=self.base, out=quiet)
        for d in ["src/Models", "src/Repositories", "src/Services", "config", "public", "tests"]:
            self.assertTrue((root / d / ".gitkeep").is_file(), d)
        for f in ["README.md", ".gitignore", ".env.example", "composer.json", "config/config.php", "public/index.php"]:
            self.assertTrue((root / f).is_file(), f)

    def test_php_composer_has_psr4_mapping(self):
        root = ds.create_project("my-app", base=self.base, out=quiet)
        composer = json.loads((root / "composer.json").read_text(encoding="utf-8"))
        self.assertEqual(composer["autoload"]["psr-4"], {"MyApp\\": "src/"})

    def test_python_template_layout(self):
        root = ds.create_project("my-tool", template="python", base=self.base, out=quiet)
        self.assertTrue((root / "src/my_tool/__init__.py").is_file())
        self.assertTrue((root / "pyproject.toml").is_file())
        self.assertTrue((root / "tests/test_smoke.py").is_file())

    def test_files_end_with_newline(self):
        root = ds.create_project("MyApp", base=self.base, out=quiet)
        for f in ["README.md", ".gitignore", "composer.json", "config/config.php"]:
            self.assertTrue((root / f).read_text(encoding="utf-8").endswith("\n"), f)

    def test_existing_files_are_not_overwritten(self):
        root = ds.create_project("MyApp", base=self.base, out=quiet)
        (root / "README.md").write_text("my notes\n", encoding="utf-8")
        ds.create_project("MyApp", base=self.base, out=quiet)
        self.assertEqual((root / "README.md").read_text(encoding="utf-8"), "my notes\n")

    def test_force_overwrites(self):
        root = ds.create_project("MyApp", base=self.base, out=quiet)
        (root / "README.md").write_text("my notes\n", encoding="utf-8")
        ds.create_project("MyApp", force=True, base=self.base, out=quiet)
        self.assertIn("DevScaffold", (root / "README.md").read_text(encoding="utf-8"))

    def test_rejects_unsafe_names(self):
        for bad in ["../escaped", "/abs", "has space", "1starts-with-digit", "", "a/b"]:
            with self.subTest(name=bad):
                with self.assertRaises(ValueError):
                    ds.create_project(bad, base=self.base, out=quiet)
        self.assertEqual(list(self.base.iterdir()), [])

    def test_rejects_unknown_template(self):
        with self.assertRaises(ValueError):
            ds.create_project("MyApp", template="cobol", base=self.base, out=quiet)


class CliTests(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = ds.main(list(argv))
            except SystemExit as e:  # argparse exits on usage errors
                code = e.code
        return code, out.getvalue(), err.getvalue()

    def test_bad_name_exits_2(self):
        code, _, err = self.run_cli("../escaped")
        self.assertEqual(code, 2)
        self.assertIn("Error", err)

    def test_missing_name_exits_2(self):
        code, _, _ = self.run_cli()
        self.assertEqual(code, 2)

    def test_success_exits_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            import os
            cwd = os.getcwd()
            os.chdir(tmp)
            try:
                code, out, _ = self.run_cli("Demo", "--template", "python")
            finally:
                os.chdir(cwd)
        self.assertEqual(code, 0)
        self.assertIn("ready", out)


if __name__ == "__main__":
    unittest.main()
