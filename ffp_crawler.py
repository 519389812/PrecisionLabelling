from selenium import webdriver
from settings import source_dir, ics_processed_dir, config_dir, ics_results_dir
import os
from PIL import Image
import requests
from box_body import ask_box, alert_box, yes_no_box
import pandas as pd
import configparser
import base64
from tools import get_date, get_station
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random


# try:
#     element = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.XPATH, '//*[@id="su"]'))
#     )
#     text = driver.page_source
#     print("text", text)
# finally:
#     driver.quit()


ffp_url = 'https://ffp.csair.com'
config = configparser.ConfigParser()
config.read('%s%sconfig.ini' % (config_dir, os.sep))
username = config.get('ffp', 'username')
password = base64.b64decode(config.get('ffp', 'password')).decode()


def get_ff_list(date):
    try:
        ff_list = pd.read_excel('%s%s%s.xlsx' % (ics_processed_dir, os.sep, date), converters={'flt_num': str, 'ff_number': str})
    except:
        alert_box('未找到当天航班的xlsx文档，请检查。注：文档需从SOC预报中直接复制入Excel表格，并以YYYY-MM-DD_XXX.xlsx命名，其中XXX为场站三字码。', '退出程序')
        os._exit(0)
    ff_list = ff_list[(ff_list['ff_airline'] == 'CZ') & (ff_list['ff_number'].isna() == False) & (ff_list['ff_number'] != '')]
    if len(ff_list) == 0:
        alert_box('会员列表无数据，请确认。', '退出程序')
        os._exit(0)
    ff_list.fillna('', inplace=True)
    return ff_list


def open_driver():
    driver = webdriver.Chrome('%s%schromedriver.exe' % (source_dir, os.sep))
    driver.maximize_window()
    driver.implicitly_wait(10)
    return driver


def get_captcha_image(captcha_image_url):
    # with open('%s%scaptcha.png' % (captcha_dir, os.sep), 'wb') as f:
    #     f.write(requests.get(captcha_image_url).content)
    # image = Image.open('%s%scaptcha.png' % (captcha_dir, os.sep))
    # image.show()
    captcha_code = ask_box('请输入验证码', '验证码')
    return captcha_code


def login_ffp(driver, username=username, password=password):
    while True:
        driver.get(ffp_url)
        driver.implicitly_wait(10)
        try:
            driver.find_element_by_id('acceptButton').click()
        except:
            pass
        username_input = driver.find_element_by_id('j_username')
        password_input = driver.find_element_by_id('j_password')
        captcha_input = driver.find_element_by_id('j_verify')
        username_input.clear()
        driver.implicitly_wait(1)
        username_input.send_keys(username)
        driver.implicitly_wait(1)
        password_input.send_keys(password)
        driver.implicitly_wait(1)
        captcha_image_url = captcha_input.find_element_by_xpath('..').find_element_by_tag_name('img').get_attribute('src')
        captcha_code = get_captcha_image(captcha_image_url)
        captcha_input.send_keys(captcha_code)
        driver.implicitly_wait(1)
        driver.find_element_by_id('loginButton').click()
        driver.implicitly_wait(10)
        if 'error' in driver.current_url:
            choice = yes_no_box('登录失败，是否重新登录？', 'ICS登录')
            if choice == '是':
                continue
            else:
                alert_box('您正在退出程序，感谢使用', '退出程序')
                os._exit(0)
        driver.find_element_by_id('row_customer').click()
        driver.implicitly_wait(10)
        return driver


def main_crawler(driver, ff_list):
    unstructured_data = []
    for _, row in ff_list.iterrows():
        try:
            driver.find_element_by_id('j_idt2:customerSearchForm:j_idt3:j_idt21:ccNo:ccNoAccessCheckPanel:ccNo').send_keys(row['ff_number'])
            driver.implicitly_wait(1)
            driver.find_element_by_id('j_idt2:customerSearchForm:j_idt3:customerSearchActionBar:customerSearchActionBarFindButton').click()
            driver.implicitly_wait(10)
            time.sleep(1 + random.random())
            available_miles = driver.find_element_by_id('j_idt2:customerOverviewForm:bonusBalanceCumulative_2').text
            name = row['last_name'] + '/' + row['first_name'] if row['first_name'] != '' else row['last_name']
            unstructured_data.append((row['flt_date'], row['station'], 'CZ'+row['flt_num'], name, row['seat_class'],
                                      row['group_'], row['ff_number'], row['ff_level'], available_miles, row['inbound']))
            driver.find_element_by_id('row_searchCustomerMenu').click()
            driver.implicitly_wait(10)
            time.sleep(1 + random.random())
        except:
            driver.implicitly_wait(10)
            time.sleep(1 + random.random())
            continue
    return unstructured_data


def data_structuring(unstructured_data, date):
    structured_data = pd.DataFrame(unstructured_data,
                                   columns=['flt_date', 'station', 'flt_num', 'name', 'seat_class', 'group_',
                                            'ff_number', 'ff_level', 'available_miles', 'inbound'])
    structured_data.to_excel('%s%s%s_ffp.xlsx' % (ics_results_dir, os.sep, date))


def logout_ffp(driver):
    driver.find_element_by_id('arrow').click()
    driver.implicitly_wait(2)
    driver.find_element_by_id('logout').click()
    driver.implicitly_wait(2)


if __name__ == "__main__":
    date = get_date()
    ff_list = get_ff_list(date)
    try:
        driver = open_driver()
        login_ffp(driver)
        unstructured_data = main_crawler(driver, ff_list)
        data_structuring(unstructured_data, date)
        alert_box('数据处理完毕，请从%s文件夹查看，感谢使用！' % ics_results_dir, '退出程序')
    except:
        alert_box('程序出现问题，正在退出程序，感谢使用！', '退出程序')
    finally:
        logout_ffp(driver)
        driver.quit()
