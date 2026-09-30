"""Interfaz real sin simulación de fetch ni inyección de tokens en el navegador."""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from test_flujos import catalog

pytestmark = pytest.mark.e2e


def click(driver, selector):
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))).click()


def login(driver, url):
    driver.get(url)
    click(driver, "#account [data-go='Ingresar']")
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "authForm")))
    driver.find_element(By.ID, "f_identificador").send_keys("cuenta2@example.com")
    driver.find_element(By.ID, "f_password").send_keys("PasswordTest2026!")
    click(driver, "#authForm button")
    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "logout")))


@pytest.mark.caso("CP-19")
def test_cp19_sesion_navegador(browser, live_server):
    login(browser, live_server)
    browser.refresh()
    WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.ID, "logout")))
    click(browser, "#logout")
    WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#account [data-go='Ingresar']")))
    assert not browser.find_elements(By.CSS_SELECTOR, "#nav [data-view='Mis citas']")


@pytest.mark.caso("CP-20")
def test_cp20_reservar_reprogramar_cancelar(browser, live_server, client, headers):
    service, date, _ = catalog(client, headers)
    login(browser, live_server)
    click(browser, f"[data-reserve='{service}']")
    WebDriverWait(browser, 15).until(EC.visibility_of_element_located((By.ID, "search")))
    Select(browser.find_element(By.ID, "f_personal_id")).select_by_value("3")
    # Un input date recibe ISO de forma consistente mediante el control DOM;
    # la consulta y el guardado se disparan con los botones reales.
    browser.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('change', {bubbles:true}))", browser.find_element(By.ID, "f_fecha"), date)
    click(browser, "#search button")
    click(browser, "[data-hour='09:00']")
    wait = WebDriverWait(browser, 15)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".appointment-card")))
    assert "09:00" in browser.find_element(By.CSS_SELECTOR, ".appointment-card").text
    browser.refresh()
    wait.until(EC.visibility_of_element_located((By.ID, "logout")))
    click(browser, "#nav [data-view='Mis citas']")
    click(browser, "[data-change]")
    # El radio está oculto por CSS; interactuar con la opción visible de su label.
    click(browser, "#rescheduleSlots input[value='11:00'] + span")
    click(browser, "#modalForm button[type='submit']")
    wait.until(lambda d: not d.find_element(By.ID, "modal").is_displayed())
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".appointment-card"), "11:00"))
    click(browser, "[data-cancel]")
    wait.until(EC.alert_is_present()).accept()
    wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".appointment-card"), "Cancelada"))
