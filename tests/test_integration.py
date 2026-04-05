# -*- coding: utf-8 -*-
"""
Integration Tests - Space-Raiden
測試多個子系統協同運作的行為：透過真實 game loop 驗收，需等待時間。
涵蓋：asteroid 自然生成、四向邊界 clamp（input → 物理 → 邊界限制）

執行方式: pytest tests/test_integration.py -v -s
"""
import pytest

pytestmark = pytest.mark.integration


def _print(msg):
    """Windows cp950 safe print"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def test_spawn_asteroid_increases_count(game_page):
    _print("\n[INTEGRATION TEST] Test: After 3 seconds of gameplay, asteroids should appear")
    _print("  -> Action: Press Space twice to start, wait 3 seconds for natural spawning")
    game_page.keyboard.press("Space")   # start -> menu
    game_page.keyboard.press("Space")   # menu -> playing
    game_page.wait_for_timeout(3000)

    count = game_page.evaluate("() => asteroids.length")
    assert count > 0
    _print(f"  [OK] {count} asteroids on screen")


def test_spawn_asteroid_properties(game_page):
    _print("\n[INTEGRATION TEST] Test: Verify asteroid physical properties match spec")
    _print("  -> Action: Press Space twice to start, wait 3 seconds for asteroids to spawn")
    game_page.keyboard.press("Space")   # start -> menu
    game_page.keyboard.press("Space")   # menu -> playing
    game_page.wait_for_timeout(3000)

    asteroid = game_page.evaluate("() => asteroids[0]")
    assert asteroid["r"] >= 18
    assert asteroid["vy"] > 0
    assert asteroid["hp"] >= 1
    _print(f"  [OK] radius={asteroid['r']:.1f}, vy={asteroid['vy']:.2f}, hp={asteroid['hp']}")


def test_boundary_left(game_page):
    _print("\n[INTEGRATION TEST] Test: Hold ArrowLeft long enough -> player should stop at left boundary")
    _print("  -> Action: Start game -> hold ArrowLeft 3s -> verify x >= player.w/2 (=18)")
    game_page.keyboard.press("Space")   # start -> menu
    game_page.keyboard.press("Space")   # menu -> playing
    game_page.keyboard.down("ArrowLeft")
    game_page.wait_for_timeout(3000)
    game_page.keyboard.up("ArrowLeft")
    result = game_page.evaluate("() => ({ x: player.x, min: player.w / 2 })")
    assert result["x"] >= result["min"]
    _print(f"  [OK] x={result['x']:.1f}, left boundary={result['min']:.1f} (clamped correctly)")


def test_boundary_right(game_page):
    _print("\n[INTEGRATION TEST] Test: Hold ArrowRight long enough -> player should stop at right boundary")
    _print("  -> Action: Start game -> hold ArrowRight 3s -> verify x <= W - player.w/2 (=462)")
    game_page.keyboard.press("Space")   # start -> menu
    game_page.keyboard.press("Space")   # menu -> playing
    game_page.keyboard.down("ArrowRight")
    game_page.wait_for_timeout(3000)
    game_page.keyboard.up("ArrowRight")
    result = game_page.evaluate("() => ({ x: player.x, max: W - player.w / 2 })")
    assert result["x"] <= result["max"]
    _print(f"  [OK] x={result['x']:.1f}, right boundary={result['max']:.1f} (clamped correctly)")


def test_boundary_top(game_page):
    _print("\n[INTEGRATION TEST] Test: Hold ArrowUp long enough -> player should stop at top boundary")
    _print("  -> Action: Start game -> hold ArrowUp 3s -> verify y >= player.h/2 (=28)")
    game_page.keyboard.press("Space")   # start -> menu
    game_page.keyboard.press("Space")   # menu -> playing
    game_page.keyboard.down("ArrowUp")
    game_page.wait_for_timeout(3000)
    game_page.keyboard.up("ArrowUp")
    result = game_page.evaluate("() => ({ y: player.y, min: player.h / 2 })")
    assert result["y"] >= result["min"]
    _print(f"  [OK] y={result['y']:.1f}, top boundary={result['min']:.1f} (clamped correctly)")


def test_boundary_bottom(game_page):
    _print("\n[INTEGRATION TEST] Test: Hold ArrowDown long enough -> player should stop at bottom boundary")
    _print("  -> Action: Start game -> hold ArrowDown 3s -> verify y <= H - player.h/2 (=612)")
    game_page.keyboard.press("Space")   # start -> menu
    game_page.keyboard.press("Space")   # menu -> playing
    game_page.keyboard.down("ArrowDown")
    game_page.wait_for_timeout(3000)
    game_page.keyboard.up("ArrowDown")
    result = game_page.evaluate("() => ({ y: player.y, max: H - player.h / 2 })")
    assert result["y"] <= result["max"]
    _print(f"  [OK] y={result['y']:.1f}, bottom boundary={result['max']:.1f} (clamped correctly)")


# ── Scoring & Game Loop Tests ─────────────────────────────────────────────────

def test_score_dom_syncs_with_js(game_page):
    _print("\n[INTEGRATION TEST] Test: JS score change should reflect in #score DOM")
    _print("  -> Action: Start game -> set score=999 -> wait for game loop -> verify DOM == JS score")
    game_page.keyboard.press("Space")   # start -> menu
    game_page.keyboard.press("Space")   # menu -> playing
    game_page.wait_for_timeout(200)
    game_page.evaluate("() => { score = 999; }")
    game_page.wait_for_timeout(200)
    dom_score = int(game_page.locator("#score").inner_text())
    js_score = game_page.evaluate("() => score")
    assert dom_score == js_score
    assert dom_score >= 999
    _print(f"  [OK] #score DOM = '{dom_score}', JS score = {js_score} (synced)")


def test_laser_destroys_asteroid_and_scores(game_page):
    _print("\n[INTEGRATION TEST] Test: Laser hitting asteroid -> asteroid removed + score increases")
    _print("  -> Action: Start game -> fix player pos -> place asteroid in laser path -> fire -> wait -> verify")
    game_page.keyboard.press("Space")   # start -> menu
    game_page.keyboard.press("Space")   # menu -> playing
    game_page.wait_for_timeout(200)
    initial_score = game_page.evaluate("""() => {
        player.x = 240; player.y = 550; player.vx = 0; player.vy = 0;
        asteroids = [{ x: 240, y: 470, r: 20, hp: 1, vx: 0, vy: 0, _test: true }];
        laserCooldown = 0;
        fireLaser();
        return score;
    }""")
    game_page.wait_for_timeout(800)
    result = game_page.evaluate("() => ({ remaining: asteroids.filter(a => a._test).length, score })")
    assert result["remaining"] == 0
    assert result["score"] >= initial_score + 15
    _print(f"  [OK] test asteroid destroyed, score gained={result['score'] - initial_score}")
