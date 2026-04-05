import pytest
import threading
import http.server
import os


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # CI=true (GitHub Actions) → headless；本機開發 → headed（保留視窗）
    headless = os.environ.get("CI", "false").lower() == "true"
    return {**browser_type_launch_args, "headless": headless}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8765


@pytest.fixture(scope="session", autouse=True)
def local_server():
    """啟動本機靜態伺服器以供 Playwright 存取 HTML 檔案"""
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("localhost", PORT), handler)
    os.chdir(BASE_DIR)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    yield
    httpd.shutdown()


@pytest.fixture
def game_page(page):
    """黑箱測試用：開啟遊戲頁面，停在 start 畫面（state='start'）"""
    page.goto(f"http://localhost:{PORT}/space_dodge.html")
    page.wait_for_selector("#canvas")
    return page


@pytest.fixture
def playing_page(game_page):
    """白箱測試用：直接以 JS 啟動遊戲，跳過選單 UI（state='playing'）"""
    game_page.evaluate("() => startGame('player')")
    return game_page
