from box_body import *
import datetime
import re
from window_handler import locate_on_window, locate_on_window_center
from ics_handler import *
import configparser
from settings import config_dir
from window_handler import is_app_opened, open_app, get_window_by_title
from dateutil.relativedelta import relativedelta


config = configparser.ConfigParser()
config.read('%s%sconfig.ini' % (config_dir, os.sep))


def get_date():
    while True:
        date = date_box()
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
            return date
        except:
            if yes_no_box('输入日期格式有误，是否重新输入？', '日期格式错误') == '是':
                continue
            else:
                alert_box('您正在退出程序，感谢使用', '退出程序')
                os._exit(0)


def get_station():
    while True:
        station = ask_box('请输入场站', '场站', 'CAN')
        pattern = r'[A-Za-z]{3}'
        if re.match(pattern, station):
            return station.upper()
        else:
            if yes_no_box('输入格式有误，是否重新输入？', '格式错误') == '是':
                continue
            else:
                alert_box('您正在退出程序，感谢使用', '退出程序')
                os._exit(0)


def change_ics_date_format(date):  # 从 2018-08-25 转换成 25AUG18
    month_exchange = {'01': 'JAN', '02': 'FEB', '03': 'MAR', '04': 'APR', '05': 'MAY', '06': 'JUN', '07': 'JUL',
                      '08': 'AUG', '09': 'SEP', '10': 'OCT', '11': 'NOV', '12': 'DEC'}
    year, month, day = date.split('-')
    date = day + month_exchange[month] + year[2:]
    return date


def roll_back_ics_date_format(date):  # 25AUG18 转换成 2018-08-25
    try:
        month = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
        date = date[-2:]+month[date[2:5]]+date[:2]
        date = datetime.datetime.strptime(date, "%y%m%d")
        # if date.date() > datetime.datetime.now().date():
        #     date = date - relativedelta(years=100)
        date = date.strftime("%Y-%m-%d")
        return date
    except:
        return ''


def adjust_location():
    keyboard_clean_screen()
    keyboard_press('esc', 'esc', 'esc', 'esc', 'esc', 'esc')
    paste_start_location = locate_on_window(config.get('location', 'paste_start_location_image_path'))
    try:
        x_start = paste_start_location[0]
        paste_start_location = locate_on_window_center(paste_start_location)
        y_start = paste_start_location[1]
    except:
        try:
            paste_start_location = config.get('location', 'paste_start_location').split(',')
        except:
            paste_start_location = (4, 142)  # 默认最大化时开始位置
        x_start, y_start = paste_start_location
    x_start, y_start = int(x_start), int(y_start)
    try:
        paste_end_location_offset = config.get('location', 'paste_end_location_offset').split(',')
    except:
        paste_end_location_offset = (635, 370)
    x_end, y_end = x_start + int(paste_end_location_offset[0]), y_start + int(paste_end_location_offset[1])
    x_end, y_end = int(x_end), int(y_end)
    return x_start, y_start, x_end, y_end


def activate_app(app_path, title_keyword):
    title = is_app_opened(title_keyword)
    if not title:
        open_app(app_path)
        title = is_app_opened(title_keyword)
        if not title:
            alert_box('应用程序已开启，但程序未检测到相应的的窗口，请检查窗口名字设置是否正确，或者应用程序运行是否正常。', '错误')
            os._exit(0)
    window_object = get_window_by_title(title)
    return window_object


def switch_input_language():
    alert_box('【重要】请将屏幕切换至ICS屏幕，切换【输入法】至【英文】，然后点击【确认】', '输入法确认')


def copy_text(x_start, y_start, x_end, y_end):
    mouse_move(x_start, y_start)
    mouse_drap(x_end, y_end, button='left')
    text_copy()
    text = text_paste()
    return text


def is_ics_login(text, signed_in_text='SIGNED IN'):
    if signed_in_text in text:
        return True
    return False


def login_ics(x_start, y_start, x_end, y_end):
    choice = yes_no_box('是否已经登录工号？', 'ICS登录')
    if choice != '是':
        while True:
            username, password, level, office = login_ics_box()
            keyboard_write_si(username, password, level, office)
            text = copy_text(x_start, y_start, x_end, y_end)
            if is_ics_login(text):
                break
            else:
                choice = yes_no_box('登录失败，是否重新输入？', 'ICS登录')
                if choice == '是':
                    continue
                else:
                    alert_box('您正在退出程序，感谢使用', '退出程序')
                    os._exit(0)


def login_emg():
    choice = yes_no_box('是否已经登录工号？', 'ICS登录')
    if choice != '是':
        while True:
            username, password, level, office = login_ics_box()
            keyboard_write_si(username, password, level, office)
            text = copy_text(x_start, y_start, x_end, y_end)
            if is_ics_login(text):
                break
            else:
                choice = yes_no_box('登录失败，是否重新输入？', 'ICS登录')
                if choice == '是':
                    continue
                else:
                    alert_box('您正在退出程序，感谢使用', '退出程序')
                    os._exit(0)


if __name__ == '__main__':
    pass
