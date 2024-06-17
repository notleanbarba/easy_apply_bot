import tomllib
import time
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def main(browser: WebDriver):
    with open("config.toml", "rb") as file:
        config = tomllib.load(file)["bumeran"]

    wait = WebDriverWait(browser, 15)

    ### Go to Job Offers page
    ###

    browser.get("https://www.bumeran.com.ar")

    print(
        "\
=================================================\n\
Applying to jobs in Bumeran\n\
\t - Search query: %s\n\
\t - City to apply: %s\n\
\t - Intended Salary: %d\n\
================================================="
        % (config["jobs_to_apply"], config["city"], config["intended_salary"])
    )

    try:
        browser.find_element(value="ingresarNavBar").click()
        browser.find_element(value="email").send_keys(config["user"])
        browser.find_element(value="password").send_keys(config["password"], Keys.RETURN)
    except NoSuchElementException:
        pass

    browser.find_element(value="react-select-2-input").send_keys(config["jobs_to_apply"][0])
    browser.find_element(value="lugar-de-trabajo").click()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "select__option")))
    for option in browser.find_elements(By.CLASS_NAME, "select__option"):
        if option.text == config["city"]:
            option.click()
            break

    time.sleep(3)

    counter = 0
    for i in range(1, len(config["jobs_to_apply"])):
        while True:
            offers_list = browser.find_element(value="listado-avisos")
            offers = offers_list.find_elements(By.CLASS_NAME, "sc-dDDicx")
            original_tab = browser.current_window_handle
            for offer in offers:
                # Skip job already applied
                try:
                    offer.find_element(By.CSS_SELECTOR, "[name='icon-light-checkbox-checked']")
                    continue
                except NoSuchElementException:
                    pass

                # Break on jobs from ZonaJobs
                try:
                    offer.find_element(By.CSS_SELECTOR, "[alt='logo Zonajobs']")
                    break
                except NoSuchElementException:
                    pass

                offer.click()
                wait.until(EC.number_of_windows_to_be(2))
                for tab in browser.window_handles:
                    if tab != original_tab:
                        browser.switch_to.window(tab)
                        break
                wait.until(EC.title_contains("| Bumeran"))
                try:
                    wait.until(EC.presence_of_element_located((By.ID, "salarioPretendido")))
                except TimeoutException:
                    browser.close()
                    browser.switch_to.window(original_tab)
                    continue
                if browser.find_element(value="salarioPretendido").text == "":
                    salary_box = browser.find_element(value="salarioPretendido")
                    salary_box.send_keys(Keys.CONTROL, "a")
                    salary_box.send_keys(str(config["intended_salary"]))
                browser.find_element(By.CSS_SELECTOR, "[content='Postularme']").click()

                title = browser.find_element(value="header-component").find_element(By.TAG_NAME, "h1").text
                company = "confidencial"
                try:
                    company = browser.find_element(value="header-component").find_element(By.TAG_NAME, "a").text
                except NoSuchElementException:
                    pass

                location = (
                    browser.find_element(value="ficha-detalle")
                    .find_elements(By.CLASS_NAME, "sc-EHOje")[0]
                    .find_element(By.TAG_NAME, "a")
                    .text
                )

                counter += 1
                print(
                    "Bumeran offer: Applied to %s at %s. Job Location: %s" % (title, company, location),
                )
                browser.close()
                browser.switch_to.window(original_tab)

            next_page = offers_list.find_element(By.CLASS_NAME, "sc-cBXKeB")
            if next_page.get_attribute("disabled") == "true":
                break
            else:
                next_page.click()
                wait.until(EC.title_contains("Empleos en"))
                time.sleep(3)

        search_bar = browser.find_element(value="busqueda")
        search_bar.find_element(By.CLASS_NAME, "select__indicators").click()
        browser.find_element(By.CLASS_NAME, "select__value-container").find_element(By.TAG_NAME, "input").send_keys(
            config["jobs_to_apply"][i], Keys.RETURN
        )
        wait.until(EC.title_contains("| Bumeran"))
        wait.until(EC.presence_of_element_located((By.ID, "listado-avisos")))
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sc-cBXKeB")))
    return counter
