# Space-Raiden: AI Algorithm Sandbox (Master Specification)

## 1. 專案願景 (Project Vision)
本專案旨在將原有的單一 HTML5 Canvas 太空射擊遊戲 (`space_dodge.html`)，重構並轉型為**「泛用型 AI 演算法測試沙盒」**。系統將透過嚴格的介面解耦，支援從傳統規則驅動到深度強化學習 (DRL)、神經演化 (NEAT) 甚至多模態大模型 (VLM) 的快速插拔，並具備橫向擴充多種遊戲環境的能力。

---

## 2. 開源生態借鑒與核心架構 (Architecture & Inspirations)

為解決遊戲與 AI 演算法之間的「N × M 維度爆炸」與「空間不匹配」問題，本系統的底層設計深度參考了業界兩大標竿專案：

*   **[Farama/Gymnasium]](https://github.com/Farama-Foundation/Gymnasium)**：借鑒其 `Env` 介面與 `Wrapper` 設計模式。我們將引入 **Adapter (轉接器)** 層，將遊戲的物理狀態標準化為 Agent 可讀的張量，並負責 Reward Shaping，實現遊戲邏輯與 AI 訓練的徹底解耦。
*   **[wagenaartje/neataptic](https://github.com/wagenaartje/neataptic)**：借鑒其純 JS 神經網路黑箱化與演化邏輯。這確保了我們的 AI Agent 模組可以完全獨立於 Node.js 或瀏覽器前端運行，實現無縫的 Epoch 批次訓練。

### 2.1 四層解耦模組 (4-Module Architecture)
基於上述理念，系統採用四層獨立架構，並透過 Factory Pattern 進行動態組裝：

1. **Game Engine (遊戲引擎)**：處理純物理運算、碰撞偵測與狀態結算。必須支援 Headless (無頭) 極速執行，完全不依賴 DOM/Canvas。
2. **Adapter (轉接器/橋樑)**：負責空間轉換、特徵工程 (Feature Engineering) 與分數塑形。分立 `Stateless` 與 `Stateful` (支援 Frame Stacking 且需實作 clone)；處理高頻數據轉換。
3. **AI Agent (代理大腦)**：接收標準化 Observation，輸出數學/邏輯決策 (Action)。對遊戲環境完全無知 (Agnostic)。
4. **Renderer (渲染器)**：純視覺展示層。掛載於 Engine 的事件流上，Headless 訓練時可完全卸載以節省運算資源。

---

## 3. 泛用性支援矩陣 (Support Matrix)

系統架構設計必須能包容以下 5 種遊戲環境與 AI 模型的任意組合：

| 遊戲載體 (Env) | 狀態與動作空間 | 推薦適配之 AI 策略 (Agent) |
| :--- | :--- | :--- |
| **Space-Raiden** | 連續狀態 / 離散動作 | DRL (DQN/PPO), Scripted |
| **Tetris** | 離散網格 / 離散巨集 | MCTS (蒙地卡羅樹搜尋) |
| **Pac-Man** | 迷宮圖論 / 離散動作 | FSM, Behavior Tree (行為樹) |
| **2D Racing** | 連續物理 / 連續動作 | NEAT (純前端神經演化) |
| **Platformer** | 混合空間 / 延遲獎勵 | VLM/LLM (多模態視覺決策) |

---

## 4. 標準化介面合約 (Standardized Interfaces)

定義核心資料流與 TypeScript 介面。

### 4.1 通訊資料結構 (Data Structures)
* **Engine State**: 遊戲客觀物理狀態 (例如：物件座標、大小)。
* **Observation**: Adapter 轉換後供 AI 讀取的數據 (例如：正規化後的 Float32Array)。
* **Engine Action**: 遊戲接收的具體指令 (例如：`{ up: true, shoot: false }`)。
* **Model Action**: AI 輸出的數學結果 (例如：機率分佈 Logits)。

### 4.2 核心 API 定義 (Core API)
```typescript
interface IGameEngine {
    // 依據配置重置遊戲，回傳初始狀態
    reset(config: EnvConfig): EngineState;
    // 推進一幀，回傳 Tuple (NextState, Reward, Done, Info)
    step(actions: Map<string, EngineAction>): StepResult;
}

interface IAdapter {
    // 【效能熱點】就地轉換 State 到預先分配的 Float32Array，避免 GC
    transformInPlace(engineState: EngineState, outBuffer: Float32Array): void;
    
    // Model 決策轉回 Engine 指令
    actionToEngine(modelAction: ModelAction): EngineAction;
    
    // 將原始遊戲分數轉化為訓練用 Reward
    shapeReward(rawReward: number, engineState: EngineState): number;
}

5. 參數配置驅動設計 (Config-Driven Pattern)
系統啟動時，只依賴一份統一的 JSON 設定檔進行依賴注入 (DI) 與工廠裝配，實現演算法互換而「不改一行程式碼」。

JSON
{
  "experiment_id": "exp_001_raiden_dqn",
  "environment": {
    "game": "space-raiden",
    "params": { "difficulty": "hard", "meteor_spawn_rate": 1.5 }
  },
  "agent": {
    "model": "dqn",
    "params": { "learning_rate": 0.001, "gamma": 0.99 }
  },
  "adapter": {
    "state_representation": "flattened_array_normalized",
    "reward_shaping": { "survival_weight": 0.1, "kill_weight": 5.0 }
  }
}
6. 效能與測試規範 (Performance & Testing)
本專案將嚴格執行高效能標準，並維持現有基於 Playwright + pytest 的自動化測試網：

6.1 Zero-Allocation 效能規範
在 Headless 訓練的熱點迴圈 (Hot Loop) 中，禁止使用 new Object(), Array.map 等會觸發垃圾回收 (GC) 的操作。所有狀態轉換一律使用 TypedArray (Float32Array) 與 transformInPlace 進行記憶體直接覆寫。

6.2 五層自動化測試架構
Smoke Test: 驗證 Run Config JSON 讀取與 Factory 裝配是否能成功實例化四層模組。

Unit Test: 針對 Adapter 的 State Mapping 與 Reward Shaping 邏輯進行隔離測試。

Functional Test: 驗證各個獨立的 AI Agent 是否能輸出合法定義的 Model Action。

Integration Test: 驗證 Headless Engine 結合 Adapter 能以高頻率連跑 1000 幀不崩潰、無記憶體洩漏。

Regression Test: 確保重構後，Renderer UI 掛載正常，且人類玩家透過鍵盤操作的物理手感與舊版完全一致。