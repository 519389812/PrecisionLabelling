import requests
from PIL import Image
import execjs
import pandas as pd
import base64
import configparser
from bs4 import BeautifulSoup
import time
from settings import chrome_driver, pax_dir, phantomjs_driver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from box_body import ask_box


class Access:
    """
    接入南航系统获取数据
    """
    def __init__(self, engine='chrome'):
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
        self.driver = self.new_driver(engine=engine)

    def new_driver(self, engine):
        try:
            if engine == 'Chrome':
                options = Options()
                options.add_experimental_option("prefs", {
                    "download.default_directory": pax_dir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                })
                driver = webdriver.Chrome(chrome_driver, chrome_options=options)
            elif engine == 'FireFox':
                profile = webdriver.FirefoxProfile()
                profile.set_preference('browser.download.folderList', 2)  # custom location
                profile.set_preference('browser.download.manager.showWhenStarting', False)
                profile.set_preference('browser.download.dir', pax_dir)
                profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
                driver = webdriver.Firefox(profile)
            else:
                driver = webdriver.PhantomJS(phantomjs_driver)
        except:
            driver = webdriver.PhantomJS(phantomjs_driver)
        return driver

    def close_driver(self):
        self.driver.close()

    def get_captcha_by_headless(self, rand_image):
        """
        获取验证码图片

        :return imgs: <list>数据格式验证码
        """
        self.driver.save_screenshot('etCaptcha.png')
        rand_image_size = rand_image.size
        rand_image_location = rand_image.location
        rangle = (int(rand_image_location['x']), int(rand_image_location['y']), int(rand_image_location['x'] + rand_image_size['width']), int(rand_image_location['y'] + rand_image_size['height']))  # 计算验证码整体坐标
        full_image = Image.open("etCaptcha.png")
        rand_image = full_image.crop(rangle)  # 截取验证码图片
        rand_image.save('etCaptcha.png')
        img = Image.open('etCaptcha.png')
        img.show()
        label = ask_box('请输入验证码', '验证码')
        return label

    def confirm_alert(self):
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            return alert.text
        except:
            pass

    def is_login(self):
        if self.driver.current_url == self.etmanage_url:
            return False
        return True

    def login_by_headless(self, inside=True):
        """
        登录坤翔系统

        :return: 无
        """
        self.__init__()
        # self.driver = webdriver.PhantomJS(driver_path)
        self.driver.get(self.etmanage_url)
        self.driver.implicitly_wait(5)
        username = self.driver.find_element_by_id("userName")
        username.send_keys(ask_box('请输入用户名', '用户名'))
        self.driver.implicitly_wait(2)
        password = self.driver.find_element_by_id("password")
        password.send_keys(ask_box('请输入密码', '密码'))
        self.driver.implicitly_wait(2)
        if inside:
            rand_image = self.driver.find_element_by_id("randImage")
            label = self.get_captcha_by_headless(rand_image)
            self.driver.implicitly_wait(2)
        else:
            message_btn = self.driver.find_element_by_class_name("sendButton")
            message_btn.click()
            self.driver.implicitly_wait(2)
            label = ask_box('请输入验证码', '验证码')
        rand = self.driver.find_element_by_id("rand")
        rand.send_keys(label)
        self.driver.implicitly_wait(2)
        login_btn = self.driver.find_element_by_id("loginBtn")
        login_btn.click()
        self.driver.implicitly_wait(5)

    def switch_by_link(self, link_text):
        element = self.driver.find_element_by_link_text(link_text)
        element.click()
        self.driver.implicitly_wait(5)

    def call_pax_list(self, flt_num, flt_date, flt_num_tag_keyword='flightNo', date_tag_name_keyword='flightDate', search_tag_keyword='tktDispBtn', download_tag_keyword='导出EXCEL格式'):
        flt_num_element = self.driver.find_element_by_name(flt_num_tag_keyword)
        flt_num_element.send_keys(flt_num)
        self.driver.implicitly_wait(2)
        # 去除日期选择框的readonly属性
        js = 'document.getElementByName("%s").removeAttribute("readonly")' % date_tag_name_keyword
        self.driver.execute_script(js)
        flt_date_element = self.driver.find_element_by_name(date_tag_name_keyword)
        # 修改日期选择框的value
        # execute_script()第一个参数是设置value，第二个参数表示获取的元素对象
        # arguments[0]可以帮我们把selenium的元素传入到JavaScript语句中，arguments指的是execute_script()方法中js代码后面的所有参数
        # arguments[0]表示第一个参数，argument[1]表示第二个参数
        self.driver.execute_script("arguments[0].value = '%s'" % flt_date, flt_date_element)
        search_button_element = self.driver.find_element_by_name(search_tag_keyword)
        search_button_element.click()
        self.driver.implicitly_wait(20)
        download_button_element = self.driver.find_element_by_xpath('//input[@value="%s"]' % download_tag_keyword)
        download_button_element.click()
        self.driver.implicitly_wait(10)
