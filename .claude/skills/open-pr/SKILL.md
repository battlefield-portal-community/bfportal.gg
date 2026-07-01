---
name: open-pr
description: Open a GitHub PR for the current feature branch, link it to all the issues it resolves, and apply the Has PR label to each. Run this once you have real commits on a feature branch created by plan-issue. One PR typically bundles several issues.
---

# open-pr

Open a pull request for the work on the current feature branch and wire it to **all** the issues it resolves, matching bfportal conventions. A feature branch usually closes multiple issues (e.g. PR #251 closed #248, #249, #250).

## Preconditions
- You are on a feature branch (not `main`), and it has at least one commit ahead of `main`.

## Steps

1. **Determine which issues this PR closes.** The branch is named after the feature, not an issue, so gather the set explicitly:
   - Prefer the issue numbers created by `plan-issue` earlier in this session.
   - Otherwise ask the user, or cross-check open issues that lack the `Has PR` label:
     ```bash
     gh issue list --state open --search '-label:"Has PR"'
     ```
   - Confirm the final list with the user before proceeding.

2. **Sync the branch:**
   ```bash
   git push -u origin HEAD
   ```

3. **Draft the PR:**
   - **Title**: a conventional-commit style summary of the whole feature (`feat: ...`, `fix: ...`) consistent with the repo's history.
   - **Body**: brief summary of what changed, then a bulleted `- Closes #<N>` line **for each** issue. Use `-` list items so GitHub renders each issue's title inline:
     ```
     - Closes #248
     - Closes #249
     - Closes #250
     ```

4. **Show the user** the title, body, and the full issue list before creating — PR creation is outward-facing.

5. **Create the PR** against `main`:
   ```bash
   gh pr create --base main --title "<title>" --body "<body>"
   ```
   Add `--draft` if the user says the work isn't ready for review.

6. **Apply the `Has PR` label to every linked issue:**
   ```bash
   for n in 248 249 250; do gh issue edit "$n" --add-label "Has PR"; done
   ```

7. **Report** the PR URL and the issues it closes.

## Notes
- If some commits look unrelated to the listed issues, flag the mismatch to the user instead of forcing the links.
- If `gh` isn't authenticated, tell the user to run `! gh auth login`.
