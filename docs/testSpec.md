# 測試規範文件 — 太空梭躲避隕石

## 概覽

本專案採用 **Python + Playwright** 進行瀏覽器自動化測試，依測試目的分為五類：

| 測試類型 | 視角 | 說明 | 檔案 | 數量 |
|----------|------|------|------|------|
| Smoke Test | 黑箱 | 頁面基本可用性，開機確認 | `tests/test_smoke.py` | 10 |
| Unit Test | 白箱 | 純公式與算法驗算，最小單元 | `tests/test_unit.py` | 8 |
| Functional Test | 白箱 | 單一 game feature 行為驗收 | `tests/test_functional.py` | 16 |
| Integration Test | 白/黑箱 | 多系統串聯，依賴真實 game loop | `tests/test_integration.py` | 8 |
| Regression Test | 黑箱 | 邊界情境與防 bug 復發守衛 | `tests/test_regression.py` | 6 |
| **合計** | | | | **48** |

### 白箱 vs 黑箱

- **白箱**：透過 `page.evaluate()` 存取 JS 內部變數與函式（state、lives、score、lasers 等）
- **黑箱**：只透過鍵盤操作與 DOM 觀察（`#score`、`#lives`、`#level` 等元素）

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

## 專案設定：pyproject.toml

pytest marker 在 `pyproject.toml` 統一管理：

```toml
[tool.pytest.ini_options]
markers = [
    "smoke:       基本頁面可用性，開機確認（黑箱）",
    "unit:        純公式與算法驗算，最小單元（白箱）",
    "functional:  單一 game feature 行為驗收（白箱）",
    "integration: 多系統串聯，依賴 game loop（白/黑箱）",
    "regression:  邊界情境與防 bug 復發守衛（黑箱）",
]
```

每個測試檔以 `pytestmark` 宣告所屬分類：

```python
import pytest
pytestmark = pytest.mark.functional  # 或 smoke / unit / integration / regression
```

---

## 測試目錄結構

```
second_project/
├── pyproject.toml                 # pytest marker 設定
├── space_dodge.html
├── docs/
│   └── testSpec.md               ← 本文件
└── tests/
    ├── conftest.py               # 共用 fixture：本機伺服器 + game_page
    ├── test_smoke.py             # Smoke Tests（黑箱，10 項）
    ├── test_unit.py              # Unit Tests（白箱，8 項）
    ├── test_functional.py        # Functional Tests（白箱，16 項）
    ├── test_integration.py       # Integration Tests（白/黑箱，8 項）
    └── test_regression.py        # Regression Tests（黑箱，6 項）
```

---

## Fixture 設計原則（核心概念）

### 兩個 Fixture，兩種視角

測試 Fixture 依視角分為兩種，**選用哪個 fixture 就決定了測試的性質**：

| Fixture | 起始狀態 | 進入方式 | 適用測試類型 |
|---------|----------|----------|-------------|
| `game_page` | `state = 'start'`（遊戲開頭畫面） | 頁面載入，等待 `#canvas` | Smoke、Integration、Regression |
| `playing_page` | `state = 'playing'`（直接進入遊戲） | JS 呼叫 `startGame('player')` | Unit、Functional |

### 設計理由

**黑箱測試用 `game_page`**：從使用者視角出發，透過鍵盤操作導航整個 UI 流程（start → menu → playing），觀察 DOM 元素與遊戲反應。

**白箱測試用 `playing_page`**：直接繞過選單 UI，以 JS 啟動遊戲核心，確保畫面與遊戲狀態一致。這樣測試時瀏覽器視窗顯示的是實際遊戲畫面，而不是停在選單，避免視覺混淆與 `frameCount` 累積的副作用。

```
黑箱（game_page）：  載入 → start 畫面 → [鍵盤 Space×2] → playing
白箱（playing_page）：載入 → [JS startGame()] → playing（直接）
```

### 錯誤示範

```python
# ❌ 白箱測試用 game_page + 按 Space → 停在 menu 畫面，視覺混淆
def test_collision(game_page):
    game_page.keyboard.press("Space")  # → 進入 menu，不是 playing
    game_page.evaluate("() => update()")

# ✓ 白箱測試用 playing_page → 直接在 playing 狀態執行
def test_collision(playing_page):
    playing_page.evaluate("() => update()")
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

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """強制 headed 模式，測試時可看到瀏覽器畫面"""
    return {**browser_type_launch_args, "headless": False}

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
    """黑箱測試用：開啟遊戲頁面，停在 start 畫面（state='start'）"""
    page.goto(f"http://localhost:{PORT}/space_dodge.html")
    page.wait_for_selector("#canvas")
    return page

@pytest.fixture
def playing_page(game_page):
    """白箱測試用：直接以 JS 啟動遊戲，跳過選單 UI（state='playing'）"""
    game_page.evaluate("() => startGame('player')")
    return game_page
```

