# 測試規範文件 — 太空梭躲避隕石

## 概覽

本專案採用 **Python + Playwright** 進行瀏覽器自動化測試，分為兩大類：

| 測試類型 | 說明 | 檔案 |
|----------|------|------|
| Function Test | 單一獨立功能驗證，每個測試只觸發一個事件或機制 | `tests/test_function.py` |
| Integration Test | 多功能互動驗證，測試兩個以上事件互相影響的結果 | `tests/test_integration.py` |

> 舊有的 `test_ui.py` / `test_api.py` 將依此規範逐步遷移至新分類。

---

## 環境建立

### 1. 建立虛擬環境

```bash
python -m venv .venv
```

### 2. 啟動虛擬環境

```bash
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. 安裝所有必要套件

```bash
pip install pytest playwright pytest-playwright pytest-html
```

### 4. 安裝 Playwright 瀏覽器核心

```bash
playwright install chromium
```

---

## 必裝套件清單

| 套件 | 版本需求 | 用途 |
|------|----------|------|
| `pytest` | >= 7.0 | 測試框架 |
| `playwright` | >= 1.40 | 瀏覽器自動化核心 |
| `pytest-playwright` | >= 0.4 | pytest 與 Playwright 整合 |
| `pytest-html` | >= 4.0 | 產生 HTML 測試報告 |

---

## 測試目錄結構

```
second_project/
├── space_dodge.html
├── docs/
│   └── testSpec.md            ← 本文件
└── tests/
    ├── conftest.py            # 共用 fixture：本機伺服器 + game_page
    ├── test_function.py       # Function Tests（單一功能）
    └── test_integration.py    # Integration Tests（多功能互動）
```

---

## conftest.py — 共用 Fixture

```python
import pytest
import threading
import http.server
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8765

@pytest.fixture(scope="session", autouse=True)
def local_server():
    """啟動本機靜態伺服器以供 Playwright 存取 HTML 檔案"""
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("localhost", PORT), handler)
    os.chdir(BASE_DIR)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    yield
    httpd.shutdown()

@pytest.fixture
def game_page(page):
    """開啟遊戲頁面並等待畫布載入"""
    page.goto(f"http://localhost:{PORT}/space_dodge.html")
    page.wait_for_selector("#canvas")
    return page
```

---

## Function Test 規範

### 定義

> 單一獨立功能：每個測試只觸發 **一個事件或機制**，不依賴其他功能的輸出。

### 原則

- 使用 `page.keyboard.press()` 觸發按鍵事件（可視化）
- 使用 `page.evaluate()` 原子性讀取或設定狀態
- 每個測試只驗證一個功能點
- 命名規則：`test_<功能名稱>()`

### 測試項目清單

#### 遊戲開啟

| 測試名稱 | 操作 | 驗證點 |
|----------|------|--------|
| `test_press_space_starts_game` | 按 Space | `state == 'playing'` |
| `test_press_enter_starts_game` | 按 Enter | `state == 'playing'` |
| `test_start_resets_score` | startGame() | `score == 0` |
| `test_start_resets_lives` | startGame() | `lives == 3` |
| `test_start_clears_all_entities` | startGame() | asteroids/lasers/particles/explosions 全為 0 |

#### 畫面元素

| 測試名稱 | 操作 | 驗證點 |
|----------|------|--------|
| `test_canvas_dimensions` | 載入頁面 | width=480, height=640 |
| `test_initial_score_display` | 載入頁面 | `#score` = "0" |
| `test_initial_lives_display` | 載入頁面 | `#lives` = "❤️❤️❤️" |
| `test_initial_level_display` | 載入頁面 | `#level` = "1" |
| `test_hint_text_visible` | 載入頁面 | `#hint` 含 "Space" |

#### 玩家移動

| 測試名稱 | 操作 | 驗證點 |
|----------|------|--------|
| `test_move_left` | 按住 ArrowLeft / A | `player.x` 減少 |
| `test_move_right` | 按住 ArrowRight / D | `player.x` 增加 |
| `test_move_up` | 按住 ArrowUp / W | `player.y` 減少 |
| `test_move_down` | 按住 ArrowDown / S | `player.y` 增加 |
| `test_boundary_left` | 持續向左移動 | `player.x` 不小於 `player.w/2` |
| `test_boundary_right` | 持續向右移動 | `player.x` 不大於 `W - player.w/2` |
| `test_boundary_top` | 持續向上移動 | `player.y` 不小於 `player.h/2` |
| `test_boundary_bottom` | 持續向下移動 | `player.y` 不大於 `H - player.h/2` |

#### 發射雷射

| 測試名稱 | 操作 | 驗證點 |
|----------|------|--------|
| `test_fire_laser_creates_projectile` | 遊戲中按 Space | `lasers.length == 1` |
| `test_fire_laser_sets_cooldown` | fireLaser() | `laserCooldown == 12` |
| `test_cooldown_prevents_double_fire` | 連按兩次 Space | `lasers.length == 1` |

#### 分數系統

| 測試名稱 | 操作 | 驗證點 |
|----------|------|--------|
| `test_score_increases_over_time` | 遊戲運行 2 秒 | `#score` > 0 |
| `test_level_formula_300` | score=300 | level=2 |
| `test_level_formula_600` | score=600 | level=3 |

