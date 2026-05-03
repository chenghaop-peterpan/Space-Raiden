為了解決 GC 效能瓶頸與雙重 Action Space 問題，底層 TypeScript (或 JSDoc) 介面設計如下：

// 1. Adapter 介面
interface IAdapter {
    // GC 優化：就地轉換 State 到預先分配的陣列
    transformInPlace(engineState: EngineState, outBuffer: Float32Array): void;
    
    // 空間轉換：Model Action -> Engine Action
    actionToEngine(modelAction: ModelAction): EngineAction;
    
    // 分數塑形
    shapeReward(rawReward: number, engineState: EngineState): number;
    
    // 針對 MCTS 或 Stateful Adapter 必須實作
    clone(): IAdapter; 
}

// 2. Engine 介面
interface IGameEngine {
    reset(config: EnvConfig): EngineState;
    // 支援多 Agent 的 Map 輸入
    step(actions: Map<string, EngineAction>): StepResult; 
}

// 3. 回傳結構
interface StepResult {
    states: Map<string, EngineState>;
    rewards: Map<string, number>;
    dones: Map<string, boolean>;
    info: Record<string, any>;
}

***

### 3. 開發計畫：`planning.md`

```markdown
# Execution Plan: Space-Raiden Refactoring

本計畫旨在確保從單一腳本到四層架構的過渡期間，系統始終處於可測試、可運行的狀態。

## Phase 1: 核心解耦與 Adapter 引入 (針對 Space-Raiden)
**目標**：將現有的 `space_dodge.html` 拆分為無頭引擎，並成功運行舊有的規則型 AI。

* [ ] **Step 1.1: 抽離 Game Engine**
  * 建立 `engine.js`，將所有物理運算、碰撞偵測、狀態更新移入。
  * 移除所有對 `window`, `document`, `canvas` 的直接依賴。
  * 實作 `reset()` 與 `step()` 介面。
* [ ] **Step 1.2: 抽離 Renderer**
  * 建立 `renderer.js`，實作繪製邏輯。
  * 透過 Event Listener 或直接呼叫，監聽 Engine 的狀態變化並渲染。
* [ ] **Step 1.3: 實作 Adapter 基礎類別**
  * 定義 `StatelessAdapter` 介面。
  * 實作 `SpaceRaidenBaseAdapter`，將 Engine 的物件陣列轉換為扁平化的數值陣列 (預備給 AI 使用)。
* [ ] **Step 1.4: 遷移現有 AI 策略**
  * 將現有的「威脅迴避」、「強攻型」包裝為實作了 `Agent` 介面的類別。
  * 確保透過 Engine -> Adapter -> Agent 的資料流能正常驅動遊戲。
* [ ] **Step 1.5: 測試覆蓋**
  * 執行 Playwright Integration Test，驗證人類鍵盤輸入與重構後的 Engine 互動正常。
  * 執行 Headless Epoch 測試，確保重構沒有帶來嚴重的效能回退。

## Phase 2: Python Gym 橋接與 RL 訓練
**目標**：打通 JavaScript 引擎與 Python 強化學習生態系的橋樑。

* [ ] **Step 2.1: 實作 Gym Wrapper (Python)**
  * 在 Python 端實作 `gym.Env` 類別 (`SpaceRaidenEnv`)。
* [ ] **Step 2.2: IPC 通訊實作**
  * 透過 WebSocket 或 Playwright 的 CDP 協議，讓 Python 的 `step()` 能呼叫 JS 端的 Engine 迴圈。
* [ ] **Step 2.3: 引入 DQN 訓練**
  * 使用 Stable-Baselines3 套件，接上 `SpaceRaidenEnv` 進行初步訓練。
  * 實作 `StatefulAdapter` 處理 Frame Stacking。
* [ ] **Step 2.4: 效能調校**
  * 實作 `transformInPlace` 與 `Float32Array`，將 Headless 訓練的 FPS 推升至極限，解決 GC 延遲。

## Phase 3: 橫向遊戲擴充 (Proof of Concept)
**目標**：驗證 Factory Pattern 與架構的泛用性。

* [ ] **Step 3.1: 實作 Tetris Engine**
  * 開發一個純邏輯的俄羅斯方塊引擎，實作與 Space-Raiden 完全相同的 `IGameEngine` 介面。
* [ ] **Step 3.2: 實作 MCTS Agent 與對應 Adapter**
  * 開發 MCTS 演算法。
  * 實作將 Tetris 網格狀態轉換為 MCTS 節點的 Adapter。
* [ ] **Step 3.3: Factory 組裝測試**
  * 透過更改 `run_config.json`，系統能無縫啟動 Tetris + MCTS 組合，證明架構解耦成功。