---

## 執行測試

### 開發流程建議

```bash
# 改完立即跑（~15s）
pytest -m "unit or smoke"

# commit 前跑（~40s）
pytest -m "not integration"

# PR / 上線前全跑（~90s）
pytest
```

### 按分類執行

```bash
pytest -m smoke          # ~10s  開機確認
pytest -m unit           # ~5s   公式驗算
pytest -m functional     # ~30s  功能行為
pytest -m integration    # ~60s  系統串聯
pytest -m regression     # ~15s  邊界防守
```

### 其他選項

```bash
# 詳細輸出
pytest tests/ -v -s

# 可視化模式（看瀏覽器操作）
pytest tests/ -v -s --headed --slowmo 2000

# 產生 HTML 報告
pytest tests/ -v --html=report.html --self-contained-html
```

---

## Smoke Test 規範

### 定義

> 頁面載入後的 DOM 初始狀態與基本互動，只觀察畫面元素，不碰 JS 內部。

### 測試項目清單

| 測試名稱 | 操作 | 驗證點 |
|----------|------|--------|
| `test_canvas_dimensions` | 載入頁面 | width=480, height=640 |
| `test_canvas_is_visible` | 載入頁面 | `#canvas` 可見 |
| `test_initial_score_is_zero` | 載入頁面 | `#score` = "0" |
| `test_initial_lives_display` | 載入頁面 | `#lives` = "❤️❤️❤️" |
| `test_initial_level_is_one` | 載入頁面 | `#level` = "1" |
| `test_press_space_starts_game` | 按 Space | `state == 'playing'` |
| `test_press_enter_starts_game` | 按 Enter | `state == 'playing'` |
| `test_score_increases_over_time` | 等 2 秒 | `#score` > 0 |
| `test_hint_text_visible` | 載入頁面 | `#hint` 含 "Space" |
| `test_ui_bar_visible` | 載入頁面 | `#ui` 可見 |

---

## Unit Test 規範

### 定義

> 單一公式或算法的正確性驗算，不依賴 game loop，結果完全確定。

### 原則

- 透過 `page.evaluate()` 直接執行公式，不依賴遊戲狀態
- 每個測試驗證一條公式在多個邊界值的行為
- 若遊戲程式碼修改了任何公式，這類測試最先失敗

### 測試項目清單

| 測試名稱 | 驗證公式 | 邊界值 |
|----------|----------|--------|
| `test_level_formula_boundaries` | `1 + floor(score/300)` | score: 0, 299, 300, 600, 900 |
| `test_collision_player_radius` | `dist < a.r + 16` | r=20 → threshold=36 |
| `test_collision_laser_radius` | `dist < a.r + 4` | r=20 → threshold=24 |
| `test_boundary_clamp_x` | `max(w/2, min(W-w/2, x))` | 越界、邊界、中間值 |
| `test_boundary_clamp_y` | `max(h/2, min(H-h/2, y))` | 越界、邊界、中間值 |
| `test_score_small_asteroid` | `r <= 28 → +15` | r=28 |
| `test_score_large_asteroid` | `r > 28 → +30` | r=29 |
| `test_spawn_interval_formula` | `max(10, 28 - level*3)` | level: 1, 3, 6, 9 |

---

## Functional Test 規範

### 定義

> 單一 game feature 的完整行為驗收，直接呼叫 JS function，結果立即可讀。

### 原則

- 使用 `page.evaluate()` 原子性呼叫 game function 並讀取結果
- 每個測試只驗證一個功能點
- 命名規則：`test_<feature>_<expected_behavior>()`

### 測試項目清單

#### 遊戲啟動（2 項）
| 測試名稱 | 驗證點 |
|----------|--------|
| `test_startgame_resets_state` | state=playing, score=0, lives=3, level=1 |
| `test_startgame_clears_entities` | asteroids/lasers/explosions/particles 全為 0 |

#### 雷射（2 項）
| 測試名稱 | 驗證點 |
|----------|--------|
| `test_fire_laser_adds_projectile` | lasers.length=1, laserCooldown=12 |
| `test_fire_laser_respects_cooldown` | 連發兩次 → lasers.length=1 |

#### 爆炸特效（3 項）
| 測試名稱 | 驗證點 |
|----------|--------|
| `test_explode_small_generates_particles` | particles >= 14, explosions >= 1 |
| `test_explode_big_generates_more_particles` | particles >= 28, explosions >= 1 |
| `test_explode_big_triggers_screen_shake` | shake == 14 |

#### 等級（1 項）
| 測試名稱 | 驗證點 |
|----------|--------|
| `test_level_formula` | score=600 → DOM #level=3, JS level=3 |

