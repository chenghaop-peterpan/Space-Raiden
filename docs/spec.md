# 技術規格文件 — 太空梭躲避隕石

## 專案概覽

| 項目 | 說明 |
|------|------|
| 檔案 | `space_dodge.html` |
| 技術 | 原生 HTML5 / CSS3 / JavaScript（無外部依賴） |
| 畫布尺寸 | 480 × 640 px |
| 語言 | 繁體中文介面 |

---

## 遊戲狀態機

```
start ──[Space/Enter]──► menu ──[Player]──────────────────────► playing ──[lives=0]──► dead ──[1.2s]──► gameover
                          │                  ▲                      │                                        │
                          ├──[AI]──► ai_params ──[Start AI]──►      │                                        │
                          └──[Game Settings]──► game_settings        │                                        │
                               [Esc/Back]──► menu ◄──[Space/Enter]───┘                                        │
                                                                                                               │
                          playing ──[Esc]──► paused ──[Esc / 繼續遊戲]──► playing                             │
                                               └──[返回選單]──► menu ◄───────────────────────────────────────┘
```

| 狀態 | 說明 |
|------|------|
| `start` | 開始畫面，顯示操作說明 |
| `menu` | 模式選單：玩家模式 / AI 模式 / ⚙ 遊戲設定（↑↓ 切換，Space/Enter 確認） |
| `ai_params` | AI 參數面板（HTML overlay，滑桿調整 5 項參數 + Epoch 選擇） |
| `game_settings` | 遊戲設定面板（HTML overlay，Dash 相關 toggle 與 slider） |
| `paused` | 遊戲暫停中；畫面凍結，疊加暫停選單（繼續遊戲 / 返回選單） |
| `playing` | 遊戲進行中，執行完整 update/draw 迴圈 |
| `dead` | 玩家死亡動畫播放中（1.2 秒） |
| `gameover` | 顯示最終分數與等級，Space/Enter 返回選單 |

---

## 玩家（Player）

| 屬性 | 值 |
|------|-----|
| 碰撞寬高 | 36 × 56 px |
| 最大速度 | 5 px/frame |
| 加速度 | 0.8 px/frame² |
| 摩擦係數 | 0.82（每幀速度乘以此值） |
| 無敵時間 | 被擊中後 120 幀（約 2 秒） |

### 移動物理

每幀依按鍵狀態累加速度，乘以摩擦係數後限制在最大速度內，再加到位置上。邊界夾緊至畫布範圍。

---

## Dash 機制

### 設定結構（`dashConfig`）

```javascript
let dashConfig = {
  enabled:       true,   // Dash 功能總開關
  upOnly:        true,   // true=只往上 / false=依當前移動方向
  invincible:    true,   // dash 期間是否無敵
  invincibleSec: 1.0,    // 無敵秒數（預設 1.0s = 60 幀）
  cooldownSec:   2.0,    // 冷卻秒數（預設 2.0s = 120 幀）
};
let dashCooldown = 0;    // 剩餘冷卻幀數
let dashGhosts   = [];   // 殘影列表 [{x, y, life}]
```

### `fireDash()`

- 若 `!dashConfig.enabled || dashCooldown > 0`：直接返回
- `upOnly=true`：`player.y -= player.h`（56px），不低於上邊界
- `upOnly=false`：依當前速度方向，位移一個 player.h 距離
- 設定 `dashCooldown = round(cooldownSec × 60)`
- 若 `invincible=true`：延長 invincible 幀數（取較大值）
- 在舊位置推入殘影 `{ x: oldX, y: oldY, life: 1 }`

### 殘影（`dashGhosts`）

每幀 `life -= 0.12`，降到 0 時移除。繪製時 `globalAlpha = life × 0.5`，青色（`#0ff`）shadowBlur。

---

## 隕石（Asteroid）

