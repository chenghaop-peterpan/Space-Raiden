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
start ──[Space/Enter]──► menu ──[Player]──────────────────► playing ──[lives=0]──► dead ──[1.2s]──► gameover
                          │                                                                               │
                          └──[AI]──► ai_params ──[Start AI]──► playing(AI)                               │
                                         └──[Esc]──► menu ◄────────────────────[Space/Enter]─────────────┘
```

| 狀態 | 說明 |
|------|------|
| `start` | 開始畫面，顯示操作說明 |
| `menu` | 模式選單：玩家模式 / AI 模式（↑↓ 切換，Space/Enter 確認） |
| `ai_params` | AI 參數面板（HTML overlay，滑桿調整 5 項參數） |
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
9. 疊加 UI 畫面（開始 / 遊戲結束）

---

## AI 開發模式（Auto-Pilot Mode）

### 遊戲模式

| `gameMode` | 說明 |
|------------|------|
| `'player'` | 玩家以鍵盤控制 |
| `'ai'` | 規則式 AI 自動操控，每幀呼叫 `aiUpdate()` |

### API

#### `getGameState() → Object`

回傳當前遊戲快照，供 AI 或外部程式讀取：

```javascript
{
  player: { x, y, vx, vy, invincible: bool, invincibleFrames: number },
  laserCooldown: number,
  asteroids: [{ x, y, r, vx, vy, hp }],
  lasers:    [{ x, y, vy }],
  score, lives, level, frameCount, state, gameMode
}
```

#### `executeCommand(cmd) → void`

統一的飛船控制介面，鍵盤輸入與 AI 決策皆透過此函數驅動：

```javascript
executeCommand({ left, right, up, down, shoot })
// 範例：向左移動同時發射
executeCommand({ left: true, shoot: true })
```

### AI 決策狀態（`aiDecisionState`）

| 狀態 | 意義 | HUD 顏色 |
|------|------|----------|
| `'Idle'` | 無威脅，無目標 | 藍 `#88f` |
| `'Tracking'` | 有隕石在上方，等待對準 | 黃 `#ff8` |
| `'Firing'` | 隕石在瞄準容差內，正在射擊 | 綠 `#0f8` |
| `'Evading'` | 威脅在安全距離內，側向閃躲 | 橘 `#f80` |
| `'Dodging'` | 威脅極近（< safetyRadius × 0.5），緊急規避 | 紅 `#f44` |

### Debug HUD

按 `H` 鍵開關 Canvas 疊加儀表板，顯示：
- 遊戲模式、狀態、幀數
- 雷射命中率（hits / fired）
- AI 決策狀態燈號（僅 AI 模式）
- 目前 AI 參數數值

### AI 參數（`aiParams`）

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `reactionDelay` | 250 ms | 反應延遲（目前預留，尚未接入） |
| `safetyRadius` | 80 px | 觸發閃躲的距離閾值 |
| `aimTolerance` | 40 px | 瞄準容許誤差 |
| `aggressionLevel` | 7 | 攻擊積極度（1–10，每幀射擊機率） |
| `lookaheadFrames` | 20 fr | 預測隕石未來位置的幀數 |

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

3. 建立 git tag 並推上遠端：
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
