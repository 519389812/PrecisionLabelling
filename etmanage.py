import requests
from PIL import Image
import execjs
import pandas as pd
import base64
import configparser
from bs4 import BeautifulSoup
import time
from settings import chrome_driver
from selenium import webdriver
from common_func import login_emg


class Access:
    """
    接入南航系统获取数据
    """
    def __init__(self):
        """
        基本的网络配置
        """
        self.s = requests.Session()
        # self.captcha_url = 'https://172.31.66.40/captcha.img'
        self.captcha_url = 'https://etmanage.csair.com/Manage/authImg'
        self.etmanage_url = 'https://etmanage.csair.com/Manage/login.jsp'
        self.login_url = 'https://etmanage.csair.com/Manage/loginAction.do'
        self.check_url = 'https://etmanage.csair.com/Manage/changelang.do'
        self.ticket_url = 'https://etmanage.csair.com/Manage/ticketInput.do'
        self.user_data = {
            'member': 'outside',
            'cellphone': '',
        }
        self.headers = {
            'Host': 'etmanage.csair.com',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '96',
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache',
            'Origin': 'https://etmanage.csair.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
            'Referer': 'https://etmanage.csair.com/Manage/login.jsp',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

    def get_captcha(self):
        """
        获取验证码图片

        :return imgs: <list>数据格式验证码
        """
        captcha_img = self.s.get(self.captcha_url, timeout=2)
        with open('etCaptcha.png', 'wb') as f:
            f.write(captcha_img.content)
            # f.flush()  # refresh
        img = Image.open('etCaptcha.png')
        img.show()
        label = input("Please enter captcha code: ")
        return label

    def get_captcha_by_headless(self, rand_image):
        """
        获取验证码图片

        :return imgs: <list>数据格式验证码
        """
        rand_image_size = rand_image.size
        rand_image_location = rand_image.location
        rangle = (int(rand_image_location['x']), int(rand_image_location['y']), int(rand_image_location['x'] + rand_image_size['width']), int(rand_image_location['y'] + rand_image_size['height']))  # 计算验证码整体坐标
        full_image = Image.open("etCaptcha.png")
        rand_image = full_image.crop(rangle)  # 截取验证码图片
        rand_image.save('etCaptcha.png')
        img = Image.open('etCaptcha.png')
        img.show()
        label = input("Please enter captcha code: ")
        return label

    def encode_password(self, password):
        """
        密码加密

        :param password: <str>原始密码
        :return password: <str>加密后密码
        """
        with open('ec.js') as f:
            jsstr = f.read()
        f.close()
        js = execjs.compile(jsstr)
        return js.call('secret', password)

    def access_status(self):
        """
        检查连接是否正常

        :return: "O"正常，“F”异常
        """
        try:
            response = self.s.post(self.check_url, data={"lang": "en"})
            if response.url == self.check_url or response.text == '{"result":"success"}':
                return "O"
            else:
                return "F"
        except:
            return "F"

    def login_by_headless(self, inside=True):
        """
        登录坤翔系统

        :return: 无
        """
        self.__init__()
        # driver = webdriver.PhantomJS(driver_path)
        driver = webdriver.Chrome(chrome_driver)
        driver.get(self.etmanage_url)
        time.sleep(2)
        driver.save_screenshot('etCaptcha.png')
        username = driver.find_element_by_id("userName")
        username.send_keys(input("Please input user name: "))
        time.sleep(2)
        password = driver.find_element_by_id("password")
        password.send_keys(input("Please input password: "))
        time.sleep(2)
        if inside is True:
            rand_image = driver.find_element_by_id("randImage")
            label = self.get_captcha_by_headless(rand_image)
            time.sleep(2)
        else:
            message_btn = driver.find_element_by_class_name("sendButton")
            message_btn.click()
            time.sleep(2)
            label = input("Please input message code: ")
        rand = driver.find_element_by_id("rand")
        rand.send_keys(label)
        time.sleep(2)
        login_btn = driver.find_element_by_id("loginBtn")
        login_btn.click()
        time.sleep(3)
        cookies = driver.get_cookies()
        # driver.close()
        self.s.headers.update(self.headers)
        for cookie in cookies:
            self.s.cookies.set(cookie['name'], cookie['value'])
        status = self.access_status()
        return status

    def login(self):
        """
        登录坤翔系统

        :return: 无
        """
        self.__init__()
        label = self.get_captcha()
        self.user_data['rand'] = label
        self.s.headers.update(self.headers)
        self.response = self.s.post(self.login_url, data=self.user_data)
        status = self.access_status()
        return status

    def call_ticket(self, ticketNumber, carrier="CZ"):
        request_data = {
            'action': 'display',
            'searchType': '0',
            'ticketNumber': ticketNumber,
            'pasgName': '',
            'fltNo': '',
            'fltDate': '',
            'pnrCode': '',
            'certificateId': '',
            'carrier': carrier,
            'flightNo': '',
            'flightDate': '',
        }
        response = self.s.post(self.ticket_url, data=request_data)
        if response.ok:
            content = response.content
            soup = BeautifulSoup(content, 'lxml')
            tags = soup.find_all("tr", attrs={"class": "spread"})
            if len(tags) != 0:
                data = []
                try:
                    for tag in tags:
                        line = tag.find_all("td")
                        coupon = line[0].text.strip()
                        flt_date = line[1].text.strip()
                        airline = line[2].text.strip()
                        flt_num = line[3].text.strip()
                        flight_class = line[4].text.strip()
                        departure = line[5].text.strip()[:3]
                        arrival = line[6].text.strip()[:3]
                        booking_status = line[7].text.strip()
                        involuntary = line[8].text.strip()
                        ticket_status = tag.next_sibling.next_sibling.next_sibling.next_sibling.find_all("td")[1].text.strip()
                        data.append((coupon, flt_date, airline, flt_num, flight_class, departure, arrival, booking_status, involuntary, ticket_status))
                    data = pd.DataFrame(data, columns=['coupon', 'flt_date', 'airline', 'flt_num', 'flight_class', 'departure', 'arrival', 'booking_status', 'involuntary', 'ticket_status'])
                except:
                    return None
            else:
                data = pd.DataFrame(None)
            return data
        else:
            return None

    def call_pax_list(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.folderList", 2)
        profile.set_preference("browser.download.manager.showWhenStarting", False)
        profile.set_preference("browser.download.dir", 'PATH TO DESKTOP')
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

        driver = webdriver.Firefox(firefox_profile=profile)
        driver.get("Name of web site I'm grabbing from")
        driver.find_element_by_xpath("//a[contains(text(), 'DEV.tgz')]").click()