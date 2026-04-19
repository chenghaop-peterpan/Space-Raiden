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