| 屬性 | 說明 |
|------|------|
| 半徑 | 18–42 px（基礎），等級越高上限略增 |
| 縱向速度 | `1.5 + random(0~1.5) + level × 0.25` px/frame |
| 橫向速度 | `±(1.5 + level × 0.3)` px/frame |
| 血量 (hp) | 半徑 > 32 px 為 2，其餘為 1 |
| 生成頻率 | 每 `max(28 - level×3, 10)` 幀生成一顆 |
| 形狀 | 9 頂點不規則多邊形，帶旋轉動畫 |

---

## 雷射（Laser）

| 屬性 | 值 |
|------|-----|
| 尺寸 | 3 × 18 px |
| 速度 | -14 px/frame（向上） |
| 冷卻時間 | 12 幀 |
| 碰撞判定 | 雷射中心與隕石圓心距離 < 隕石半徑 + 4 |

---

## 爆炸與粒子系統

### 爆炸光圈（Explosion）
- 生成一個以 `life` 值控制透明度的放射漸層圓
- 小爆炸半徑 22 px，大爆炸半徑 40 px
- 每幀 `life -= 0.06`，life ≤ 0 移除

### 粒子（Particle）
- 小爆炸生成 14 顆，大爆炸生成 28 顆
- 具有初速、重力（`vy += 0.1`）、生命衰減
- 顏色為暖色系 HSL（hue 20–60）

### 畫面震動（Screen Shake）
- 被隕石擊中：震動 20 幀
- 大型隕石爆炸：震動 14 幀
- 每幀隨機偏移畫布 ±4 px

---

## 背景星空

- 120 顆星，位置與速度隨機初始化
- 速度範圍 0.2–0.8 px/frame（視差滾動效果）
- 亮度以 sin 函數週期閃爍

---

## 分數與等級

| 事件 | 分數 |
|------|------|
| 存活時間 | +1 分 / 6 幀 |
| 擊毀小隕石（r ≤ 28） | +15 分 |
| 擊毀大隕石（r > 28） | +30 分 |

```
level = 1 + floor(score / 300)
```

---

## 渲染管線（每幀 draw 順序）

1. 背景填色
2. 星空
3. 玩家尾焰粒子
4. 爆炸光圈
5. 爆炸粒子
6. 隕石
7. 雷射
8. 玩家太空梭（無敵時閃爍）
9. Dash 殘影（`dashGhosts`，青色半透明，`globalAlpha = life × 0.5`）
10. 疊加 UI 畫面（開始 / 遊戲結束）

---

## AI 開發模式（Auto-Pilot Mode）

### 遊戲模式

| `gameMode` | 說明 |
|------------|------|
| `'player'` | 玩家以鍵盤控制 |
| `'ai'` | 規則式 AI 自動操控，每幀呼叫 `aiUpdate()` |

### 可插拔策略架構（`AI_STRATEGIES`）

```javascript
const AI_STRATEGIES = {
  threat:     { name: '威脅迴避', decide(gs, p), getDecisionState(gs, p) },
  aggressive: { name: '強攻型',   decide(gs, p), getDecisionState(gs, p) },
  defensive:  { name: '防守型',   decide(gs, p), getDecisionState(gs, p) },
};
```

- `decide(gs, p)` → `{ left, right, up, down, shoot, dash }` 指令物件
- `getDecisionState(gs, p)` → `string`（用於 HUD 顯示）
- `currentStrategy`：目前選用的策略鍵（`'threat'` / `'aggressive'` / `'defensive'`）

#### 各策略 Dash 門檻

| 策略 | Dash 觸發條件（距離 < safetyRadius × N） |
|------|----------------------------------------|
| 威脅迴避 | × 0.35（中等積極） |
| 強攻型 | × 0.25（保守，偏好戰鬥） |
| 防守型 | × 0.50（積極，優先逃生） |

### API

#### `getGameState() → Object`

回傳當前遊戲快照，供 AI 或外部程式讀取：

