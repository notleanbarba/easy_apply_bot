import tomllib
import linkedin
import bumeran
import zonajobs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if __name__ == "__main__":
    ### Open Google chrome instance
    ###
    options = Options()
    options.add_argument("user-data-dir=/tmp/easy_apply_bot")

    browser = webdriver.Chrome(options=options)

    with open("config.toml", "rb") as file:
        activate = tomllib.load(file)["activate"]

    counter_linkedin = 0
    counter_bumeran = 0
    counter_zonajobs = 0

    if activate["linkedin"]:
        counter_linkedin = linkedin.main(browser)
    if activate["bumeran"]:
        counter_bumeran = bumeran.main(browser)
    if activate["zonajobs"]:
        counter_zonajobs = zonajobs.main(browser)
    print(
        "No more jobs to apply. Jobs applied=%d: LinkedIn=%d, Bumeran=%d, Zonajobs=%d"
        % (counter_linkedin + counter_bumeran + counter_zonajobs, counter_linkedin, counter_bumeran, counter_zonajobs)
    )
    input("Press any key to close")
    browser.quit()
