"""DevScaffold: create a consistent project skeleton from the command line.

    python src/dev_scaffold.py MyProject                   # PHP template (default)
    python src/dev_scaffold.py my_tool --template python
    python src/dev_scaffold.py MyProject --force           # overwrite seeded files

Folders are always created (and kept in git via .gitkeep). Seeded files are
never overwritten unless --force is given, so re-running is safe.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

__version__ = "1.0.0"

# Must start with a letter; letters, digits, '-' and '_' only. This also
# blocks path tricks like "../elsewhere" or absolute paths.
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def _php_namespace(name: str) -> str:
    """'my-app' -> 'MyApp' so the PSR-4 namespace is a valid PHP identifier."""
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[-_]", name) if part)


def _python_package(name: str) -> str:
    return name.lower().replace("-", "_")


def php_template(name: str) -> tuple[list[str], dict[str, str]]:
    ns = _php_namespace(name)
    composer = {
        "name": f"vendor/{name.lower()}",
        "type": "project",
        "require": {"php": ">=8.1"},
        "autoload": {"psr-4": {f"{ns}\\": "src/"}},
    }
    dirs = ["src/Models", "src/Repositories", "src/Services", "config", "public", "tests"]
    files = {
        "README.md": f"# {name}\n\nProject initialized with DevScaffold.\n",
        ".gitignore": "/vendor/\n.env\n*.log\n",
        ".env.example": "DB_HOST=localhost\nDB_NAME=\nDB_USER=\nDB_PASS=\n",
        "composer.json": json.dumps(composer, indent=4) + "\n",
        "config/config.php": "<?php\n\ndeclare(strict_types=1);\n\nreturn [\n    // Read settings from the environment, e.g. getenv('DB_HOST')\n];\n",
        "public/index.php": f"<?php\n\ndeclare(strict_types=1);\n\nrequire __DIR__ . '/../vendor/autoload.php';\n\necho 'Hello from {name}';\n",
    }
    return dirs, files


def python_template(name: str) -> tuple[list[str], dict[str, str]]:
    pkg = _python_package(name)
    dirs = [f"src/{pkg}", "tests"]
    files = {
        "README.md": f"# {name}\n\nProject initialized with DevScaffold.\n",
        ".gitignore": "__pycache__/\n*.pyc\n.venv/\n.env\n*.log\ndist/\n*.egg-info/\n",
        "pyproject.toml": (
            "[build-system]\nrequires = [\"setuptools>=61\"]\nbuild-backend = \"setuptools.build_meta\"\n\n"
            f"[project]\nname = \"{name}\"\nversion = \"0.1.0\"\nrequires-python = \">=3.9\"\n"
        ),
        f"src/{pkg}/__init__.py": f'"""{name}."""\n\n__version__ = "0.1.0"\n',
        "tests/test_smoke.py": f"import {pkg}\n\n\ndef test_version():\n    assert {pkg}.__version__\n",
    }
    return dirs, files


TEMPLATES = {"php": php_template, "python": python_template}


def create_project(name: str, template: str = "php", force: bool = False,
                   base: Path = Path("."), out=print) -> Path:
    """Create the project under ``base`` and return its root path."""
    if not NAME_RE.match(name):
        raise ValueError("name must start with a letter and contain only letters, digits, '-' or '_'")
    if template not in TEMPLATES:
        raise ValueError(f"unknown template '{template}' (choose from: {', '.join(TEMPLATES)})")

    root = Path(base) / name
    dirs, files = TEMPLATES[template](name)

    for d in dirs:
        folder = root / d
        folder.mkdir(parents=True, exist_ok=True)
        (folder / ".gitkeep").touch()  # git doesn't track empty folders
        out(f"Created directory: {folder}")

    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not force:
            out(f"Skipped (already exists): {path}")
            continue
        # open() rather than write_text(newline=...), which needs Python 3.10+
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        out(f"Seeded file: {path}")

    return root


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dev-scaffold", description="Scaffold a new project.")
    parser.add_argument("name", help="project name (letters, digits, - and _)")
    parser.add_argument("-t", "--template", choices=sorted(TEMPLATES), default="php",
                        help="project template (default: php)")
    parser.add_argument("--force", action="store_true", help="overwrite existing seeded files")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)

    try:
        root = create_project(args.name, args.template, args.force)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Done: '{root}' is ready ({args.template} template).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
