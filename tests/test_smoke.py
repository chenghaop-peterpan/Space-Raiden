# -*- coding: utf-8 -*-
"""
Smoke Tests - Space-Raiden
驗證頁面載入後的 DOM 初始狀態與基本互動，確認遊戲可正常開啟與啟動。
涵蓋：初始 DOM、模式選單導航、AI 面板互動、遊戲啟動流程

執行方式: pytest tests/test_smoke.py -v -s
"""
import pytest

pytestmark = pytest.mark.smoke


# ── 頁面初始狀態 ───────────────────────────────────────────────────────────────

def test_canvas_dimensions(game_page):
    width = game_page.evaluate("() => document.getElementById('canvas').width")
    height = game_page.evaluate("() => document.getElementById('canvas').height")
    assert width == 480
    assert height == 640


def test_canvas_is_visible(game_page):
    assert game_page.locator("#canvas").is_visible()


def test_initial_score_is_zero(game_page):
    assert game_page.locator("#score").inner_text() == "0"


def test_initial_lives_display(game_page):
    lives_text = game_page.locator("#lives").inner_text()
    assert lives_text == "❤️❤️❤️"


def test_initial_level_is_one(game_page):
    assert game_page.locator("#level").inner_text() == "1"


def test_hint_text_visible(game_page):
    hint = game_page.locator("#hint")
    assert hint.is_visible()
    text = hint.inner_text()
    assert "Space" in text


def test_ui_bar_visible(game_page):
    assert game_page.locator("#ui").is_visible()


def test_ai_panel_initially_hidden(game_page):
    assert not game_page.locator("#ai-panel").is_visible()


# ── 模式選單（start → menu）────────────────────────────────────────────────────

def test_space_opens_menu(game_page):
    game_page.keyboard.press("Space")
    state = game_page.evaluate("() => state")
    assert state == "menu"


def test_enter_opens_menu(game_page):
    game_page.keyboard.press("Enter")
    state = game_page.evaluate("() => state")
    assert state == "menu"


def test_menu_default_highlights_player_mode(game_page):
    game_page.keyboard.press("Space")
    index = game_page.evaluate("() => menuIndex")
    assert index == 0


def test_menu_arrowdown_selects_ai_mode(game_page):
    game_page.keyboard.press("Space")         # → menu
    game_page.keyboard.press("ArrowDown")     # index 0 → 1
    index = game_page.evaluate("() => menuIndex")
    assert index == 1


def test_menu_arrowup_toggles_back(game_page):
    game_page.keyboard.press("Space")         # → menu
    game_page.keyboard.press("ArrowDown")     # → index 1
    game_page.keyboard.press("ArrowUp")       # → index 0
    index = game_page.evaluate("() => menuIndex")
    assert index == 0


def test_menu_confirm_player_mode_starts_game(game_page):
    game_page.keyboard.press("Space")         # → menu (index=0, player)
    game_page.keyboard.press("Space")         # → startGame('player')
    state = game_page.evaluate("() => state")
    assert state == "playing"


def test_menu_confirm_ai_mode_shows_panel(game_page):
    game_page.keyboard.press("Space")         # → menu
    game_page.keyboard.press("ArrowDown")     # → index 1 (AI)
    game_page.keyboard.press("Space")         # → ai_params
    state = game_page.evaluate("() => state")
    assert state == "ai_params"
    assert game_page.locator("#ai-panel").is_visible()


def test_gameover_space_returns_to_menu(game_page):
    game_page.evaluate("() => { state = 'gameover'; }")
    game_page.keyboard.press("Space")
    state = game_page.evaluate("() => state")
    assert state == "menu"


# ── AI 面板互動（ai_params）────────────────────────────────────────────────────

def test_ai_panel_back_button_returns_to_menu(game_page):
    game_page.keyboard.press("Space")         # → menu
    game_page.keyboard.press("ArrowDown")     # → AI mode
    game_page.keyboard.press("Space")         # → ai_params, panel shown
    game_page.locator("#btn-back").click()
    state = game_page.evaluate("() => state")
    assert state == "menu"
    assert not game_page.locator("#ai-panel").is_visible()


def test_ai_panel_esc_returns_to_menu(game_page):
    game_page.keyboard.press("Space")         # → menu
    game_page.keyboard.press("ArrowDown")     # → AI mode
    game_page.keyboard.press("Space")         # → ai_params
    game_page.keyboard.press("Escape")
    state = game_page.evaluate("() => state")
    assert state == "menu"
    assert not game_page.locator("#ai-panel").is_visible()


def test_ai_panel_start_button_begins_ai_game(game_page):
    game_page.keyboard.press("Space")         # → menu
    game_page.keyboard.press("ArrowDown")     # → AI mode
    game_page.keyboard.press("Space")         # → ai_params
    game_page.locator("#btn-start").click()
    state = game_page.evaluate("() => state")
    game_mode = game_page.evaluate("() => gameMode")
    assert state == "playing"
    assert game_mode == "ai"
    assert not game_page.locator("#ai-panel").is_visible()


# ── 遊戲啟動流程 ────────────────────────────────────────────────────────────────

def test_press_space_starts_game(game_page):
    game_page.keyboard.press("Space")         # start -> menu
    game_page.keyboard.press("Space")         # menu -> playing (player mode)
    state = game_page.evaluate("() => state")
    assert state == "playing"


def test_press_enter_starts_game(game_page):
    game_page.keyboard.press("Enter")         # start -> menu
    game_page.keyboard.press("Enter")         # menu -> playing (player mode)
    state = game_page.evaluate("() => state")
    assert state == "playing"


def test_score_increases_over_time(game_page):
    game_page.keyboard.press("Space")         # start -> menu
    game_page.keyboard.press("Space")         # menu -> playing
    game_page.wait_for_timeout(2000)
    score = int(game_page.locator("#score").inner_text())
    assert score > 0
