# Space-Raiden: AI Algorithm Sandbox Specification

## 1. 專案願景
將原有的單一 HTML5 Canvas 太空射擊遊戲，重構並轉型為「泛用型 AI 演算法測試沙盒」。系統需支援從傳統規則驅動 (Rule-based) 到深度強化學習 (DRL) 等多種 AI 模型的快速插拔，並具備橫向擴充多種遊戲環境的能力。

## 2. 系統需求與核心特性
* **四層高度解耦**：嚴格拆分 Game Engine、Adapter、AI Agent 與 Renderer。
* **空間多型橋接 (Space Bridging)**：支援連續/離散狀態空間與動作空間的無縫轉換。
* **高頻率無頭訓練 (Headless Training)**：支援無 UI 渲染的極速執行模式。
* **零分配優化 (Zero-Allocation)**：在訓練的熱點路徑 (Hot Path) 上，必須支援 TypedArray (如 `Float32Array`) 與 `transformInPlace` 記憶體覆寫，避免 GC (Garbage Collection) 造成的效能抖動。
* **配置即原件 (Config-Driven)**：透過統一的 JSON/YAML 參數檔，動態實例化遊戲與 AI 組合。

## 3. 支援矩陣目標

### 3.1 遊戲環境 (Environments)
1. Space-Raiden (太空躲避) - 連續空間，即時反應。
2. Tetris (俄羅斯方塊) - 離散空間，長期規劃。
3. Pac-Man (吃豆人) - 迷宮圖論，多 Agent 協同。
4. Racing (2D賽車) - 連續物理空間，極限控制。
5. Platformer (馬力歐) - 混合空間，延遲獎勵。

### 3.2 支援 AI 演算法 (Agents)
1. Scripted (硬編碼腳本)
2. FSM (有限狀態機)
3. Behavior Tree (行為樹)
4. MCTS (蒙地卡羅樹搜尋)
5. NEAT (神經演化 - 前端原生)
6. DQN / PPO (深度強化學習 - 透過 Gym 橋接 Python)
7. VLM / LLM (多模態大模型視覺決策)

## 4. 測試標準與 CI/CD 規範
必須維持並擴展現有的五層測試架構 (Playwright + pytest)：
* **Smoke Test**: 驗證核心設定檔讀取與 Factory 裝配是否正常。
* **Unit Test**: 針對 Adapter 的 State Mapping 與 Reward Shaping 邏輯進行隔離測試。
* **Functional Test**: 驗證各個獨立的 AI Agent 是否能輸出合法的 Action Space。
* **Integration Test**: Headless Engine 結合 Adapter 跑滿 1000 幀不崩潰。
* **Regression Test**: 確保重構後，人類玩家透過鍵盤操作的手感與舊版完全一致。