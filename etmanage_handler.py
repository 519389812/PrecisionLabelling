import requests
from PIL import Image
from box_body import ask_box, password_box
from driver_handler import switch_by_id, switch_by_link


captcha_url = 'https://etmanage.csair.com/Manage/authImg'
etmanage_url = 'https://etmanage.csair.com/Manage/login.jsp'
login_url = 'https://etmanage.csair.com/Manage/loginAction.do'
check_url = 'https://etmanage.csair.com/Manage/changelang.do'
ticket_url = 'https://etmanage.csair.com/Manage/ticketInput.do'


def get_captcha_by_headless(rand_image):
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


def confirm_alert(driver):
    try:
        alert = driver.switch_to.alert
        alert.accept()
        return alert.text
    except:
        pass


def is_login(driver):
    if driver.current_url == etmanage_url:
        return False
    return True


def login_by_headless(driver, inside=True):
    driver.get(etmanage_url)
    driver.implicitly_wait(5)
    try:
        switch_by_id(driver, 'details-button')
        switch_by_id(driver, 'proceed-link')
    except:
        pass
    driver.save_screenshot('etCaptcha.png')
    username = driver.find_element_by_id("userName")
    username.send_keys(ask_box('请输入用户名', '用户名'))
    driver.implicitly_wait(2)
    password = driver.find_element_by_id("password")
    password.send_keys(password_box('请输入密码', '密码'))
    driver.implicitly_wait(2)
    if inside:
        rand_image = driver.find_element_by_id("randImage")
        label = get_captcha_by_headless(rand_image)
        driver.implicitly_wait(2)
    else:
        message_btn = driver.find_element_by_class_name("sendButton")
        message_btn.click()
        driver.implicitly_wait(2)
        label = ask_box('请输入验证码', '验证码')
    rand = driver.find_element_by_id("rand")
    rand.send_keys(label)
    driver.implicitly_wait(2)
    login_btn = driver.find_element_by_id("loginBtn")
    login_btn.click()
    driver.implicitly_wait(5)


def call_pax_list(driver, flt_num, flt_date, flt_num_tag_keyword='flightNo', date_tag_name_keyword='flightDate', search_tag_keyword='tktDispBtn', download_tag_keyword='导出EXCEL格式'):
    flt_num_element = driver.find_element_by_name(flt_num_tag_keyword)
    flt_num_element.send_keys(flt_num)
    driver.implicitly_wait(2)
    # 去除日期选择框的readonly属性
    js = 'document.getElementByName("%s").removeAttribute("readonly")' % date_tag_name_keyword
    driver.execute_script(js)
    flt_date_element = driver.find_element_by_name(date_tag_name_keyword)
    # 修改日期选择框的value
    # execute_script()第一个参数是设置value，第二个参数表示获取的元素对象
    # arguments[0]可以帮我们把selenium的元素传入到JavaScript语句中，arguments指的是execute_script()方法中js代码后面的所有参数
    # arguments[0]表示第一个参数，argument[1]表示第二个参数
    driver.execute_script("arguments[0].value = '%s'" % flt_date, flt_date_element)
    search_button_element = driver.find_element_by_name(search_tag_keyword)
    search_button_element.click()
    driver.implicitly_wait(20)
    download_button_element = driver.find_element_by_xpath('//input[@value="%s"]' % download_tag_keyword)
    download_button_element.click()
    driver.implicitly_wait(10)