#### 隕石生成

| 測試名稱 | 操作 | 驗證點 |
|----------|------|--------|
| `test_asteroids_spawn_naturally` | 遊戲運行 3 秒 | `asteroids.length` > 0 |
| `test_asteroid_has_valid_radius` | spawnAsteroid() | `r >= 18` |
| `test_asteroid_moves_downward` | spawnAsteroid() | `vy > 0` |
| `test_asteroid_has_hp` | spawnAsteroid() | `hp >= 1` |
| `test_large_asteroid_has_more_hp` | spawnAsteroid(r>32) | `hp == 2` |

#### 爆炸特效

| 測試名稱 | 操作 | 驗證點 |
|----------|------|--------|
| `test_small_explosion_particles` | explode(false) | `particles.length >= 14` |
| `test_big_explosion_more_particles` | explode(true) | `particles.length >= 28` |
| `test_big_explosion_screen_shake` | explode(true) | `shake == 14` |

---

## Integration Test 規範

### 定義

> 多功能互動：每個測試涉及 **兩個以上獨立事件的互動結果**，驗證系統整合行為。

### 原則

- 需先完成對應 Function Test 才能撰寫 Integration Test
- 模擬完整的使用者操作流程
- 驗證點為互動後的最終狀態（DOM 或 JS 狀態）
- 命名規則：`test_<事件A>_and_<事件B>_<結果>()`

### 測試項目清單

#### 飛機 × 隕石

| 測試名稱 | 情境 | 驗證點 |
|----------|------|--------|
| `test_collision_reduces_lives` | 飛機撞隕石 | `lives` 從 3 變 2，`#lives` DOM 更新 |
| `test_collision_triggers_invincibility` | 飛機撞隕石 | `invincible > 0`（無敵幀數啟動） |
| `test_three_collisions_causes_gameover` | 連撞 3 次 | `state == 'gameover'` |
| `test_moving_into_asteroid_loses_life` | 玩家向隕石方向移動 → 碰撞 | `lives` 減少 |

#### 雷射 × 隕石

| 測試名稱 | 情境 | 驗證點 |
|----------|------|--------|
| `test_laser_destroys_small_asteroid` | 雷射打小隕石（hp=1） | asteroid 從陣列移除 |
| `test_laser_scores_on_small_asteroid` | 雷射打小隕石 | `score` 增加 15 |
| `test_laser_scores_on_big_asteroid` | 雷射打大隕石 | `score` 增加 30 |
| `test_large_asteroid_needs_two_hits` | 雷射打大隕石（hp=2）兩次 | 第一發 hp=1，第二發移除 |
| `test_laser_explosion_on_hit` | 雷射擊中隕石 | `explosions.length > 0` 且 `particles.length > 0` |

#### 移動 × 發射

| 測試名稱 | 情境 | 驗證點 |
|----------|------|--------|
| `test_move_and_shoot_simultaneously` | 按住方向鍵同時按 Space | 玩家位置改變 且 `lasers.length >= 1` |
| `test_laser_position_matches_player` | 發射雷射 | `lasers[0].x` 接近 `player.x` |

#### 分數 × 等級 × 隕石

| 測試名稱 | 情境 | 驗證點 |
|----------|------|--------|
| `test_level_up_increases_asteroid_speed` | score=300（level=2） vs level=1 | level 2 隕石 `vy` 平均值更大 |
| `test_level_up_increases_spawn_rate` | level=5 | 隕石生成頻率比 level=1 更快 |

#### 遊戲流程

| 測試名稱 | 情境 | 驗證點 |
|----------|------|--------|
| `test_gameover_then_restart_resets_state` | 遊戲結束後按 Space 重開 | score=0, lives=3, level=1, state='playing' |
| `test_score_accumulates_from_survival_and_kills` | 存活時間 + 擊殺隕石 | 最終分數 > 純存活分數 |

---

## 執行測試

### 基本指令

```bash
# 全部測試
pytest tests/ -v

# 只跑 Function Tests
pytest tests/test_function.py -v

# 只跑 Integration Tests
pytest tests/test_integration.py -v

# 可視化模式（看瀏覽器操作）
pytest tests/ -v -s --headed --slowmo 2000
```

### 產生報告

```bash
pytest tests/ -v --html=report.html --self-contained-html
```

---

## 新增測試檢查清單

每次新增功能或修改遊戲邏輯時，依序確認：

- [ ] 為新功能補充 **Function Test**（單一行為驗證）
- [ ] 為新功能與現有系統的互動補充 **Integration Test**
- [ ] 本機執行 `pytest tests/ -v` 全部通過
- [ ] 可視化模式跑過一次確認瀏覽器行為符合預期

---

## 測試分類判斷原則

> 不確定要放哪類時，參考以下問題：

| 問題 | 答案 → 分類 |
|------|------------|
| 這個測試只涉及一個功能/按鍵/函式嗎？ | 是 → Function Test |
| 測試結果依賴兩個以上系統的互動嗎？ | 是 → Integration Test |
| 可以不啟動其他功能就單獨驗證嗎？ | 是 → Function Test |
| 需要先觸發 A 才能觀察 B 的變化嗎？ | 是 → Integration Test |
