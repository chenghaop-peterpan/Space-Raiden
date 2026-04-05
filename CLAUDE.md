# CLAUDE.md

## 每次對話開始前

先讀 `docs/roadmap.md`，確認當前進度與待辦事項。

---

## 測試執行

```bash
.venv/Scripts/pytest.exe tests/ -v
```

不是 `pytest`，不是 `python -m pytest`。
本機：headed（有瀏覽器視窗）。CI（GitHub Actions）：headless（由 `CI` 環境變數自動切換）。

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

## 每次 Iteration 開發流程

```
1. 開 branch
   git checkout main && git pull
   git checkout -b feat/vX.Y.Z

2. 實作
   - 只改 space_dodge.html（遊戲邏輯）
   - 新增 / 修改 tests/
   - 更新 docs/spec.md（如有新 API 或架構異動）

3. 跑測試（確認全過）
   .venv/Scripts/pytest.exe tests/ -v

4. 補 changelog（必做，merge 前不可跳過）
   - 新增 changelog/vX.Y.Z.md（主題 / 新增 / 修改 / 修復 / 測試）
   - 更新 changelog/SUMMARY.md：新版本插入表格最上方（新的在上）

5. Commit & Push
   git add <files>
   git commit -m "feat(vX.Y.Z): ..."
   git push origin feat/vX.Y.Z

6. GitHub Actions 自動跑 CI（push 觸發）
   → 確認 Actions 綠燈

7. Merge to main + 刪 branch（必做，不等提醒）
   git checkout main
   git merge feat/vX.Y.Z --no-ff
   git push origin main
   git push origin --delete feat/vX.Y.Z
   git branch -d feat/vX.Y.Z

8. Tag
   git tag vX.Y.Z
   git push origin vX.Y.Z
```

---

## 版本號規則

| 類型 | 版號 |
|------|------|
| 破壞性變更 / 重大功能 | Major +1 |
| 新功能（向下相容） | Minor +1 |
| Bug 修復 / 小調整 | Patch +1 |