```javascript
{
  player: { x, y, vx, vy, invincible: bool, invincibleFrames: number },
  laserCooldown:  number,
  dashCooldown:   number,   // Dash 剩餘冷卻幀數（0 = 可用）
  asteroids: [{ x, y, r, vx, vy, hp }],
  lasers:    [{ x, y, vy }],
  score, lives, level, frameCount, state, gameMode
}
```

#### `executeCommand(cmd) → void`

統一的飛船控制介面，鍵盤輸入與 AI 決策皆透過此函數驅動：

```javascript
executeCommand({ left, right, up, down, shoot, dash })
// 範例：向左移動同時發射
executeCommand({ left: true, shoot: true })
// 範例：觸發 Dash
executeCommand({ dash: true })
```

### AI 決策狀態

各策略透過 `getDecisionState()` 回傳當前狀態字串，顯示於 HUD：

| 狀態 | 意義 | HUD 顏色 |
|------|------|----------|
| `'Idle'` | 無威脅，無目標 | 藍 `#88f` |
| `'Tracking'` | 有隕石在上方，等待對準 | 黃 `#ff8` |
| `'Firing'` | 隕石在瞄準容差內，正在射擊 | 綠 `#0f8` |
| `'Evading'` | 威脅在安全距離內，側向閃躲 | 橘 `#f80` |
| `'Dodging'` | 威脅極近，緊急規避 | 紅 `#f44` |

### Debug HUD

Canvas 疊加儀表板（透過設定面板 → 視覺化 tab 開關），顯示：
- 遊戲模式、狀態、幀數
- 雷射命中率（hits / fired）
- AI 決策狀態燈號（僅 AI 模式）
- 目前 AI 參數數值
- `safetyViz: ON/OFF`（安全距離視覺化狀態）
- `dash CD  : Nfr / READY`（Dash 冷卻狀態）

### 安全距離視覺化

透過設定面板 → 視覺化 tab 開關，顯示/隱藏紅色虛線圓圈：
- **淡紅色外圈**：`aiParams.safetyRadius`（基礎安全距離）
- **亮紅色內圈**：當前策略有效半徑（aggressive × 0.6，defensive × 1.5）

### AI 參數（`aiParams`）

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `reactionDelay` | 250 ms | 反應延遲（預留） |
| `safetyRadius` | 80 px | 觸發閃躲的距離閾值 |
| `aimTolerance` | 40 px | 瞄準容許誤差 |
| `aggressionLevel` | 7 | 攻擊積極度（1–10） |
| `lookaheadFrames` | 20 fr | 預測隕石未來位置的幀數 |

---

## Epoch 批次執行系統

### 設定結構（`epochConfig`）

```javascript
let epochConfig = {
  target:  0,   // 目標局數（0=關閉，可選 10/20/30）
  current: 0,   // 已完成局數
};
```

### 執行流程

1. 用戶在 AI 參數面板選擇 Epoch 數 → `epochConfig.target = N`
2. 每局結束呼叫 `recordRun()`，若 epoch 進行中則呼叫 `advanceEpoch()`
3. `advanceEpoch()`：`current++`，若 `current < target`，則 `setTimeout(400ms) → startGame('ai')`
4. 達標後顯示統計（平均分、最高分、標準差）於 gameover 畫面

---

## Benchmark 系統

### 資料結構

#### `runHistory[]`

每局結束後呼叫 `recordRun()` 自動寫入：

```javascript
{
  run:      number,       // 累計場次編號
  score:    number,
  level:    number,
  accuracy: number,       // 命中率 0–100（%）
  frames:   number,       // 存活幀數
  mode:     'player'|'ai',
  strategy: string,       // AI 策略名稱（AI 模式）
  states: { Idle, Tracking, Firing, Evading, Dodging } // AI 幀數分布
}
```

#### `stateFrameCounts`

每幀於 `aiUpdate()` 末尾自動累加，隨 `startGame()` 重置。

---

### 三大功能

