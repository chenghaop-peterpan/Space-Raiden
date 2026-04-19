---
description: Run the full test suite with pytest and report results.
allowed-tools: Bash(CI=true .venv/Scripts/pytest.exe *)
---

Run the full test suite in headless mode:

```
CI=true .venv/Scripts/pytest.exe tests/ -v
```

Report the number of passed/failed tests. If any tests fail, show the failure details clearly.
