from settings import chrome_driver, phantomjs_driver, geckodriver_driver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import requests


def new_driver(engine, save_file_dir):
    try:
        if engine == 'Chrome':
            options = ChromeOptions()
            options.add_experimental_option("prefs", {
                "download.default_directory": save_file_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            })
            options.add_argument("--headless")
            driver = webdriver.Chrome(chrome_driver, chrome_options=options)
        elif engine == 'FireFox':
            profile = webdriver.FirefoxProfile()
            profile.set_preference('browser.download.folderList', 2)  # custom location
            profile.set_preference('browser.download.manager.showWhenStarting', False)
            profile.set_preference('browser.download.dir', save_file_dir)
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
            profile.set_preference('security.tls.version.min', 1)
            options = FirefoxOptions()
            driver = webdriver.Firefox(profile, options=options, executable_path=geckodriver_driver)
        else:
            driver = webdriver.PhantomJS(phantomjs_driver)
    except:
        driver = webdriver.PhantomJS(phantomjs_driver)
    return driver


def close_driver(driver):
    driver.close()


def switch_by_id(driver, id_):
    element = driver.find_element_by_id(id_)
    element.click()
    driver.implicitly_wait(5)


def switch_by_link(driver, link_text):
    element = driver.driver.find_element_by_link_text(link_text)
    element.click()
    driver.driver.implicitly_wait(5)


def new_session():
    return requests.Session()
