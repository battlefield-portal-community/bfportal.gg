---
name: plan-issue
description: Turn the feature plan from the current conversation into one or more GitHub issues and cut a feature branch. Run this AFTER a plan is agreed (e.g. after plan mode) and BEFORE writing any code. Do not use once commits exist — use open-pr for that.
---

# plan-issue

Convert the plan produced in **this conversation** into well-formed GitHub issue(s) matching bfportal conventions, then cut a single feature branch to work on. A feature typically decomposes into several issues that later share one PR (e.g. #248/#249/#250 → PR #251).

## Preconditions
- A plan/spec has been discussed in this session. If no clear plan exists, ask the user to share or point to it — do NOT invent scope.
- Working tree is clean and on `main` (or an up-to-date base). If not, tell the user and stop; don't stash or switch over uncommitted work.

## Steps

1. **Split the plan into issues.** One issue per logical, independently-describable change (mirror how a feature breaks into backend/models/frontend pieces). A small plan may be a single issue; don't force a split.

2. **Draft each issue.** Do not re-plan; summarize what was agreed.
   - **Title**: imperative, concise, no trailing period. E.g. `Register BF6 scripts models and add migration`.
   - **Body**: match the house format —
     - One plain intro line describing the change.
     - A bulleted list of concrete specifics; wrap identifiers, files, and symbols in backticks (`` `ScriptsCategory` ``, `` `bf6.models` ``, `` `0003` ``).
     - **No "Part of the X feature" footer** — the PR will link these issues, so the relationship is captured there.

3. **Pick labels** per issue (pass each with its emoji exactly as `gh label list` shows):
   - Exactly one `type:*` — `type:backend 🖥`, `type:frontend 🏞`, `type:style 🎨`, or `type:3rd party 🧿`. If an issue spans backend+frontend, apply both.
   - `enhancement ✨✨` for new features/requests, `bug ⚠` for fixes.
   - Add a priority (`0 priority: High 🥇` / `1 priority: medium 🥈` / `2 priority: Low 🥉`) only if the user stated urgency; otherwise leave unset.
   - Do NOT add `Has PR` — that is applied by the `open-pr` skill.

4. **Show the user** the drafted title/body/labels for every issue. Get a thumbs-up (or edits) before creating — issue creation is outward-facing.

5. **Create the issues:**
   ```bash
   gh issue create --title "<title>" --body "<body>" \
     --label "enhancement ✨✨" --label "type:backend 🖥"
   ```
   Capture each issue number from the returned URLs.

6. **Cut ONE feature branch** from up-to-date `main`, named after the **feature** (kebab-case, descriptive — e.g. `bf6-scripts-snippets`), NOT after any issue number, since the branch/PR bundles all the issues:
   ```bash
   git fetch origin main
   git switch -c <feature-slug> origin/main
   ```

7. **Report** every issue number/URL and the branch name. Note the issue numbers so the eventual `open-pr` can link them all. Do not commit or push anything.

## Notes
- Never fabricate scope not present in the discussed plan.
- If `gh` isn't authenticated, tell the user to run `! gh auth login` rather than guessing.
