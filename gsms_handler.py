import requests
from PIL import Image
import execjs
import datetime
import json
import pandas as pd
import time
from selenium import webdriver
from box_body import ask_box, password_box


from http import client
client.HTTPConnection._http_vsn = 10
client.HTTPConnection._http_vsn_str = 'HTTP/1.0'

login_url = 'https://gsms.csair.com/head-Login-login.gsms'
captcha_url = 'https://gsms.csair.com/captcha.img'
check_url = 'https://gsms.csair.com/main_defaultmain.gsms'

list_url = 'https://gsms.csair.com/ghc-rebooking-QueryRebookingPsg-queryBatchPsgList.gsms'
flight_list_url = 'https://gsms.csair.com/ghc-flightForecast-Flight-queryFlightForecastList.gsms'

headers = {
    'Host': 'gsms.csair.com',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://gsms.csair.com',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://gsms.csair.com/main_defaultmain.gsms#',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}


def new_session():
    return requests.Session()


def data_exchange(the_date):
    """
    日期格式转换

    :param the_date: <str>日期格式如20180101
    :return the_date: <str>日期格式如2018-01-01
    """
    if the_date == '.':
        return datetime.date.today().strftime('%Y-%m-%d')
    elif the_date == '+':
        return (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    elif the_date == '-':
        return (datetime.date.today() + datetime.timedelta(days=-1)).strftime('%Y-%m-%d')
    else:
        return the_date


def is_login(session):
    response = session.post(check_url)
    if response.url == login_url:
        return False
    return True


def get_captcha_by_headless(rand_image):
    rand_image_size = rand_image.size
    rand_image_location = rand_image.location
    rangle = (int(rand_image_location['x']), int(rand_image_location['y']),
              int(rand_image_location['x'] + rand_image_size['width']),
              int(rand_image_location['y'] + rand_image_size['height']))  # 计算验证码整体坐标
    full_image = Image.open("gsmsCaptcha.png")
    rand_image = full_image.crop(rangle)  # 截取验证码图片
    rand_image.save('gsmsCaptcha.png')
    img = Image.open('gsmsCaptcha.png')
    img.show()
    label = ask_box('请输入验证码', '验证码')
    return label


def login_by_headless(driver, session, inside=True):
    driver.get(login_url)
    driver.implicitly_wait(5)
    driver.save_screenshot('gsmsCaptcha.png')
    username = driver.find_element_by_id("j_username")
    username.send_keys(ask_box('请输入用户名', '用户名'))
    driver.implicitly_wait(2)
    password = driver.find_element_by_id("j_password")
    password.send_keys(password_box('请输入密码', '密码'))
    driver.implicitly_wait(2)
    if inside:
        rand_image = driver.find_element_by_id("imgCode")
        label = get_captcha_by_headless(rand_image)
        driver.implicitly_wait(2)
    else:
        message_btn = driver.find_element_by_class_name("sendButton")
        message_btn.click()
        driver.implicitly_wait(2)
        label = ask_box('请输入验证码', '验证码')
    rand = driver.find_element_by_id("inputRand")
    rand.send_keys(label)
    driver.implicitly_wait(2)
    login_btn = driver.find_element_by_class_name("submitBtn")
    login_btn.click()
    driver.implicitly_wait(5)
    cookies = driver.get_cookies()
    session.headers.update(headers)
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])


def call_flight_list(session, date='.', dep_code='CAN', type_="国际出港"):
    types = {
        '出港航班': 'O',
        '进港航班': 'I',
        '国际进港': 'II',
        '国际出港': 'IO',
        '国内进港': 'DI',
        '国内出港': 'DO',
        '南航进港': 'CZI',
        '南航出港': 'CZO',
        '外航进港': 'OTHI',
        '外航出港': 'OTHO',
        '所有航班': 'MUO',
    }
    request_data = {
        'fltDate': data_exchange(date),
        'airport': dep_code,
        'fcasType': types[type_],
        'fcasTypeText': type_,
    }
    response = session.post(flight_list_url, data=request_data)
    flight_list = []
    if response.ok:
        json_data = json.loads(response.content)
        rows = json_data['rows']
        if len(rows) != 0:
            try:
                for row in rows:
                    flt_num, flt_date, dep_code, arr_code, airline_code, soc_task, tail_num = row['fltNr'], row['schDepDtStr'], row['depCd'], row['arvCd'], row['alnCd'], row['socTask'], row['tailNr']
                    if airline_code == 'CZ' and soc_task != 'F':
                        date_time = flt_date.split(" ")
                        date = date_time[0]
                        time = date_time[1]
                        flight_list.append((flt_num, flt_date, date, time, dep_code, arr_code, airline_code, soc_task, tail_num))
                flight_list = pd.DataFrame(flight_list, columns=['flt_num', 'flt_datetime', 'flt_date', 'flt_time', 'departure', 'arrival', 'airline', 'task', 'tail number'])
                return flight_list
            except:
                return
        else:
            flight_list = pd.DataFrame(None)
            return flight_list
    else:
        return


if __name__ == '__main__':
    pass
