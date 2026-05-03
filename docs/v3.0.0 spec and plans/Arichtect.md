# Space-Raiden System Architecture

## 1. 核心四層架構 (4-Module Architecture)

系統由四個完全獨立的模組組成，嚴格遵守單向資料流與介面隔離原則：

1. **Game Engine (遊戲引擎)**: 純邏輯結算，無渲染。管理 Engine State 與接收 Engine Action。
2. **Adapter (轉接器/包裝器)**: 處理空間轉換、特徵工程與 Reward Shaping。每個 Agent 擁有獨立實例。分為 `StatelessAdapter` 與 `StatefulAdapter`。
3. **AI Agent (代理大腦)**: 封裝演算法，接收 Observation，輸出 Model Action。
4. **Renderer (渲染器)**: 獨立的 UI 監聽層，將 Engine State 繪製至 Canvas。訓練時完全卸載。

## 2. 系統資料流 (System Flow)

以下 Mermaid 圖表展示了從設定檔裝配到遊戲迴圈的完整資料流向：

```mermaid
flowchart TD
    %% 設定與裝配區塊
    subgraph Initialization [Factory Pattern & Injection]
        direction TB
        Config[Run Config JSON\n包含 Env, Adapter, Agent 設定]
        Builder{Sandbox Builder}
        
        Config --> Builder
    end

    %% 運行時迴圈區塊
    subgraph RuntimeLoop [Headless Runtime Loop]
        direction LR
        Engine((1. Game Engine))
        Adapter{{2. Adapter Wrapper}}
        Model[3. AI Agent]

        Engine -- "Engine State\n(Object/Map)" --> Adapter
        Adapter -- "Observation\n(Float32Array)" --> Model
        Model -- "Model Action\n(Logits/Continuous)" --> Adapter
        Adapter -- "Engine Action\n(Boolean Dict)" --> Engine
        
        %% Reward Feedback
        Engine -. "Raw Reward & Done" .-> Adapter
        Adapter -. "Shaped Reward" .-> Model
    end

    %% 渲染層 (可選)
    Renderer[[4. Renderer UI]]
    Engine -. "State Updates\n(Event Emitter)" .-> Renderer

    %% 注入關係
    Builder ==>|Inject| Engine
    Builder ==>|Inject| Adapter
    Builder ==>|Inject| Model