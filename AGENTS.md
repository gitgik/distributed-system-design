# Working in this repository

The articles and examples are the product. Favor a precise explanation, a worked
counterexample, or a small executable check over a new framework or service.

- Read the whole affected section before editing. State assumptions and limits;
  distinguish a teaching model from a production guarantee.
- Check the matching Markdown, notebook, and any `executed_` notebook. Keep the
  affected explanation or code consistent without unrelated formatting changes.
- Preserve notebook metadata and outputs unless the change requires updating them.
  Never clear outputs just to make a test pass.
- Use the existing Python requirements and GitHub Actions. Add dependencies only
  when the change needs them; do not install them merely to edit prose.
- Preserve unrelated work. Stage explicit paths, inspect the staged diff, and do
  not merge a PR unless asked.
- Write direct PR descriptions: the problem, the change, actual validation, and
  material limitations. Do not invent benchmark results or claim unrun checks.
- Keep contributions original. Do not import private source, internal procedures,
  identifying details, or credentials from another repository.

## Focused workflows

Repository skills live in `.github/skills/`. Copilot CLI discovers them there;
other tools can read the same instructions directly.

- [Create a PR](.github/skills/create-pr/SKILL.md)
- [Review a PR or local changes](.github/skills/review-pr/SKILL.md)
- [Validate notebooks](.github/skills/validate-notebooks/SKILL.md)
- [Review a system-design explanation](.github/skills/review-design-content/SKILL.md)
