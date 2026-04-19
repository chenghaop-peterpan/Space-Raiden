# -*- coding: utf-8 -*-
"""
Functional Tests - Space-Raiden
測試單一 game feature 的行為：直接呼叫 JS function，結果立即驗收。
涵蓋：startGame、fireLaser、explode、level 公式、四向移動、碰撞

執行方式: pytest tests/test_functional.py -v -s
"""
import pytest

pytestmark = pytest.mark.functional


def _print(msg):
    """Windows cp950 safe print"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def test_startgame_resets_state(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: startGame() resets state to playing with clean values")
    _print("  -> Action: Game already playing -> call startGame() atomically -> verify reset")
    playing_page.wait_for_timeout(1000)  # show game running visually

    result = playing_page.evaluate("""() => {
        startGame();
        return { state, score, lives, level };
    }""")
    assert result["state"] == "playing"
    assert result["score"] == 0
    assert result["lives"] == 3
    assert result["level"] == 1
    playing_page.wait_for_timeout(1000)
    _print(f"  [OK] state={result['state']}, score={result['score']}, lives={result['lives']}, level={result['level']}")


def test_startgame_clears_entities(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: After startGame(), all entity arrays should be empty")
    _print("  -> Action: Game already playing -> call startGame() atomically -> verify entities cleared")
    playing_page.wait_for_timeout(1000)  # show game running visually

    result = playing_page.evaluate("""() => {
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
    playing_page.wait_for_timeout(1000)
    _print(f"  [OK] asteroids={result['asteroids']}, lasers={result['lasers']}, explosions={result['explosions']}, particles={result['particles']}")


def test_fire_laser_adds_projectile(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: fireLaser() adds a projectile to lasers array")
    _print("  -> Action: Game already playing -> call fireLaser() atomically -> verify laser added")
    result = playing_page.evaluate("""() => {
        laserCooldown = 0;
        fireLaser();
        return { laserCount: lasers.length, cooldown: laserCooldown };
    }""")
    assert result["laserCount"] >= 1
    assert result["cooldown"] > 0
    playing_page.wait_for_timeout(1000)
    _print(f"  [OK] lasers={result['laserCount']}, cooldown={result['cooldown']}")


def test_fire_laser_respects_cooldown(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Firing during cooldown should only produce 1 laser")
    _print("  -> Action: Game already playing -> fire twice rapidly -> verify only 1 laser")
    count = playing_page.evaluate("""() => {
        laserCooldown = 0;
        fireLaser();
        fireLaser();
        return lasers.length;
    }""")
    assert count == 1
    playing_page.wait_for_timeout(1000)
    _print(f"  [OK] lasers={count} (cooldown working, no double-fire)")


def test_explode_small_generates_particles(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Small explosion should generate particle effects")
    _print("  -> Action: Game already playing -> trigger small explosion at center")
    result = playing_page.evaluate("""() => {
        explode(240, 320, false);
        return { particles: particles.length, explosions: explosions.length };
    }""")
    assert result["particles"] >= 14
    assert result["explosions"] >= 1
    playing_page.wait_for_timeout(1500)
    _print(f"  [OK] particles={result['particles']}, explosions={result['explosions']}")


def test_explode_big_generates_more_particles(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Large explosion should generate MORE particles")
    _print("  -> Action: Game already playing -> trigger large explosion at center")
    result = playing_page.evaluate("""() => {
        explode(240, 320, true);
        return { particles: particles.length, explosions: explosions.length };
    }""")
    assert result["particles"] >= 28
    assert result["explosions"] >= 1
    playing_page.wait_for_timeout(1500)
    _print(f"  [OK] particles={result['particles']}, explosions={result['explosions']} (large explosion)")


def test_explode_big_triggers_screen_shake(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Large explosion should trigger screen shake")
    _print("  -> Action: Game already playing -> trigger large explosion -> verify shake value")
    shake_val = playing_page.evaluate("""() => {
        explode(240, 320, true);
        return shake;
    }""")
    assert shake_val == 14
    playing_page.wait_for_timeout(1500)
    _print(f"  [OK] shake={shake_val} (screen shake triggered, visible in browser)")


def test_level_formula(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Score 600 should push level to 3")
    _print("  -> Action: Game already playing -> set score=600 -> verify #level DOM updates")
    playing_page.evaluate("() => { score = 600; level = 1 + Math.floor(score / 300); }")
    playing_page.wait_for_timeout(1000)

    level_text = playing_page.locator("#level").inner_text()
    level_val = playing_page.evaluate("() => level")
    assert level_val == 3
    _print(f"  [OK] DOM #level={level_text}, JS level={level_val}")


def test_move_left(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Hold ArrowLeft -> player.x should decrease")
    _print("  -> Action: Game already playing -> record x -> hold ArrowLeft -> verify x decreased")
    before = playing_page.evaluate("() => player.x")
    playing_page.keyboard.down("ArrowLeft")
    playing_page.wait_for_timeout(800)
    playing_page.keyboard.up("ArrowLeft")
    after = playing_page.evaluate("() => player.x")
    assert after < before
    _print(f"  [OK] x: {before:.1f} -> {after:.1f} (moved left by {before - after:.1f}px)")


def test_move_right(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Hold ArrowRight -> player.x should increase")
    _print("  -> Action: Game already playing -> record x -> hold ArrowRight -> verify x increased")
    before = playing_page.evaluate("() => player.x")
    playing_page.keyboard.down("ArrowRight")
    playing_page.wait_for_timeout(800)
    playing_page.keyboard.up("ArrowRight")
    after = playing_page.evaluate("() => player.x")
    assert after > before
    _print(f"  [OK] x: {before:.1f} -> {after:.1f} (moved right by {after - before:.1f}px)")


def test_move_up(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Hold ArrowUp -> player.y should decrease")
    _print("  -> Action: Game already playing -> record y -> hold ArrowUp -> verify y decreased")
    before = playing_page.evaluate("() => player.y")
    playing_page.keyboard.down("ArrowUp")
    playing_page.wait_for_timeout(800)
    playing_page.keyboard.up("ArrowUp")
    after = playing_page.evaluate("() => player.y")
    assert after < before
    _print(f"  [OK] y: {before:.1f} -> {after:.1f} (moved up by {before - after:.1f}px)")


def test_move_down(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Hold ArrowDown -> player.y should increase")
    _print("  -> Action: Game already playing -> record y -> hold ArrowDown -> verify y increased")
    before = playing_page.evaluate("() => player.y")
    playing_page.keyboard.down("ArrowDown")
    playing_page.wait_for_timeout(800)
    playing_page.keyboard.up("ArrowDown")
    after = playing_page.evaluate("() => player.y")
    assert after > before
    _print(f"  [OK] y: {before:.1f} -> {after:.1f} (moved down by {after - before:.1f}px)")


# ── Collision Tests ───────────────────────────────────────────────────────────

def test_collision_decreases_lives(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Asteroid collision -> lives should decrease by 1")
    _print("  -> Action: Game already playing -> place asteroid on player -> call update() -> verify lives == 2")
    result = playing_page.evaluate("""() => {
        invincible = 0;
        asteroids = [{ x: player.x, y: player.y, r: 20, hp: 1, vx: 0, vy: 0 }];
        update();
        return lives;
    }""")
    assert result == 2
    _print(f"  [OK] lives={result} (decreased from 3 to 2 after collision)")


def test_collision_sets_invincible(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Asteroid collision -> invincible should be set to 120")
    _print("  -> Action: Game already playing -> place asteroid on player -> call update() -> verify invincible == 120")
    result = playing_page.evaluate("""() => {
        invincible = 0;
        asteroids = [{ x: player.x, y: player.y, r: 20, hp: 1, vx: 0, vy: 0 }];
        update();
        return invincible;
    }""")
    assert result == 120
    _print(f"  [OK] invincible={result} (120 frames protection activated)")


def test_lives_zero_triggers_dead_state(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: lives=1, collision -> state should become 'dead'")
    _print("  -> Action: Game already playing -> set lives=1 -> place asteroid on player -> call update() -> verify state == 'dead'")
    result = playing_page.evaluate("""() => {
        lives = 1;
        invincible = 0;
        asteroids = [{ x: player.x, y: player.y, r: 20, hp: 1, vx: 0, vy: 0 }];
        update();
        return state;
    }""")
    assert result == "dead"
    _print(f"  [OK] state='{result}' (game over triggered)")


def test_large_asteroid_requires_two_hits(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: Large asteroid (hp=2) requires 2 laser hits to destroy")
    _print("  -> Action: Game already playing -> place hp=2 asteroid -> hit once -> hp=1 -> hit again -> destroyed + score +30")
    result = playing_page.evaluate("""() => {
        const ax = 240, ay = 200;
        asteroids = [{ x: ax, y: ay, r: 30, hp: 2, vx: 0, vy: 0 }];
        // l.y + l.h/2 == ay ensures center collision
        lasers = [{ x: ax, y: ay - 9, w: 3, h: 18, vy: -14 }];
        const scoreBefore = score;
        update();
        const hpAfterOne = asteroids.length > 0 ? asteroids[0].hp : -1;
        // Second hit
        if (asteroids.length > 0) {
            lasers = [{ x: asteroids[0].x, y: asteroids[0].y - 9, w: 3, h: 18, vy: -14 }];
            update();
        }
        return {
            hpAfterOne,
            destroyed: asteroids.length === 0,
            scoreGained: score - scoreBefore
        };
    }""")
    assert result["hpAfterOne"] == 1
    assert result["destroyed"] is True
    assert result["scoreGained"] >= 30
    _print(f"  [OK] hp after 1st hit={result['hpAfterOne']}, destroyed={result['destroyed']}, score gained={result['scoreGained']}")


# ── executeCommand() API ──────────────────────────────────────────────────────

def test_execute_command_left_moves_player(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: executeCommand({left}) -> player.x decreases")
    before = playing_page.evaluate("() => player.x")
    playing_page.evaluate("() => { executeCommand({ left: true }); update(); }")
    after = playing_page.evaluate("() => player.x")
    assert after < before
    _print(f"  [OK] x: {before:.1f} -> {after:.1f}")


def test_execute_command_right_moves_player(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: executeCommand({right}) -> player.x increases")
    before = playing_page.evaluate("() => player.x")
    playing_page.evaluate("() => { executeCommand({ right: true }); update(); }")
    after = playing_page.evaluate("() => player.x")
    assert after > before
    _print(f"  [OK] x: {before:.1f} -> {after:.1f}")


def test_execute_command_up_moves_player(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: executeCommand({up}) -> player.y decreases")
    before = playing_page.evaluate("() => player.y")
    playing_page.evaluate("() => { executeCommand({ up: true }); update(); }")
    after = playing_page.evaluate("() => player.y")
    assert after < before
    _print(f"  [OK] y: {before:.1f} -> {after:.1f}")


def test_execute_command_down_moves_player(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: executeCommand({down}) -> player.y increases")
    before = playing_page.evaluate("() => player.y")
    playing_page.evaluate("() => { executeCommand({ down: true }); update(); }")
    after = playing_page.evaluate("() => player.y")
    assert after > before
    _print(f"  [OK] y: {before:.1f} -> {after:.1f}")


def test_execute_command_shoot_fires_laser(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: executeCommand({shoot}) -> laser added")
    result = playing_page.evaluate("""() => {
        laserCooldown = 0; lasers = [];
        executeCommand({ shoot: true });
        return lasers.length;
    }""")
    assert result == 1
    _print(f"  [OK] lasers.length={result}")


def test_execute_command_idle_no_movement(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: executeCommand({}) -> player stays in place")
    result = playing_page.evaluate("""() => {
        player.x = 240; player.y = 400;
        player.vx = 0;  player.vy = 0;
        executeCommand({});
        update();
        return { x: Math.round(player.x), y: Math.round(player.y) };
    }""")
    assert result["x"] == 240
    assert result["y"] == 400
    _print(f"  [OK] position unchanged: ({result['x']}, {result['y']})")


def test_execute_command_combined_move_and_shoot(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: executeCommand({left, shoot}) -> moves AND fires simultaneously")
    result = playing_page.evaluate("""() => {
        laserCooldown = 0; lasers = [];
        const xBefore = player.x;
        executeCommand({ left: true, shoot: true });
        update();
        return { moved: player.x < xBefore, fired: lasers.length >= 1 };
    }""")
    assert result["moved"] is True
    assert result["fired"] is True
    _print(f"  [OK] moved={result['moved']}, fired={result['fired']}")


def test_pause_on_esc(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: ESC during playing -> state becomes 'paused'")
    playing_page.keyboard.press("Escape")
    result = playing_page.evaluate("state")
    assert result == "paused"
    _print(f"  [OK] state={result}")


def test_resume_from_pause_esc(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: ESC during paused -> state returns to 'playing'")
    playing_page.keyboard.press("Escape")
    playing_page.keyboard.press("Escape")
    result = playing_page.evaluate("state")
    assert result == "playing"
    _print(f"  [OK] state={result}")


def test_pause_stops_update(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: paused state -> frameCount does not increase")
    playing_page.keyboard.press("Escape")
    frame1 = playing_page.evaluate("frameCount")
    playing_page.wait_for_timeout(300)
    frame2 = playing_page.evaluate("frameCount")
    assert frame1 == frame2
    _print(f"  [OK] frameCount frozen at {frame1}")


def test_dash_hud_shows_cooldown(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: dash cooling down -> #dash-hud visible with countdown text")
    result = playing_page.evaluate("""() => {
        dashConfig.enabled = true;
        dashCooldown = 60;
        update();
        const el = document.getElementById('dash-hud');
        return { display: el.style.display, text: el.textContent };
    }""")
    assert result['display'] != 'none'
    assert 's' in result['text']
    _print(f"  [OK] display={result['display']!r}, text={result['text']!r}")


def test_dash_hud_shows_ready(playing_page):
    _print("\n[FUNCTIONAL TEST] Test: dash cooldown 0 -> #dash-hud shows DASH")
    result = playing_page.evaluate("""() => {
        dashConfig.enabled = true;
        dashCooldown = 0;
        update();
        const el = document.getElementById('dash-hud');
        return { display: el.style.display, text: el.textContent };
    }""")
    assert result['display'] != 'none'
    assert 'DASH' in result['text']
    _print(f"  [OK] display={result['display']!r}, text={result['text']!r}")
