---
description: Run the full test suite with pytest and report results.
allowed-tools: Bash(.venv/Scripts/pytest.exe *)
---

Run the full test suite:

```
.venv/Scripts/pytest.exe tests/ -v
```

Report the number of passed/failed tests. If any tests fail, show the failure details clearly.
