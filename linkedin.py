from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from langdetect import detect
from selenium.webdriver.remote.webelement import WebElement
import tomllib
import re
import time
from typing import Iterator
from selenium.webdriver.chrome.webdriver import WebDriver

counter = 0


def IteratePages(resume, browser: WebDriver, cv_applied=False):
    ## Bypass job safety
    try:
        if browser.find_element(By.CLASS_NAME, "artdeco-modal__header").text == "Job search safety reminder":
            browser.find_element(By.CLASS_NAME, "jobs-apply-button").click()
    except NoSuchElementException:
        pass

    apply_modal = browser.find_element(By.CLASS_NAME, "jobs-easy-apply-modal")
    try:
        current_progress = apply_modal.find_element(
            By.CLASS_NAME, "artdeco-completeness-meter-linear__progress-element"
        ).get_property("value")
    except NoSuchElementException:
        pass

    ### Check if resumes is asked
    if not cv_applied:
        try:
            if apply_modal.find_element(
                By.CSS_SELECTOR,
                "[aria-label='Upload resume button. Only, DOC, DOCX, PDF formats are supported. Max file size is (2 MB).']",
            ):
                for saved in apply_modal.find_elements(By.CLASS_NAME, "ui-attachment--pdf"):
                    if re.search("Select resume %s" % resume, saved.text) is not None:
                        saved.click()
                        cv_applied = True
                        break
        except NoSuchElementException:
            pass

    ### Check for unanswer
    try:
        for question in apply_modal.find_elements(By.CLASS_NAME, "artdeco-text-input--container"):
            if question.find_element(By.TAG_NAME, "input").get_attribute("value") == "":
                print("\033[sQuestion: " + question.find_element(By.TAG_NAME, "label").text)
                ans = input("\aAnswer: ")
                print("\033[2F\033[J\033[F")
                question.find_element(By.TAG_NAME, "input").send_keys(ans)
    except NoSuchElementException:
        pass

    try:
        apply_modal.find_element(By.CSS_SELECTOR, "[aria-label='Submit application']").click()
        time.sleep(3)
        browser.find_element(By.CSS_SELECTOR, "[aria-label='Dismiss']").click()
        return
    except NoSuchElementException:
        try:
            apply_modal.find_element(By.CSS_SELECTOR, "[aria-label='Continue to next step']").click()
            while (
                browser.find_element(By.CLASS_NAME, "artdeco-completeness-meter-linear__progress-element").get_property(
                    "value"
                )
                == current_progress
            ):
                print("Required field to complete. Follow instructions in browser")
                input("\aPress to continue execution...")
                print("\033[2F\033[J\033[F")
                apply_modal.find_element(By.CSS_SELECTOR, "[aria-label='Continue to next step']").click()
        except NoSuchElementException:
            apply_modal.find_element(By.CSS_SELECTOR, "[aria-label='Review your application']").click()
            while (
                browser.find_element(By.CLASS_NAME, "artdeco-completeness-meter-linear__progress-element").get_property(
                    "value"
                )
                == current_progress
            ):
                print("Required field to complete. Follow instructions in browser")
                input("\aPress to continue execution...")
                print("\033[2F\033[J\033[F")
                apply_modal.find_element(By.CSS_SELECTOR, "[aria-label='Review your application']").click()
        finally:
            IteratePages(resume, browser, cv_applied=cv_applied)


def ApplyToJob(offers: Iterator[WebElement], browser: WebDriver, resumes, blacklist):
    try:
        offer = offers.__next__()

        offer.click()

        time.sleep(2)

        offer_lang = detect(
            browser.find_element(By.CLASS_NAME, "jobs-description-content__text").find_element(By.TAG_NAME, "div").text
        )
        offer_resume = resumes[offer_lang]

        title = browser.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title").text
        company = browser.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name").text
        if company in blacklist:
            return
        location = (
            browser.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__primary-description-container")
            .find_elements(By.TAG_NAME, "span")[0]
            .text
        )

        browser.find_element(By.CLASS_NAME, "jobs-apply-button").click()

        IteratePages(offer_resume, browser)

        global counter
        counter += 1
        print(
            "Applied to %s at %s. Job Location: %s. Language: %s. Resume used: %s"
            % (title, company, location, offer_lang, offer_resume),
        )
        ApplyToJob(offers, browser, resumes, blacklist)
    except StopIteration:
        return


def main(browser: WebDriver):
    with open("config.toml", "rb") as file:
        config = tomllib.load(file)["linkedin"]

    ### Go to Job Offers page
    ###
    BASE_URL = "https://www.linkedin.com/jobs/search"

    browser.get("https://www.linkedin.com/jobs")

    print(
        "\
=================================================\n\
Applying to jobs in LinkedIn\n\
\t - Search query: %s\n\
\t - Use Top applicant: %s\n\
\t - Blacklist: %s\n\
================================================="
        % (config["jobs_to_apply"], config["use_top_applicant"], config["blacklist"])
    )

    if re.search("Login", browser.title):
        user_box = browser.find_element(value="username")
        pass_box = browser.find_element(value="password")

        user_box.send_keys(config["user"])
        pass_box.send_keys(config["password"], Keys.RETURN)

        if browser.title == "Security Verification | LinkedIn":
            print("Captcha wall. Please, follow the instructions to continue.")
            while browser.title == "Security Verification | LinkedIn":
                time.sleep(5)

        if browser.title == "LinkedIn App Challenge":
            print("2FA wall. Please, follow the instructions to continue.")
            while browser.title == "LinkedIn App Challenge":
                time.sleep(5)

    if config["use_top_applicant"]:
        BASE_URL = "https://www.linkedin.com/jobs/collections/recommended/"
        top_offers = browser.find_element(By.CSS_SELECTOR, "[data-view-name='jobs-feed-discovery-module']")
        if re.search("Top job picks for you", top_offers.text):
            top_offers.find_element(By.CLASS_NAME, "discovery-templates-jobs-home-vertical-list__footer").click()
            time.sleep(1)

    time.sleep(3)
    assert browser.current_url.find(BASE_URL) != -1
    ###
    ###
    global counter
    pages_available = True
    while pages_available:
        ### Scan page for Easy Apply offers
        ###
        browser.execute_script("document.getElementsByClassName('jobs-search-results-list').item(0).scrollTop = 10000")

        offers_li = browser.find_element(By.CLASS_NAME, "scaffold-layout__list-container").find_elements(
            By.XPATH, "./*"
        )

        offers_w_EA = filter(
            lambda offer: re.search("Easy Apply", offer.text),
            offers_li,
        )

        ApplyToJob(offers_w_EA, browser, config["resumes"], config["blacklist"])

        pages = browser.find_elements(By.CLASS_NAME, "artdeco-pagination__indicator")
        for i, page in enumerate(pages):
            if "active" in page.get_property("classList"):
                pages[i + 1].click()
                time.sleep(3)
                pages_available = False
                break

    global counter
    return counter
