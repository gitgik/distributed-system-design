---
name: validate-notebooks
description: Validate notebook schemas, execute relevant notebooks with nbval, and check paired Markdown and notebook examples without rewriting outputs. Use for notebook, executable-example, or notebook-CI changes.
---

# Validate notebooks

## Select checks

1. Read `AGENTS.md`, the changed cells, matching Markdown, and any `executed_`
   counterpart. Inspect code before running it: a notebook can execute arbitrary
   code. Do not execute an untrusted submission without authorization.
2. Use the existing Python environment. If required modules are missing, create
   an isolated environment and install `requirements.txt`; no extra framework is
   needed. Use the same interpreter for schema checks, pytest, and kernels.
3. Schema validation, saved-output comparison, and behavior assertions establish
   different things. Choose the checks needed for the change. Older notebook
   formats are not invalid merely because they lack newer cell IDs.

## Check structure without executing cells

The helper reads JSON and validates its declared notebook format with `nbformat`.
It also checks cell ID uniqueness where IDs are required. It does not repair
inputs, rewrite files, upgrade formats, or execute cells. It requires explicit
paths and exits nonzero if any input is invalid or unreadable.

From the repository root, for all tracked notebooks in PowerShell:

```powershell
$notebooks = @(git ls-files -- '*.ipynb')
python .github\skills\validate-notebooks\scripts\validate_notebooks.py @notebooks
```

In a POSIX shell:

```sh
git ls-files -z -- '*.ipynb' | xargs -0 python .github/skills/validate-notebooks/scripts/validate_notebooks.py
```

Pass new, untracked notebook paths explicitly as well. The same helper runs in
the existing notebook CI job.

## Execute and test

- For changed code, run `python -m pytest --nbval --nbval-current-env` with the
  relevant notebook paths, their executed counterparts, and affected Python test
  files. Use `--nbval-cell-timeout=30 --nbval-kernel-startup-timeout=60` to bound
  execution; diagnose a timeout rather than treating it as success.
- For shared validation or CI changes, run `python -m pytest --nbval` across the
  repository, using `--nbval-current-env` when the selected interpreter must
  supply the kernel. CI tests Python 3.9, 3.10, and 3.11; a local run on one
  interpreter does not establish all-version compatibility.
- Add focused behavior assertions for a corrected invariant, not just "no
  exception." Cover the relevant Markdown/notebook representations without
  creating a second implementation solely for tests.
- When changing a validator, include a deliberately invalid input that must fail.
  When changing output comparison, prove a wrong saved output is rejected.
- Inspect the final diff. Preserve unrelated metadata and outputs; never discard
  expected output or relax comparison to hide a failure. For intentional output
  changes, regenerate only affected notebooks and explain the result.

Report commands, interpreter, paths, results, and any unexecuted checks. Do not
describe schema validity or an nbval pass as a production-correctness guarantee.
