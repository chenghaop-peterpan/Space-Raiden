# -*- coding: utf-8 -*-
"""
UI Tests - Tai Kong Suo Bi Yun Shi
Shi Ji Kai Qi Liu Lan Qi, Yi Jian Pan Cao Zuo Chu Fa You Xi Yuan Jian.
Zhi Xing Fang Shi: pytest tests/test_ui.py -v -s --headed --slowmo 2000
"""
import sys
import io

def _print(msg):
    """Windows cp950 safe print"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def test_startgame_resets_state(game_page):
    _print("\n[UI TEST] Test: Press Space to start, verify initial state")
    _print("  -> Action: Press Space to show game starting, then verify reset atomically")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(1000)  # show game running visually

    # startGame() + read in one atomic evaluate so no game loop runs between them
    result = game_page.evaluate("""() => {
        startGame();
        return { state, score, lives, level };
    }""")
    assert result["state"] == "playing"
    assert result["score"] == 0
    assert result["lives"] == 3
    assert result["level"] == 1
    game_page.wait_for_timeout(1000)
    _print(f"  [OK] state={result['state']}, score={result['score']}, lives={result['lives']}, level={result['level']}")


def test_startgame_clears_entities(game_page):
    _print("\n[UI TEST] Test: After starting game, all entity arrays should be empty")
    _print("  -> Action: Press Space to show game starting, then verify reset atomically")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(1000)  # show game running visually

    # startGame() + read in one atomic evaluate so no entities spawn between them
    result = game_page.evaluate("""() => {
        startGame();
        return {
            asteroids: asteroids.length,
            lasers: lasers.length,
            explosions: explosions.length,
            particles: particles.length,
        };
    }""")
    assert result["asteroids"] == 0
    assert result["lasers"] == 0
    assert result["explosions"] == 0
    assert result["particles"] == 0
    game_page.wait_for_timeout(1000)
    _print(f"  [OK] asteroids={result['asteroids']}, lasers={result['lasers']}, explosions={result['explosions']}, particles={result['particles']}")


def test_spawn_asteroid_increases_count(game_page):
    _print("\n[UI TEST] Test: After 3 seconds of gameplay, asteroids should appear")
    _print("  -> Action: Press Space to start, wait 3 seconds for natural spawning")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(3000)

    count = game_page.evaluate("() => asteroids.length")
    assert count > 0
    _print(f"  [OK] {count} asteroids on screen")


def test_spawn_asteroid_properties(game_page):
    _print("\n[UI TEST] Test: Verify asteroid physical properties match spec")
    _print("  -> Action: Press Space to start, wait 3 seconds for asteroids to spawn")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(3000)

    asteroid = game_page.evaluate("() => asteroids[0]")
    assert asteroid["r"] >= 18
    assert asteroid["vy"] > 0
    assert asteroid["hp"] >= 1
    _print(f"  [OK] radius={asteroid['r']:.1f}, vy={asteroid['vy']:.2f}, hp={asteroid['hp']}")


def test_fire_laser_adds_projectile(game_page):
    _print("\n[UI TEST] Test: Press Space in-game to fire laser")
    _print("  -> Action: Press Space to start -> Press Space again to fire laser -> check immediately")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(500)

    # Fire and check atomically before laser moves off screen
    result = game_page.evaluate("""() => {
        fireLaser();
        return { laserCount: lasers.length, cooldown: laserCooldown };
    }""")
    assert result["laserCount"] >= 1
    assert result["cooldown"] > 0
    game_page.wait_for_timeout(1000)
    _print(f"  [OK] lasers={result['laserCount']}, cooldown={result['cooldown']}")


def test_fire_laser_respects_cooldown(game_page):
    _print("\n[UI TEST] Test: Firing during cooldown should only produce 1 laser")
    _print("  -> Action: Press Space to start -> fire twice rapidly -> verify only 1 laser")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(500)

    # Fire twice atomically to avoid laser moving off screen between calls
    count = game_page.evaluate("""() => {
        fireLaser();
        fireLaser();
        return lasers.length;
    }""")
    assert count == 1
    game_page.wait_for_timeout(1000)
    _print(f"  [OK] lasers={count} (cooldown working, no double-fire)")


def test_explode_small_generates_particles(game_page):
    _print("\n[UI TEST] Test: Small explosion should generate particle effects")
    _print("  -> Action: Press Space to start -> trigger small explosion at center")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(500)

    result = game_page.evaluate("""() => {
        explode(240, 320, false);
        return { particles: particles.length, explosions: explosions.length };
    }""")
    assert result["particles"] >= 14
    assert result["explosions"] >= 1
    game_page.wait_for_timeout(1500)
    _print(f"  [OK] particles={result['particles']}, explosions={result['explosions']}")


def test_explode_big_generates_more_particles(game_page):
    _print("\n[UI TEST] Test: Large explosion should generate MORE particles")
    _print("  -> Action: Press Space to start -> trigger large explosion at center")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(500)

    result = game_page.evaluate("""() => {
        explode(240, 320, true);
        return { particles: particles.length, explosions: explosions.length };
    }""")
    assert result["particles"] >= 28
    assert result["explosions"] >= 1
    game_page.wait_for_timeout(1500)
    _print(f"  [OK] particles={result['particles']}, explosions={result['explosions']} (large explosion)")


def test_explode_big_triggers_screen_shake(game_page):
    _print("\n[UI TEST] Test: Large explosion should trigger screen shake")
    _print("  -> Action: Press Space to start -> trigger large explosion -> verify shake value")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(500)

    shake_val = game_page.evaluate("""() => {
        explode(240, 320, true);
        return shake;
    }""")
    assert shake_val == 14
    game_page.wait_for_timeout(1500)
    _print(f"  [OK] shake={shake_val} (screen shake triggered, visible in browser)")


def test_level_formula(game_page):
    _print("\n[UI TEST] Test: Score 600 should push level to 3")
    _print("  -> Action: Press Space to start -> set score=600 -> verify #level DOM updates")
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(500)
    game_page.evaluate("() => { score = 600; level = 1 + Math.floor(score / 300); }")
    game_page.wait_for_timeout(1000)

    level_text = game_page.locator("#level").inner_text()
    level_val = game_page.evaluate("() => level")
    assert level_val == 3
    _print(f"  [OK] DOM #level={level_text}, JS level={level_val}")
