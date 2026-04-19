# Roadmap — Space-Raiden

每次對話開始時，Claude 讀取此檔確認進度與待辦事項。

---

## 已完成

| 版本 | 內容 |
|------|------|
| v1.0.0 | 遊戲本體 + 基本 Playwright 測試套件 |
| v1.0.1 | 測試架構重構（smoke / functional / integration） + GitHub Pages |
| v1.0.2 | 五分類測試架構 + pyproject.toml markers，48 tests |
| v1.1.0 | AI 模式 + 模式選單狀態機（menu / ai_params） |
| v1.2.0 | AI 研究基礎設施：getGameState / executeCommand / Debug HUD（H 鍵） |
| v1.3.0 | Benchmark 系統：Canvas 趨勢圖 / HTML 歷史表格（B 鍵） / CSV 匯出（E 鍵） |
| v1.3.1 | GitHub Actions CI + 開發流程文件（CLAUDE.md） |
| v1.3.2 | CLAUDE.md 規則補強：changelog 必做、merge 後刪 branch |
| v1.3.3 | requirements.txt + roadmap.md 備忘錄機制 |
| v1.3.4 | CI 優化：Playwright caching + pip cache + 觸發條件精簡 |
| v1.3.5 | CI paths filter + 備忘錄同步 |
| v1.3.6 | CLAUDE.md 語言規則：只使用繁體中文或英文回覆 |
| v1.3.7 | Bugfix：結算/選單畫面 shake 殘留 + UX regression 測試 |
| v1.4.1 | CLAUDE.md Skills 提示補強：每次對話主動確認可用 /skill 指令 |
| v1.4.0 | Skills + MCP 基礎建設：/new-version、/test、/release、GitHub MCP |

---

## CI 改善 Backlog

| 狀態 | 項目 | 說明 |
|------|------|------|
| ✅ | requirements.txt | 統一管理依賴版本 |
| ✅ | Playwright browser caching | `actions/cache@v4`，key 綁定 playwright 版本 |
| ✅ | 觸發條件精簡 | 移除 `feat/**` push，feature branch 僅 PR 時觸發 |
| ✅ | paths filter | `space_dodge.html` / `tests/**` / `requirements.txt` / `.github/workflows/**` |
| ⬜ | smoke-first 分層執行 | PR 時先跑 smoke（快），merge 到 main 再跑全套 |

---

## 遊戲功能 Backlog

| 狀態 | 項目 |
|------|------|
| ⬜ | AI Phase 2：強化學習 / 更智慧的決策策略 |
| ⬜ | Benchmark 跨 session 持久化（localStorage） |
