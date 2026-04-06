---
description: Start a new version branch from main. Usage: /new-version feat/v1.5.0 or /new-version bugfix/v1.4.1
allowed-tools: Bash(git *)
---

Create a new version branch: $ARGUMENTS

Steps:
1. `git checkout main`
2. `git pull`
3. `git checkout -b $ARGUMENTS`

After creating the branch, confirm to the user which branch is now active.
