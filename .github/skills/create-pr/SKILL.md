---
name: create-pr
description: Prepare and publish a focused GitHub pull request for this repository. Use when asked to open a PR or prepare changes for review, not to merge a PR.
---

# Create a pull request

## Establish scope

1. Read `AGENTS.md`. Inspect `git status --short`, the current branch, and staged
   changes. Identify the files belonging to this task; a dirty file is not proof
   that it belongs in the PR.
2. Resolve the GitHub repository and default branch with
   `gh repo view --json nameWithOwner,defaultBranchRef`. Confirm any requested
   alternative base. Fetch that base and inspect both the branch commits and the
   full three-dot diff against it, plus intended uncommitted changes.
3. Use a feature branch. If it contains unrelated commits or depends on an
   unmerged PR, stop and resolve the scope with the user rather than quietly
   publishing a mixed or stacked PR.

## Validate and describe

1. Run checks appropriate to the actual change. For notebooks or executable
   examples, follow the [notebook workflow](../validate-notebooks/SKILL.md).
   For design claims, use the [content review](../review-design-content/SKILL.md).
   Prose-only changes do not need a gratuitous runtime suite.
2. Read the resulting diff, including new files, and run `git diff --check`.
   Check Markdown links and paired representations. Fix failures caused by this
   change; distinguish unrelated failures from passes.
3. Prepare a short title and body covering the defect or need, the solution,
   commands and results, and any meaningful limit or risk. Include issue links
   only when they genuinely apply. Do not add a deployment plan to a prose fix.
4. Preview the intended files, title, and body. Obtain approval to commit, push,
   and publish unless those exact actions and scope are already approved. Ask
   whether GitHub Copilot review is wanted, without a suggested answer. Do not
   carry another PR's review choice forward without permission.

## Publish and verify

1. Stage only approved paths and inspect `git diff --cached`. Confirm the staged
   file set, run `git diff --cached --check`, and create a new commit. Honor the
   active attribution requirements without inventing identities.
2. Push explicitly to the feature branch, setting its upstream. An upstream that
   still points to the base branch is not a safe push destination. Do not amend,
   force-push, or bypass hooks without authorization.
3. Use `gh pr create` with an explicit base and head and a body file outside the
   tracked source tree. Read back the PR's files, head, base, title, and body.
4. If requested, use `gh pr edit <number> --add-reviewer @copilot`. Confirm the
   request; do not describe a submitted comment as a formal approval.
5. Watch the PR checks with `gh pr checks <number> --watch`. Inspect failures
   before declaring the PR ready. Never disable a check just to get a green
   status; a justified suppression must be narrow and explained.
6. Report the PR link, meaningful change, checks, and any remaining blockers.
   Leave the PR unmerged.
