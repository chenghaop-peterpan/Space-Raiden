# -*- coding: utf-8 -*-
"""
Smoke Tests - Space-Raiden
驗證頁面載入後的 DOM 初始狀態與基本互動，確認遊戲可正常開啟與啟動。

執行方式: pytest tests/test_smoke.py -v -s
"""
import pytest

pytestmark = pytest.mark.smoke


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


def test_press_space_starts_game(game_page):
    game_page.keyboard.press("Space")
    state = game_page.evaluate("() => state")
    assert state == "playing"


def test_press_enter_starts_game(game_page):
    game_page.keyboard.press("Enter")
    state = game_page.evaluate("() => state")
    assert state == "playing"


def test_score_increases_over_time(game_page):
    game_page.keyboard.press("Space")
    game_page.wait_for_timeout(2000)
    score = int(game_page.locator("#score").inner_text())
    assert score > 0


def test_hint_text_visible(game_page):
    hint = game_page.locator("#hint")
    assert hint.is_visible()
    text = hint.inner_text()
    assert "Space" in text


def test_ui_bar_visible(game_page):
    assert game_page.locator("#ui").is_visible()
