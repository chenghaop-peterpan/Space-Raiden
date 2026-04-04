import pytest
import threading
import http.server
import os

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
    """開啟遊戲頁面並等待畫布載入"""
    page.goto(f"http://localhost:{PORT}/space_dodge.html")
    page.wait_for_selector("#canvas")
    return page