| 功能 | 觸發 | 說明 |
|------|------|------|
| **Canvas 趨勢圖** | 自動（gameover 畫面） | 最近 10 場分數長條圖，當場用青色高亮 |
| **HTML 歷史表格** | 設定面板 → Log tab | 浮層面板，顯示全部場次詳細數據 |
| **CSV 匯出** | 設定面板 → Log tab 按鈕 | 下載 `benchmark.csv` |

### HTML 面板（`#benchmark-panel`）

- 摘要列：場次數、平均分數、最高分數
- 表格欄位：`#`、分數、等級、命中率、時長、策略、Idle/Track/Fire/Evade/Dodge（%）
- 最新一場以黃色 `#ff8` 標示
- 「✕ 關閉」按鈕可關閉

### CSV 格式

```
Run,Score,Level,Accuracy(%),Duration(s),Strategy,Idle(%),Tracking(%),Firing(%),Evading(%),Dodging(%)
1,342,2,65,15.2,威脅迴避,20,35,18,22,5
...
```

---

## 統一設定面板（`#ctrl-panel`）

### 開關方式

| 操作 | 效果 |
|------|------|
| `H` 鍵（遊戲中） | 開啟面板，自動暫停遊戲（`state = 'paused'`，`_ctrlPanelPaused = true`） |
| `H` 鍵再按 / `ESC` / ✕ 按鈕 | 關閉面板，恢復遊戲（`state = 'playing'`，`_ctrlPanelPaused = false`） |

### 三個 Tab

#### AI 參數 tab
即時調整 `aiParams` 所有欄位（安全距離、瞄準容差、攻擊性、預測幀數、反應延遲），滑桿變更立即生效，並同步原有 `#ai-panel` 顯示值。支援策略切換（威脅迴避 / 強攻型 / 防守型）。

#### 視覺化 tab
- **Debug HUD**：開啟/關閉 Canvas 疊加儀表板（`hudVisible`）
- **安全距離圓**：開啟/關閉紅色虛線圓圈（`safetyRadiusVisible`）
- **AI Terminal**：開啟/關閉右側 AI 決策捲動終端（`aiTermVisible`）

#### Log tab
- **Input Log**：開啟/關閉逐幀按鍵記錄面板（`inputLogVisible`）
- **Benchmark**：開啟/關閉 Benchmark 歷史表格面板（`benchmarkVisible`）
- 匯出 Benchmark CSV / 匯出 Input Log CSV 按鈕

### 相關變數

| 變數 | 型別 | 說明 |
|------|------|------|
| `ctrlPanelVisible` | boolean | 面板是否可見 |
| `ctrlPanelTab` | `'ai'｜'visual'｜'log'` | 目前選中的 tab |
| `_ctrlPanelPaused` | boolean | 是否由開面板觸發的暫停（關閉時自動恢復） |

---

## Input Log

### 資料結構

每幀於 `update()` 末尾自動 append 至 `inputLog[]`：

```javascript
{
  frame:  number,    // 幀號
  keys:   string,    // 按鍵字串（↑↓←→ 組合，無按鍵為 '-'）
  x:      number,    // 玩家 X（整數）
  y:      number,    // 玩家 Y（整數）
  dx:     number,    // 本幀 X 位移（1 位小數）
  dy:     number,    // 本幀 Y 位移（1 位小數）
  dist:   number,    // 本幀位移距離（1 位小數）
  event:  string,    // 'DASH' | 'LASER' | 'HIT' | ''
}
```

- 上限 7200 筆（超過則移除最舊一筆，約 2 分鐘 @ 60fps）
- `startGame()` 時重置為空陣列

### 事件標記來源

| 事件 | 觸發位置 |
|------|---------|
| `'DASH'` | `fireDash()` 末尾 |
| `'LASER'` | `fireLaser()` 末尾（若同幀已有 DASH 則不覆蓋） |
| `'HIT'` | 碰撞 `lives--` 後 |

### HTML 面板（`#input-log-panel`）

顯示最近 200 筆，欄位：幀 / 按鍵 / X / Y / dX / dY / 距離 / 事件。事件非空時以黃色 `#ff8` 標示。摘要列顯示總幀數、DASH/LASER/HIT 次數。

