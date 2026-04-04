🎮 **線上遊玩**：https://chenghaop-peterpan.github.io/Space-Raiden/

# 太空梭躲避隕石

一款以 HTML5 Canvas 實作的瀏覽器太空射擊遊戲。玩家駕駛太空梭，在不斷湧入的隕石雨中求生，同時發射雷射摧毀障礙。

## 快速開始

直接用瀏覽器開啟 `space_dodge.html` 即可遊玩，無需安裝任何套件。

## 操控方式

| 按鍵 | 動作 |
|------|------|
| 方向鍵 / WASD | 移動太空梭 |
| Space | 發射雷射 / 開始遊戲 |
| Enter | 開始遊戲 |

## 遊戲機制

- **生命值**：共 3 條生命，被隕石擊中扣 1 條，並進入 2 秒無敵時間
- **分數**：每 6 幀自動累積 1 分；擊毀小隕石 +15 分，大隕石 +30 分
- **等級**：每累積 300 分升一級，隕石速度與生成頻率隨等級提升
- **雷射冷卻**：每次發射後需等待 12 幀才能再次發射

## 測試規範

本專案採用五層測試架構，每次新增功能或修改邏輯時依需求補充：

| 類型 | 視角 | 說明 |
|------|------|------|
| **Smoke Test** | 黑箱 | 頁面基本可用性，開機確認 |
| **Unit Test** | 白箱 | 純公式驗算（碰撞、分數、等級、生成頻率） |
| **Functional Test** | 白箱 | 單一 game feature 行為（startGame、fireLaser、explode 等） |
| **Integration Test** | 白/黑箱 | 多系統串聯，依賴真實 game loop |
| **Regression Test** | 黑箱 | 邊界情境守衛，防止已知行為退化 |

**快速執行：**
```bash
pytest -m "unit or smoke"      # ~15s 改完立即跑
pytest -m "not integration"    # ~40s commit 前
pytest                         # ~90s 上線前全跑
```

詳細環境設定與測試撰寫規範請參閱 [`docs/testSpec.md`](docs/testSpec.md)

## 版本記錄

各版本開發主題與改動內容詳見 [`changelog/SUMMARY.md`](changelog/SUMMARY.md)

## 技術規格

詳見 [`docs/spec.md`](docs/spec.md)

## 檔案結構

```
second_project/
├── space_dodge.html       # 遊戲本體（HTML + CSS + JavaScript 單檔）
├── README.md
├── changelog/
│   ├── SUMMARY.md         # 所有版本摘要
│   └── v1.0.0.md          # v1.0.0 改動記錄
├── docs/
│   ├── spec.md            # 技術規格文件
│   └── testSpec.md        # 測試規範文件
└── tests/
    ├── conftest.py        # pytest fixture（本機伺服器）
    ├── test_smoke.py        # Smoke tests      (10)
    ├── test_unit.py         # Unit tests       (8)
    ├── test_functional.py   # Functional tests (16)
    ├── test_integration.py  # Integration tests (8)
    └── test_regression.py   # Regression tests  (6)
```
