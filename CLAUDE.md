# CLAUDE.md

## 測試執行

```bash
.venv/Scripts/pytest.exe tests/ -v
```

不是 `pytest`，不是 `python -m pytest`。

---

## 遊戲程式碼

唯一修改目標：`space_dodge.html`
不新增 JS / CSS 檔，不引入外部套件。

---

## Fixture 原則

| Fixture | 狀態 | 用途 |
|---------|------|------|
| `game_page` | `start`（黑箱） | smoke / integration |
| `playing_page` | 直接呼叫 `startGame()` 跳過 UI（白箱） | unit / functional / regression |

---

## 版本管理（每次發版必做）

1. 新增 `changelog/vX.Y.Z.md`（主題 / 新增 / 修改 / 修復 / 測試）
2. 更新 `changelog/SUMMARY.md`：新版本插入表格**最上方**（新的在上，舊的在下）
3. `git tag vX.Y.Z && git push origin vX.Y.Z`

---

## 瀏覽器設定

`headless=False`（在 `tests/conftest.py` 的 `browser_type_launch_args` fixture 設定）
