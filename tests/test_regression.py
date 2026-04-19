# -*- coding: utf-8 -*-
"""
Regression Tests - Space-Raiden
防止已知邊界行為與狀態轉換邏輯退化，每條測試對應一個容易被改壞的行為。

執行方式: pytest tests/test_regression.py -v -s
"""
import pytest

pytestmark = pytest.mark.regression


def _print(msg):
    """Windows cp950 safe print"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def test_invincible_prevents_double_damage(playing_page):
    _print("\n[REGRESSION TEST] Test: Two asteroids same frame -> lives only decreases by 1")
    _print("  -> invincible flag must block the second hit within the same update()")
    result = playing_page.evaluate("""() => {
        lives = 3;
        invincible = 0;
        asteroids = [
            { x: player.x, y: player.y, r: 20, hp: 1, vx: 0, vy: 0 },
            { x: player.x, y: player.y, r: 20, hp: 1, vx: 0, vy: 0 },
        ];
        update();
        return lives;
    }""")
    assert result == 2
    _print(f"  [OK] lives={result} (only 1 deducted despite 2 simultaneous hits)")


def test_dead_state_blocks_laser(playing_page):
    _print("\n[REGRESSION TEST] Test: Space key in 'dead' state must NOT fire laser")
    _print("  -> keyboard handler only calls fireLaser() when state='playing'")
    playing_page.evaluate("() => { state = 'dead'; laserCooldown = 0; }")
    playing_page.keyboard.press("Space")
    result = playing_page.evaluate("() => lasers.length")
    assert result == 0
    _print(f"  [OK] lasers={result} (no laser fired in dead state)")


def test_score_stops_when_not_playing(playing_page):
    _print("\n[REGRESSION TEST] Test: Score must NOT increment when state != 'playing'")
    _print("  -> update() score logic must be gated by state check")
    playing_page.wait_for_timeout(300)
    playing_page.evaluate("() => { state = 'gameover'; }")
    score_before = playing_page.evaluate("() => score")
    playing_page.wait_for_timeout(500)
    score_after = playing_page.evaluate("() => score")
    assert score_after == score_before
    _print(f"  [OK] score stayed at {score_before} after 500ms in gameover state")


def test_dead_transitions_to_gameover(playing_page):
    _print("\n[REGRESSION TEST] Test: state='dead' must transition to 'gameover' after ~1200ms")
    _print("  -> setTimeout(1200) in game code triggers the transition")
    playing_page.evaluate("""() => {
        lives = 1;
        invincible = 0;
        asteroids = [{ x: player.x, y: player.y, r: 20, hp: 1, vx: 0, vy: 0 }];
        update();
    }""")
    state_dead = playing_page.evaluate("() => state")
    assert state_dead == "dead"
    playing_page.wait_for_timeout(1500)
    state_gameover = playing_page.evaluate("() => state")
    assert state_gameover == "gameover"
    _print(f"  [OK] dead → (1500ms) → gameover")


def test_restart_from_gameover(playing_page):
    _print("\n[REGRESSION TEST] Test: Space in 'gameover' state returns to menu, then starts game")
    _print("  -> gameover + Space -> menu, menu + Space -> startGame(player) -> playing")
    playing_page.evaluate("() => { state = 'gameover'; score = 999; lives = 1; }")
    playing_page.keyboard.press("Space")   # gameover -> menu
    playing_page.keyboard.press("Space")   # menu -> startGame (player mode, index=0)
    result = playing_page.evaluate("() => ({ state, score, lives })")
    assert result["state"] == "playing"
    assert result["score"] == 0
    assert result["lives"] == 3
    _print(f"  [OK] state={result['state']}, score={result['score']}, lives={result['lives']}")


def test_invincible_decrements_each_frame(playing_page):
    _print("\n[REGRESSION TEST] Test: invincible counter must decrement by 1 each frame")
    _print("  -> if (invincible > 0) invincible-- must run every update()")
    result = playing_page.evaluate("""() => {
        invincible = 120;
        update();
        return invincible;
    }""")
    assert result == 119
    _print(f"  [OK] invincible: 120 → {result} (decremented by 1)")


def test_shake_resets_on_gameover(playing_page):
    _print("\n[REGRESSION TEST] Test: shake must be 0 when state transitions to 'gameover'")
    _print("  -> setTimeout callback must reset shake=0 to prevent frozen screen shake")
    playing_page.evaluate("""() => {
        lives = 1;
        invincible = 0;
        asteroids = [{ x: player.x, y: player.y, r: 20, hp: 1, vx: 0, vy: 0 }];
        update();
    }""")
    playing_page.wait_for_timeout(1400)  # 等待 dead → gameover（1200ms）
    result = playing_page.evaluate("() => ({ state, shake })")
    assert result["state"] == "gameover"
    assert result["shake"] == 0
    _print(f"  [OK] state={result['state']}, shake={result['shake']} (no residual screen shake)")


def test_shake_resets_on_menu(playing_page):
    _print("\n[REGRESSION TEST] Test: shake must be 0 when returning to menu from gameover")
    _print("  -> Space/Enter from gameover must clear shake to prevent menu screen shake")
    playing_page.evaluate("() => { state = 'gameover'; shake = 15; }")
    playing_page.keyboard.press("Space")  # gameover → menu
    result = playing_page.evaluate("() => ({ state, shake })")
    assert result["state"] == "menu"
    assert result["shake"] == 0
    _print(f"  [OK] state={result['state']}, shake={result['shake']} (shake cleared on menu entry)")


def test_ai_mode_pause_on_esc(playing_page):
    _print("\n[REGRESSION TEST] Test: AI mode ESC -> state becomes 'paused'")
    playing_page.evaluate("() => startGame('ai')")
    playing_page.keyboard.press("Escape")
    result = playing_page.evaluate("state")
    assert result == "paused"
    _print(f"  [OK] AI mode state={result}")
