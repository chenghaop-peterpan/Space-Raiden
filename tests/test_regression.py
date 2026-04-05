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


def test_invincible_prevents_double_damage(game_page):
    _print("\n[REGRESSION TEST] Test: Two asteroids same frame -> lives only decreases by 1")
    _print("  -> invincible flag must block the second hit within the same update()")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(200)
    result = game_page.evaluate("""() => {
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


def test_dead_state_blocks_laser(game_page):
    _print("\n[REGRESSION TEST] Test: Space key in 'dead' state must NOT fire laser")
    _print("  -> keyboard handler only calls fireLaser() when state='playing'")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(200)
    game_page.evaluate("() => { state = 'dead'; laserCooldown = 0; }")
    game_page.keyboard.press("Space")
    result = game_page.evaluate("() => lasers.length")
    assert result == 0
    _print(f"  [OK] lasers={result} (no laser fired in dead state)")


def test_score_stops_when_not_playing(game_page):
    _print("\n[REGRESSION TEST] Test: Score must NOT increment when state != 'playing'")
    _print("  -> update() score logic must be gated by state check")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(300)
    game_page.evaluate("() => { state = 'gameover'; }")
    score_before = game_page.evaluate("() => score")
    game_page.wait_for_timeout(500)
    score_after = game_page.evaluate("() => score")
    assert score_after == score_before
    _print(f"  [OK] score stayed at {score_before} after 500ms in gameover state")


def test_dead_transitions_to_gameover(game_page):
    _print("\n[REGRESSION TEST] Test: state='dead' must transition to 'gameover' after ~1200ms")
    _print("  -> setTimeout(1200) in game code triggers the transition")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(200)
    game_page.evaluate("""() => {
        lives = 1;
        invincible = 0;
        asteroids = [{ x: player.x, y: player.y, r: 20, hp: 1, vx: 0, vy: 0 }];
        update();
    }""")
    state_dead = game_page.evaluate("() => state")
    assert state_dead == "dead"
    game_page.wait_for_timeout(1500)
    state_gameover = game_page.evaluate("() => state")
    assert state_gameover == "gameover"
    _print(f"  [OK] dead → (1500ms) → gameover")


def test_restart_from_gameover(game_page):
    _print("\n[REGRESSION TEST] Test: Space in 'gameover' state returns to menu, then starts game")
    _print("  -> gameover + Space -> menu, menu + Space -> startGame(player) -> playing")
    game_page.evaluate("() => { state = 'gameover'; score = 999; lives = 1; }")
    game_page.keyboard.press("Space")   # gameover -> menu
    game_page.keyboard.press("Space")   # menu -> startGame (player mode, index=0)
    result = game_page.evaluate("() => ({ state, score, lives })")
    assert result["state"] == "playing"
    assert result["score"] == 0
    assert result["lives"] == 3
    _print(f"  [OK] state={result['state']}, score={result['score']}, lives={result['lives']}")


def test_invincible_decrements_each_frame(game_page):
    _print("\n[REGRESSION TEST] Test: invincible counter must decrement by 1 each frame")
    _print("  -> if (invincible > 0) invincible-- must run every update()")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(200)
    result = game_page.evaluate("""() => {
        invincible = 120;
        update();
        return invincible;
    }""")
    assert result == 119
    _print(f"  [OK] invincible: 120 → {result} (decremented by 1)")
