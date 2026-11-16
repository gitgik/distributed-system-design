"""Check notebook schemas without executing cells or rewriting files."""

import argparse
import json
from pathlib import Path
import sys

import nbformat
from nbformat.validator import iter_validate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="+", type=Path)
    paths = parser.parse_args(argv).notebooks
    failures = 0

    for path in paths:
        try:
            notebook = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(notebook, dict):
                raise ValueError("Expected a notebook JSON object")
            for field in ("nbformat", "nbformat_minor"):
                version = notebook.get(field)
                if not isinstance(version, int) or isinstance(version, bool):
                    raise ValueError(f"{field} must be an integer")
            # validate() can repair missing cell IDs before checking the schema.
            validation_error = next(iter_validate(notebook), None)
            if validation_error is not None:
                raise validation_error
        except (OSError, ValueError, nbformat.ValidationError) as error:
            message = (
                error.message
                if isinstance(error, nbformat.ValidationError)
                else str(error)
            )
            print(f"INVALID {path}: {message}", file=sys.stderr)
            failures += 1
        else:
            print(f"VALID {path}")

    print(f"Checked {len(paths)} notebook(s); {failures} invalid.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