#### 玩家移動（4 項）
| 測試名稱 | 驗證點 |
|----------|--------|
| `test_move_left` | ArrowLeft → player.x 減少 |
| `test_move_right` | ArrowRight → player.x 增加 |
| `test_move_up` | ArrowUp → player.y 減少 |
| `test_move_down` | ArrowDown → player.y 增加 |

#### 碰撞（4 項）
| 測試名稱 | 驗證點 |
|----------|--------|
| `test_collision_decreases_lives` | 隕石在玩家位置 → lives=2 |
| `test_collision_sets_invincible` | 碰撞後 → invincible=120 |
| `test_lives_zero_triggers_dead_state` | lives=1 碰撞 → state='dead' |
| `test_large_asteroid_requires_two_hits` | hp=2 → 一發 hp=1，兩發消失 +30分 |

---

## Integration Test 規範

### 定義

> 多個子系統協同運作：需等待真實 game loop 執行，驗收系統整合結果。

### 原則

- 需先有對應的 Functional Test 才能寫 Integration Test
- 等待時間依場景決定（生成需 3s，碰撞需 < 1s）
- 命名規則：`test_<系統A>_<系統B>_<結果>()`

### 測試項目清單

#### 隕石自然生成（2 項）
| 測試名稱 | 情境 | 驗證點 |
|----------|------|--------|
| `test_spawn_asteroid_increases_count` | 等 3 秒 | asteroids.length > 0 |
| `test_spawn_asteroid_properties` | 等 3 秒 | r>=18, vy>0, hp>=1 |

#### 邊界 clamp（4 項）
| 測試名稱 | 情境 | 驗證點 |
|----------|------|--------|
| `test_boundary_left` | 持續按左 3s | x >= 18 |
| `test_boundary_right` | 持續按右 3s | x <= 462 |
| `test_boundary_top` | 持續按上 3s | y >= 28 |
| `test_boundary_bottom` | 持續按下 3s | y <= 612 |

#### 分數與射擊（2 項）
| 測試名稱 | 情境 | 驗證點 |
|----------|------|--------|
| `test_score_dom_syncs_with_js` | set score=999，等 200ms | DOM 分數 == JS score |
| `test_laser_destroys_asteroid_and_scores` | 射擊標記隕石，等 800ms | 隕石消失，score +15 |

---

## Regression Test 規範

### 定義

> 邊界情境與易錯行為的守衛測試，確保特定行為在未來開發中不會悄悄退化。

### 原則

- 每條測試對應一個具體的「容易被改壞的行為」
- 測試內容應有明確的防守說明（docstring 標注）
- 命名規則：`test_<被防守的行為>()`

### 測試項目清單

| 測試名稱 | 防守的行為 |
|----------|----------|
| `test_invincible_prevents_double_damage` | 同幀兩顆隕石只扣一次血 |
| `test_dead_state_blocks_laser` | dead 狀態按 Space 不發射雷射 |
| `test_score_stops_when_not_playing` | gameover 狀態分數不自動增加 |
| `test_dead_transitions_to_gameover` | dead → 1200ms → gameover 狀態轉換 |
| `test_restart_from_gameover` | gameover 按 Space 完整重置遊戲 |
| `test_invincible_decrements_each_frame` | invincible 每幀遞減 1 |

---

## 新增測試檢查清單

每次新增功能或修改遊戲邏輯時，依序確認：

- [ ] 選對 fixture：白箱測試用 `playing_page`，黑箱測試用 `game_page`
- [ ] 若修改了任何公式（碰撞、分數、等級、生成頻率）→ 補充或更新 **Unit Test**
- [ ] 為新 game function 補充 **Functional Test**（單一行為驗證）
- [ ] 為新功能與現有系統的互動補充 **Integration Test**
- [ ] 若發現新的邊界行為 → 補充 **Regression Test** 防止復發
- [ ] 本機執行 `pytest tests/ -v` 全部通過（可看到瀏覽器畫面）
- [ ] 執行快速版確認無誤：`pytest -m "unit or smoke"`

---

## 測試分類判斷原則

| 問題 | 答案 → 分類 | Fixture |
|------|------------|---------|
| 只是驗算一條數學公式嗎？ | 是 → Unit Test | `playing_page` |
| 測試一個 game function 的完整行為嗎？ | 是 → Functional Test | `playing_page` |
| 需要等待 game loop 跑一段時間嗎？ | 是 → Integration Test | `game_page` |
| 在防止一個已知邊界行為退化嗎？ | 是 → Regression Test | `game_page` |
| 只觀察 DOM，不碰 JS 內部嗎？ | 是 → Smoke 或 Regression Test | `game_page` |
