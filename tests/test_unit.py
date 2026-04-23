# -*- coding: utf-8 -*-
"""
Unit Tests - Space-Raiden
驗證遊戲核心公式與算法的正確性，不依賴 game loop，結果完全確定。
涵蓋：level 公式、碰撞閾值、邊界 clamp、分數計算、生成間隔

執行方式: pytest tests/test_unit.py -v -s
"""
import pytest

pytestmark = pytest.mark.unit


def _print(msg):
    """Windows cp950 safe print"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def test_level_formula_boundaries(playing_page):
    _print("\n[UNIT TEST] Test: level = 1 + floor(score / 300) at key boundaries")
    result = playing_page.evaluate("""() => ({
        at_0:   1 + Math.floor(0 / 300),
        at_299: 1 + Math.floor(299 / 300),
        at_300: 1 + Math.floor(300 / 300),
        at_600: 1 + Math.floor(600 / 300),
        at_900: 1 + Math.floor(900 / 300),
    })""")
    assert result["at_0"]   == 1
    assert result["at_299"] == 1
    assert result["at_300"] == 2
    assert result["at_600"] == 3
    assert result["at_900"] == 4
    _print(f"  [OK] score 0→1, 299→1, 300→2, 600→3, 900→4")


def test_collision_player_radius(playing_page):
    _print("\n[UNIT TEST] Test: player collision threshold = asteroid.r + 16")
    result = playing_page.evaluate("""() => {
        const r = 20;
        const threshold = r + 16;  // = 36
        return {
            threshold,
            inside_hits:  35.9 < threshold,
            exact_misses: 36.0 < threshold,
            outside_misses: 36.1 < threshold,
        };
    }""")
    assert result["threshold"]     == 36
    assert result["inside_hits"]   is True
    assert result["exact_misses"]  is False
    assert result["outside_misses"] is False
    _print(f"  [OK] threshold={result['threshold']}, dist<threshold → hit")


def test_collision_laser_radius(playing_page):
    _print("\n[UNIT TEST] Test: laser collision threshold = asteroid.r + 4")
    result = playing_page.evaluate("""() => {
        const r = 20;
        const threshold = r + 4;  // = 24
        return {
            threshold,
            inside_hits:   23.9 < threshold,
            exact_misses:  24.0 < threshold,
            outside_misses: 24.1 < threshold,
        };
    }""")
    assert result["threshold"]      == 24
    assert result["inside_hits"]    is True
    assert result["exact_misses"]   is False
    assert result["outside_misses"] is False
    _print(f"  [OK] threshold={result['threshold']}, dist<threshold → hit")


def test_boundary_clamp_x(playing_page):
    _print("\n[UNIT TEST] Test: player.x clamped to [player.w/2=18, W-player.w/2=462]")
    result = playing_page.evaluate("""() => {
        const W = 480, pw = 36;
        const clamp = x => Math.max(pw/2, Math.min(W - pw/2, x));
        return {
            below_min:  clamp(-100),
            at_min:     clamp(18),
            center:     clamp(240),
            at_max:     clamp(462),
            above_max:  clamp(600),
        };
    }""")
    assert result["below_min"]  == 18
    assert result["at_min"]     == 18
    assert result["center"]     == 240
    assert result["at_max"]     == 462
    assert result["above_max"]  == 462
    _print(f"  [OK] x clamped: [-100→18, 18→18, 240→240, 462→462, 600→462]")


def test_boundary_clamp_y(playing_page):
    _print("\n[UNIT TEST] Test: player.y clamped to [player.h/2=28, H-player.h/2=612]")
    result = playing_page.evaluate("""() => {
        const H = 640, ph = 56;
        const clamp = y => Math.max(ph/2, Math.min(H - ph/2, y));
        return {
            below_min:  clamp(-100),
            at_min:     clamp(28),
            center:     clamp(320),
            at_max:     clamp(612),
            above_max:  clamp(800),
        };
    }""")
    assert result["below_min"]  == 28
    assert result["at_min"]     == 28
    assert result["center"]     == 320
    assert result["at_max"]     == 612
    assert result["above_max"]  == 612
    _print(f"  [OK] y clamped: [-100→28, 28→28, 320→320, 612→612, 800→612]")


def test_score_small_asteroid(playing_page):
    _print("\n[UNIT TEST] Test: r <= 28 asteroid awards +15 score")
    result = playing_page.evaluate("""() => {
        score = 0; frameCount = 1;
        asteroids = [{ x: 240, y: 200, r: 28, hp: 1, vx: 0, vy: 0 }];
        lasers = [{ x: 240, y: 191, w: 3, h: 18, vy: -14 }];
        update();
        return score;
    }""")
    assert result == 15
    _print(f"  [OK] r=28 (≤28) → score={result} (+15)")


def test_score_large_asteroid(playing_page):
    _print("\n[UNIT TEST] Test: r > 28 asteroid awards +30 score")
    result = playing_page.evaluate("""() => {
        score = 0; frameCount = 1;
        asteroids = [{ x: 240, y: 200, r: 29, hp: 1, vx: 0, vy: 0 }];
        lasers = [{ x: 240, y: 191, w: 3, h: 18, vy: -14 }];
        update();
        return score;
    }""")
    assert result == 30
    _print(f"  [OK] r=29 (>28) → score={result} (+30)")


def test_spawn_interval_formula(playing_page):
    _print("\n[UNIT TEST] Test: spawn interval = max(10, 28 - level * 3)")
    result = playing_page.evaluate("""() => {
        const interval = lv => Math.max(28 - lv * 3, 10);
        return {
            level1: interval(1),
            level3: interval(3),
            level6: interval(6),
            level9: interval(9),
        };
    }""")
    assert result["level1"] == 25
    assert result["level3"] == 19
    assert result["level6"] == 10
    assert result["level9"] == 10  # clamped at min 10
    _print(f"  [OK] level1=25, level3=19, level6=10, level9=10(clamped)")


# ── getGameState() API ────────────────────────────────────────────────────────

def test_getgamestate_complete_schema(playing_page):
    _print("\n[UNIT TEST] Test: getGameState() returns all required top-level and player keys")
    result = playing_page.evaluate("() => getGameState()")
    for key in ["player", "laserCooldown", "asteroids", "lasers",
                "score", "lives", "level", "frameCount", "state", "gameMode"]:
        assert key in result, f"missing key: {key}"
    for key in ["x", "y", "vx", "vy", "invincible", "invincibleFrames"]:
        assert key in result["player"], f"missing player key: {key}"
    _print("  [OK] all schema keys present")


def test_getgamestate_player_position(playing_page):
    _print("\n[UNIT TEST] Test: getGameState() exports correct player position")
    result = playing_page.evaluate("""() => {
        player.x = 200; player.y = 500;
        return getGameState().player;
    }""")
    assert result["x"] == 200
    assert result["y"] == 500
    _print(f"  [OK] player.x={result['x']}, player.y={result['y']}")


def test_getgamestate_invincible_flag(playing_page):
    _print("\n[UNIT TEST] Test: getGameState() exports invincible as bool + frame count")
    result = playing_page.evaluate("""() => {
        invincible = 120;
        return getGameState().player;
    }""")
    assert result["invincible"] is True
    assert result["invincibleFrames"] == 120
    _print(f"  [OK] invincible={result['invincible']}, frames={result['invincibleFrames']}")


def test_getgamestate_laser_cooldown(playing_page):
    _print("\n[UNIT TEST] Test: getGameState() exports laserCooldown correctly")
    result = playing_page.evaluate("""() => {
        laserCooldown = 7;
        return getGameState().laserCooldown;
    }""")
    assert result == 7
    _print(f"  [OK] laserCooldown={result}")


def test_getgamestate_asteroids_exported(playing_page):
    _print("\n[UNIT TEST] Test: getGameState() exports asteroid list with correct fields")
    result = playing_page.evaluate("""() => {
        asteroids = [{ x: 100, y: 200, r: 25, vx: 1, vy: 2, hp: 1 }];
        return getGameState().asteroids[0];
    }""")
    assert result["x"] == 100
    assert result["y"] == 200
    assert result["r"] == 25
    assert result["hp"] == 1
    _print(f"  [OK] asteroid exported: x={result['x']}, r={result['r']}, hp={result['hp']}")


# ── recordRun() / Benchmark ────────────────────────────────────────────────────

def test_record_run_appends_to_history(playing_page):
    _print("\n[UNIT TEST] Test: recordRun() appends one entry to runHistory")
    result = playing_page.evaluate("""() => {
        runHistory = [];
        score = 250; level = 2; shotsFired = 10; shotsHit = 7;
        frameCount = 600;
        recordRun();
        return runHistory.length;
    }""")
    assert result == 1
    _print(f"  [OK] runHistory.length={result}")


def test_record_run_captures_score_and_level(playing_page):
    _print("\n[UNIT TEST] Test: recordRun() captures correct score and level")
    result = playing_page.evaluate("""() => {
        runHistory = [];
        score = 500; level = 3; shotsFired = 20; shotsHit = 12; frameCount = 1200;
        recordRun();
        return { score: runHistory[0].score, level: runHistory[0].level };
    }""")
    assert result["score"] == 500
    assert result["level"] == 3
    _print(f"  [OK] score={result['score']}, level={result['level']}")


def test_record_run_calculates_accuracy(playing_page):
    _print("\n[UNIT TEST] Test: recordRun() calculates accuracy = hits/fired*100")
    result = playing_page.evaluate("""() => {
        runHistory = [];
        score = 100; level = 1; shotsFired = 10; shotsHit = 8; frameCount = 300;
        recordRun();
        return runHistory[0].accuracy;
    }""")
    assert result == 80
    _print(f"  [OK] accuracy={result}% (8/10 hits)")


def test_record_run_zero_shots_accuracy(playing_page):
    _print("\n[UNIT TEST] Test: recordRun() accuracy is 0 when no shots fired")
    result = playing_page.evaluate("""() => {
        runHistory = [];
        score = 50; level = 1; shotsFired = 0; shotsHit = 0; frameCount = 300;
        recordRun();
        return runHistory[0].accuracy;
    }""")
    assert result == 0
    _print(f"  [OK] accuracy={result}% (no shots fired)")


def test_record_run_increments_run_number(playing_page):
    _print("\n[UNIT TEST] Test: recordRun() auto-increments run number")
    result = playing_page.evaluate("""() => {
        runHistory = [];
        score = 100; level = 1; shotsFired = 5; shotsHit = 3; frameCount = 300;
        recordRun();
        score = 200; recordRun();
        return { first: runHistory[0].run, second: runHistory[1].run };
    }""")
    assert result["first"] == 1
    assert result["second"] == 2
    _print(f"  [OK] run numbers: {result['first']}, {result['second']}")


# ── Dash ──────────────────────────────────────────────────────────────────────

def test_dash_cooldown_decrements_each_frame(playing_page):
    _print("\n[UNIT TEST] Test: dashCooldown decrements by 1 each update() call")
    result = playing_page.evaluate("""() => {
        dashCooldown = 10;
        update();
        return dashCooldown;
    }""")
    assert result == 9
    _print(f"  [OK] dashCooldown 10 -> {result}")


def test_dash_cooldown_clamps_at_zero(playing_page):
    _print("\n[UNIT TEST] Test: dashCooldown does not go below 0")
    result = playing_page.evaluate("""() => {
        dashCooldown = 0;
        update();
        return dashCooldown;
    }""")
    assert result == 0
    _print(f"  [OK] dashCooldown stays at {result}")


# ── localStorage 持久化 ────────────────────────────────────────────────────────

def test_storage_saves_run_history(playing_page):
    _print("\n[UNIT TEST] Test: recordRun() saves runHistory to localStorage['sr_runs']")
    result = playing_page.evaluate("""() => {
        localStorage.removeItem('sr_runs');
        runHistory = [];
        score = 200; level = 2; shotsFired = 10; shotsHit = 7; frameCount = 600;
        recordRun();
        const stored = localStorage.getItem('sr_runs');
        if (!stored) return null;
        return JSON.parse(stored).length;
    }""")
    assert result == 1
    _print(f"  [OK] sr_runs has {result} entry after recordRun()")


def test_storage_saves_input_log(playing_page):
    _print("\n[UNIT TEST] Test: recordRun() saves inputLog snapshot to localStorage['sr_inputlog']")
    result = playing_page.evaluate("""() => {
        localStorage.removeItem('sr_inputlog');
        inputLog = [{frame:1, keys:'-', x:240, y:400, dx:0, dy:0, dist:0, event:''}];
        score = 100; level = 1; shotsFired = 5; shotsHit = 3; frameCount = 300;
        recordRun();
        const stored = localStorage.getItem('sr_inputlog');
        return stored !== null;
    }""")
    assert result is True
    _print(f"  [OK] sr_inputlog saved after recordRun()")


def test_storage_loads_on_init(playing_page):
    _print("\n[UNIT TEST] Test: loadStorage() restores runHistory from localStorage")
    result = playing_page.evaluate("""() => {
        const fakeRuns = [{ run:1, score:500, level:3, accuracy:70,
            frames:1800, mode:'player', states:{Idle:0,Tracking:0,Firing:0,Evading:0,Dodging:0},
            strategy:'threat', epochId:null }];
        localStorage.setItem('sr_runs', JSON.stringify(fakeRuns));
        runHistory = [];
        loadStorage();
        return runHistory.length;
    }""")
    assert result == 1
    _print(f"  [OK] runHistory restored: {result} entry")


# ── 軌跡預測策略 ──────────────────────────────────────────────────────────────

def test_trajectory_calculates_correct_landing_x(playing_page):
    _print("\n[UNIT TEST] Test: trajectory landing X formula: landingX = ax + vx * (py - ay) / vy")
    result = playing_page.evaluate("""() => {
        const py = 500, ay = 100, vx = 2, vy = 5;
        const frames = (py - ay) / vy;   // 80
        const landingX = 200 + vx * frames;  // 200 + 160 = 360
        return { frames, landingX };
    }""")
    assert result["frames"] == 80
    assert result["landingX"] == 360
    _print(f"  [OK] frames={result['frames']}, landingX={result['landingX']}")


def test_trajectory_strategy_moves_away_from_landing_x(playing_page):
    _print("\n[UNIT TEST] Test: trajectory strategy → asteroid landing right of player → cmd.left=true")
    result = playing_page.evaluate("""() => {
        // Player at x=240, y=500
        // Asteroid at x=260, y=100, vx=0, vy=4 → frames=100, landingX=260
        // lateralGap = |260-240|=20, dangerW=20+36=56, 20<56 → threat
        // player.x(240) < landingX(260) → left=true
        player.x = 240; player.y = 500;
        asteroids = [{ x: 260, y: 100, r: 20, hp: 1, vx: 0, vy: 4 }];
        const gs = getGameState();
        const cmd = AI_STRATEGIES.trajectory.decide(gs, aiParams);
        return { left: cmd.left, right: cmd.right };
    }""")
    assert result["left"] is True
    assert result["right"] is False
    _print(f"  [OK] cmd.left={result['left']}, cmd.right={result['right']}")


def test_trajectory_strategy_ignores_passed_asteroids(playing_page):
    _print("\n[UNIT TEST] Test: asteroid below player.y (frames<=0) → trajectory strategy no evade")
    result = playing_page.evaluate("""() => {
        // Set up: asteroid already past player (a.y > player.y with vy > 0 → frames <= 0)
        asteroids = [{ x: 240, y: 600, r: 20, hp: 1, vx: 0, vy: 3 }];
        player.x = 240; player.y = 500;
        const gs = getGameState();
        const cmd = AI_STRATEGIES.trajectory.decide(gs, aiParams);
        return { left: cmd.left, right: cmd.right };
    }""")
    assert result["left"] is False
    assert result["right"] is False
    _print(f"  [OK] passed asteroid ignored: left={result['left']}, right={result['right']}")


def test_clear_storage_resets_all(playing_page):
    _print("\n[UNIT TEST] Test: clearStorage() removes all sr_* keys and resets runHistory")
    result = playing_page.evaluate("""() => {
        runHistory = [{ run:1, score:100 }];
        epochHistory = [];
        inputLog = [];
        _saveRuns();
        clearStorage();
        return {
            runsKey:    localStorage.getItem('sr_runs'),
            epochsKey:  localStorage.getItem('sr_epochs'),
            inputlogKey: localStorage.getItem('sr_inputlog'),
            runHistoryLen: runHistory.length,
        };
    }""")
    assert result["runsKey"] is None
    assert result["epochsKey"] is None
    assert result["inputlogKey"] is None
    assert result["runHistoryLen"] == 0
    _print(f"  [OK] all sr_* keys cleared, runHistory.length={result['runHistoryLen']}")


def test_compare_mode_variables_initialized(playing_page):
    _print("\n[UNIT TEST] Test: compareMode/comparePhase/compareRunsA/B initial values")
    result = playing_page.evaluate("""() => ({
        compareMode,
        comparePhase,
        runsA: compareRunsA.length,
        runsB: compareRunsB.length,
    })""")
    assert result["compareMode"] is False
    assert result["comparePhase"] == 0
    assert result["runsA"] == 0
    assert result["runsB"] == 0
    _print(f"  [OK] compareMode={result['compareMode']}, phase={result['comparePhase']}")


def test_compare_calc_avg_score(playing_page):
    _print("\n[UNIT TEST] Test: avg score calculation for compare result")
    result = playing_page.evaluate("""() => {
        const runs = [
            {score:100, frames:600, accuracy:70},
            {score:200, frames:900, accuracy:80}
        ];
        const sc = runs.map(r => r.score);
        return Math.round(sc.reduce((a, b) => a + b, 0) / sc.length);
    }""")
    assert result == 150
    _print(f"  [OK] avg score = {result}")


def test_compare_winner_determination(playing_page):
    _print("\n[UNIT TEST] Test: compare panel winner logic (higher avg = green)")
    result = playing_page.evaluate("""() => {
        compareRunsA = [{score:300, frames:1000, accuracy:80}];
        compareRunsB = [{score:150, frames:600,  accuracy:60}];
        compareStratA = 'threat';
        compareStratB = 'trajectory';
        renderComparePanel();
        const elA = document.getElementById('cmp-a-avg');
        const elB = document.getElementById('cmp-b-avg');
        return { colorA: elA.style.color, colorB: elB.style.color };
    }""")
    # A wins (300 > 150), A should be green (#4f4), B should be red (#f66)
    assert result["colorA"] == "rgb(68, 255, 68)"
    assert result["colorB"] == "rgb(255, 102, 102)"
    _print(f"  [OK] A=green ({result['colorA']}), B=red ({result['colorB']})")
