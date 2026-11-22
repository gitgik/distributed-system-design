import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / ".github" / "skills" / "validate-notebooks" / "scripts" / "validate_notebooks.py"
)
SPEC = importlib.util.spec_from_file_location("validate_notebooks", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load notebook validator: {SCRIPT}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class NotebookValidationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.notebook = {
            "nbformat": 4,
            "nbformat_minor": 2,
            "metadata": {},
            "cells": [{
                "cell_type": "code",
                "metadata": {},
                "source": "raise AssertionError('Schema checks must not execute cells')",
                "execution_count": None,
                "outputs": [],
            }],
        }

    def run_validator(self, *paths):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = VALIDATOR.main([str(path) for path in paths])
        return result, stdout.getvalue(), stderr.getvalue()

    def test_accepts_legacy_notebook_without_execution_or_rewriting(self):
        path = self.root / "legacy.ipynb"
        path.write_text(json.dumps(self.notebook), encoding="utf-8")
        original = path.read_bytes()

        result, _, errors = self.run_validator(path)

        self.assertEqual(result, 0)
        self.assertEqual(errors, "")
        self.assertEqual(path.read_bytes(), original)

    def test_rejects_malformed_json_and_invalid_notebook_structure(self):
        modern = {**self.notebook, "nbformat_minor": 5}
        without_cells = modern.copy()
        del without_cells["cells"]
        cases = {
            "malformed-json": "{",
            "invalid-root": "[]",
            "invalid-cells": json.dumps({**self.notebook, "cells": "not a list"}),
            "invalid-version": json.dumps({**self.notebook, "nbformat_minor": "2"}),
            "missing-required-id": json.dumps(modern),
            "missing-cells": json.dumps(without_cells),
            "null-cells": json.dumps({**modern, "cells": None}),
        }
        for name, contents in cases.items():
            with self.subTest(case=name):
                path = self.root / f"{name}.ipynb"
                path.write_text(contents, encoding="utf-8")

                result, _, errors = self.run_validator(path)

                self.assertEqual(result, 1)
                self.assertIn(str(path), errors)
                self.assertIn("INVALID", errors)

    def test_requires_unique_modern_cell_ids(self):
        path = self.root / "modern.ipynb"
        cell = {**self.notebook["cells"][0], "id": "code-cell"}
        modern = {**self.notebook, "nbformat_minor": 5, "cells": [cell]}
        path.write_text(json.dumps(modern), encoding="utf-8")
        result, _, errors = self.run_validator(path)
        self.assertEqual(result, 0)
        self.assertEqual(errors, "")

        modern["cells"].append(cell.copy())
        path.write_text(json.dumps(modern), encoding="utf-8")
        result, _, errors = self.run_validator(path)
        self.assertEqual(result, 1)
        self.assertIn("unique", errors)

    def test_reports_unreadable_input(self):
        path = self.root / "missing.ipynb"

        result, _, errors = self.run_validator(path)

        self.assertEqual(result, 1)
        self.assertIn(str(path), errors)

    def test_checks_remaining_inputs_after_a_failure(self):
        missing = self.root / "missing.ipynb"
        malformed = self.root / "malformed.ipynb"
        malformed.write_text(
            json.dumps({**self.notebook, "nbformat_minor": 5, "cells": None}),
            encoding="utf-8",
        )
        valid = self.root / "valid.ipynb"
        valid.write_text(json.dumps(self.notebook), encoding="utf-8")

        result, output, errors = self.run_validator(missing, malformed, valid)

        self.assertEqual(result, 1)
        self.assertIn(f"VALID {valid}", output)
        self.assertIn(str(missing), errors)
        self.assertIn(str(malformed), errors)


if __name__ == "__main__":
    unittest.main()
