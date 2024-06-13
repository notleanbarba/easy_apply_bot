from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from langdetect import detect
from selenium.webdriver.remote.webelement import WebElement
import tomllib
import re
import time
from typing import Iterator


def IteratePages(resume):
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
    try:
        time.sleep(1)
        if apply_modal.find_element(
            By.CSS_SELECTOR,
            "[aria-label='Upload resume button. Only, DOC, DOCX, PDF formats are supported. Max file size is (2 MB).']",
        ):
            saved_resumes = apply_modal.find_element(By.CLASS_NAME, "jobs-easy-apply-content")
            for saved in saved_resumes.find_elements(By.CLASS_NAME, "ui-attachment--pdf"):
                if re.search("resume %s" % resume, saved.text):
                    saved.click()
                    time.sleep(1)
                    break
    except NoSuchElementException:
        pass

    ### Check for unanswer
    try:
        for question in apply_modal.find_elements(By.CLASS_NAME, "artdeco-text-input--container"):
            if question.find_element(By.TAG_NAME, "input").get_attribute("value") == "":
                print("\033[sQuestion: " + question.find_element(By.TAG_NAME, "label").text)
                ans = input("Answer: ")
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
                input("Press to continue execution...")
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
                input("Press to continue execution...")
                print("\033[2F\033[J\033[F")
                apply_modal.find_element(By.CSS_SELECTOR, "[aria-label='Review your application']").click()
        finally:
            IteratePages(resume)


def ApplyToJob(offers: Iterator[WebElement]):
    try:
        offer = offers.__next__()

        offer.click()

        time.sleep(2)

        offer_lang = detect(
            browser.find_element(By.CLASS_NAME, "jobs-description-content__text").find_element(By.TAG_NAME, "div").text
        )
        offer_resume = config["resumes"][offer_lang]

        title = browser.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title").text
        company = browser.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name").text
        location = (
            browser.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__primary-description-container")
            .find_elements(By.TAG_NAME, "span")[0]
            .text
        )

        browser.find_element(By.CLASS_NAME, "jobs-apply-button").click()

        IteratePages(offer_resume)

        print(
            "Applied to %s at %s. Job Location: %s. Language: %s. Resume used: %s"
            % (title, company, location, offer_lang, offer_resume),
        )
        ApplyToJob(offers)
    except StopIteration:
        return


if __name__ == "__main__":
    try:
        with open("config.toml", "rb") as file:
            config = tomllib.load(file)

        ### Open Google chrome instance
        ###
        options = Options()
        options.add_argument("user-data-dir=/tmp/easy_apply_bot")

        browser = webdriver.Chrome(options=options)
        ###
        ###

        ### Go to Job Offers page
        ###
        if config["use_top_applicant"]:
            URL = "https://www.linkedin.com/jobs/collections/recommended/?discover=recommended&discoveryOrigin=JOBS_HOME_JYMBII"

        browser.get(URL)

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

        BASE_URL = "https://www.linkedin.com/jobs/collections/recommended/"
        assert browser.current_url.find(BASE_URL) != -1
        ###
        ###

        while True:
            ### Scan page for Easy Apply offers
            ###
            offers_list_height = 0
            browser.execute_script(
                "document.getElementsByClassName('jobs-search-results-list').item(0).scrollTop = 10000"
            )

            offers_li = browser.find_element(By.CLASS_NAME, "scaffold-layout__list-container").find_elements(
                By.XPATH, "./*"
            )

            offers_w_EA = filter(
                lambda offer: re.search("Easy Apply", offer.text),
                offers_li,
            )

            ApplyToJob(offers_w_EA)

            pages = browser.find_elements(By.CLASS_NAME, "artdeco-pagination__indicator")
            for i, page in enumerate(pages):
                if "active" in page.get_property("classList"):
                    pages[i + 1].click()
                    time.sleep(5)
                    break

    except BaseException:
        import sys

        print(sys.exc_info()[0])
        import traceback

        print(traceback.format_exc())
    finally:
        print("Press Enter to continue ...")
        input()
