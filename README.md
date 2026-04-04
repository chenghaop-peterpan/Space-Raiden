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

每次新增功能或修改遊戲邏輯時，**必須**同步補充以下兩類測試：

- **Smoke Test（冒煙測試）**：驗證頁面載入後的 DOM 初始狀態與基本互動，確認遊戲可正常開啟
- **Function Test（功能測試）**：直接呼叫遊戲 JS 函式，驗證單一邏輯行為（如 `startGame`、`fireLaser`、`explode`、移動）
- **Integration Test（整合測試）**：透過真實 game loop 驗收多系統協同行為（如 asteroid 自然生成、邊界 clamp）

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
    ├── test_smoke.py      # Smoke tests
    ├── test_function.py   # Function tests
    └── test_integration.py # Integration tests
```