### CSV 匯出（`exportInputLogCSV()`）

下載 `input_log.csv`，包含完整 `inputLog[]` 所有欄位。

---

## AI Terminal（`#ai-terminal`）

### 佈局

與 canvas 並排於 `#canvas-row` flex 容器中（canvas 左、terminal 右，`display:none` 預設隱藏）。尺寸 220 × 640px。

### 格式

每幀由 `aiUpdate()` 末尾 append 一行（最多保留 300 筆，DOM 最多渲染 80 行）：

```
FRAME  DECISION  CMD  d:DIST
 1234  Evading   ←↑💥  d:95
```

- `FRAME`：5 位幀號
- `DECISION`：決策狀態（8 字元 padEnd）
- `CMD`：按鍵圖示（←→↑↓ + 💥射擊 + ⚡Dash）
- `d:DIST`：到最近隕石的距離（整數 px）

### 顏色編碼

| 狀態 | 顏色 |
|------|------|
| Idle | 藍 `#44f` |
| Tracking | 黃 `#ff8` |
| Firing | 綠 `#0f8` |
| Evading | 橘 `#f80` |
| Dodging | 紅 `#f44` |

---

## 本地儲存（localStorage）

### Keys

| Key | 內容 | 更新時機 |
|-----|------|---------|
| `sr_runs` | `JSON(runHistory[])` | `recordRun()` 後 |
| `sr_epochs` | `JSON(epochHistory[])` | `finalizeEpoch()` 後 |
| `sr_inputlog` | `JSON(inputLog[])` 最後一局快照 | `recordRun()` 後 |

### 容量估算

| 資料 | 估算 | 說明 |
|------|------|------|
| `sr_runs` | ~200 bytes/場 | 1000 場 ≈ 200KB |
| `sr_epochs` | 極小 | 忽略不計 |
| `sr_inputlog` | ~80 bytes/幀 | 7200 幀 ≈ 576KB |
| 合計 | < 1.5MB | 遠低於 5MB 上限 |

### API

| 函數 | 說明 |
|------|------|
| `loadStorage()` | 頁面啟動時還原三組資料（try/catch 防止損壞資料） |
| `_saveRuns()` | 儲存 runHistory |
| `_saveEpochs()` | 儲存 epochHistory |
| `_saveInputLog()` | 儲存 inputLog 快照 |
| `updateStorageInfo()` | 更新設定面板「N 場 / X KB」顯示 |
| `clearStorage()` | 移除三個 key，重置對應變數，重繪面板 |

---

## 效能考量

- 所有物件以陣列管理，每幀用 `filter` 移除過期物件
- 使用 `requestAnimationFrame` 驅動主迴圈，目標 60 fps
- 無外部資源載入，首幀即可渲染

---

## 版本管理規範

每次發版或功能迭代時，依序執行：

1. 在 `changelog/` 新增 `vX.Y.Z.md`，記錄以下內容：
   - **主題**：一句話說明本次迭代核心目標
   - **新增**：新功能、新檔案
   - **修改**：既有功能調整
   - **修復**：Bug 修復
   - **測試**：新增的 Unit / Functional / Integration / Smoke / Regression Test

2. 更新 `changelog/SUMMARY.md`，在表格**最上方**插入新版本一行

3. 若新增/修改了使用者可見功能，更新 `README.md`；若新增/修改了 API、資料結構或狀態機，更新 `docs/spec.md`

4. 建立 git tag 並推上遠端：
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

### 版本號規則（Semantic Versioning）

| 類型 | 版號變化 | 範例 |
|------|----------|------|
| 破壞性變更 / 重大新功能 | Major +1 | v1.0.0 → v2.0.0 |
| 新功能（向下相容） | Minor +1 | v1.0.0 → v1.1.0 |
| Bug 修復 / 小調整 | Patch +1 | v1.0.0 → v1.0.1 |
