import linkedin
import bumeran
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if __name__ == "__main__":
    ### Open Google chrome instance
    ###
    options = Options()
    options.add_argument("user-data-dir=/tmp/easy_apply_bot")

    browser = webdriver.Chrome(options=options)

    counter_linkedin = linkedin.main(browser)
    counter_bumeran = bumeran.main(browser)
    print(
        "No more jobs to apply. Jobs applied=%d: LinkedIn=%d, Bumeran=%d"
        % (counter_linkedin + counter_bumeran, counter_linkedin, counter_bumeran)
    )
    input("Press any key to close")
    browser.quit()
