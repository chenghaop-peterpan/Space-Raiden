---
description: Full automated release flow with user confirmation. Runs tests, commits, pushes, creates PR, waits for CI, merges, deletes branch, and tags.
allowed-tools: Bash(git *) Bash(.venv/Scripts/pytest.exe *) Bash("/c/Program Files/GitHub CLI/gh.exe" *)
---

## Release Flow

### Step 1: Gather Info (READ ONLY — do not execute yet)

Run these commands to gather information:
- `git status` — see modified files
- `git branch --show-current` — get current branch name
- `git diff --stat HEAD` — summarize changes

### Step 2: Show Confirmation Summary

Present the following to the user and **WAIT for explicit confirmation (OK / yes) before proceeding**:

```
=== Release Confirmation ===
Branch:         <current branch>
Version:        <extracted from branch name>
Files to commit:
  - <list of modified files>

Proposed commit message:
  <type(vX.Y.Z): short description>

PR title:
  <same as commit message>

Flow:
  1. Run tests
  2. git add → commit → push
  3. Create PR
  4. Wait for CI
  5. Merge to main
  6. Delete branch (remote + local)
  7. Tag <version>

Proceed? (yes / no)
```

### Step 3: Execute (ONLY after user says yes/ok)

Execute in order — stop immediately if any step fails:

1. **Run tests**
   ```
   .venv/Scripts/pytest.exe tests/ -v
   ```
   If tests fail → report failure, stop, do NOT proceed.

2. **Commit**
   ```
   git add <modified files>
   git commit -m "<type(vX.Y.Z): description>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
   ```

3. **Push**
   ```
   git push origin <branch>
   ```

4. **Create PR**
   ```
   "/c/Program Files/GitHub CLI/gh.exe" pr create \
     --title "<commit message first line>" \
     --body "<summary of changes and test plan>"
   ```

5. **Wait for CI** (poll every 20 seconds, max 5 minutes)
   ```
   "/c/Program Files/GitHub CLI/gh.exe" run list --branch <branch> --limit 1
   ```
   If CI fails → report failure, stop, do NOT merge.

6. **Merge**
   ```
   git checkout main
   git merge <branch> --no-ff -m "Merge <branch> into main"
   git push origin main
   ```

7. **Delete branch**
   ```
   git push origin --delete <branch>
   git branch -d <branch>
   ```

8. **Tag**
   ```
   git tag <version>
   git push origin <version>
   ```

9. Report success with final summary.
