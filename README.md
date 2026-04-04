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

- **UI Test（介面測試）**：實際開啟瀏覽器，模擬使用者操作並驗證畫面元素（如按鍵、分數、生命顯示）
- **API Test（功能測試）**：透過 Playwright 呼叫遊戲 JS 函式，驗證遊戲邏輯狀態（如 `startGame`、`fireLaser`、`spawnAsteroid`）

詳細環境設定與測試撰寫規範請參閱 [`docs/testSpec.md`](docs/testSpec.md)

## 技術規格

詳見 [`docs/spec.md`](docs/spec.md)

## 檔案結構

```
second_project/
├── space_dodge.html       # 遊戲本體（HTML + CSS + JavaScript 單檔）
├── README.md
├── docs/
│   ├── spec.md            # 技術規格文件
│   └── testSpec.md        # 測試規範文件
└── tests/
    ├── conftest.py        # pytest fixture（本機伺服器）
    ├── test_ui.py         # UI tests
    └── test_api.py        # API tests
```
