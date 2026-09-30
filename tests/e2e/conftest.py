"""Selenium contra una aplicación real y el fixture MySQL de pruebas."""
import os
import threading
from pathlib import Path

import pytest
import pytest_html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from werkzeug.serving import make_server


@pytest.fixture
def live_server(app):
    server = make_server("127.0.0.1", 0, app, threaded=True)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    worker.join(timeout=5)
    server.server_close()


@pytest.fixture
def browser(request):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--disable-dev-shm-usage")
    if os.getenv("CHROME_NO_SANDBOX") == "1":
        options.add_argument("--no-sandbox")
    if os.getenv("CHROME_BINARY"):
        options.binary_location = os.environ["CHROME_BINARY"]
    service = Service(executable_path=os.environ["CHROMEDRIVER"]) if os.getenv("CHROMEDRIVER") else Service()
    driver = webdriver.Chrome(options=options, service=service)
    driver.set_page_load_timeout(30)
    request.node.user_properties.append(("navegador", driver.capabilities.get("browserVersion", "desconocido")))
    yield driver
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or "browser" not in item.funcargs:
        return
    driver = item.funcargs["browser"]
    directory = Path("artifacts/capturas")
    directory.mkdir(parents=True, exist_ok=True)
    try:
        # Las cuentas son ficticias; no guardar el valor de campos contraseña.
        driver.execute_script("document.querySelectorAll('input[type=password]').forEach(e => e.value = '')")
        png = driver.get_screenshot_as_base64()
        driver.save_screenshot(str(directory / f"{item.name}.png"))
        extras = getattr(report, "extras", [])
        extras.append(pytest_html.extras.png(png, name="Evidencia Selenium"))
        report.extras = extras
    except Exception:
        # Conservar el resultado original si el navegador ya no responde.
        pass
