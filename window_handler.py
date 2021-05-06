import pygetwindow as gw
import pyautogui
import os
from box_body import yes_no_box, alert_box
from ics_handler import keyboard_press
import time


def open_app(app_path):
    try:
        os.startfile(app_path)
        time.sleep(3)
        keyboard_press('enter')
        time.sleep(3)
        keyboard_press('enter')
        return True
    except:
        alert_box('无法打开应用程序%s，请检查程序路径是否正确' % app_path, '打开应用程序失败')
        os._exit(0)


def is_app_opened(title_keyword):
    all_titles = get_all_window_titles()
    for title in all_titles:
        if title_keyword in title:
            if yes_no_box('找到：%s，请确认是否已经开启目标的应用？' % title, '确认') == '是':
                return title
    return None


def get_all_window_titles():
    all_titles = gw.getAllTitles()
    return all_titles


def get_window_by_title(title):
    window = gw.getWindowsWithTitle(title)
    if window:
        return window[0]
    else:
        return None


def activate_window(window_object):
    if not window_object.isActive:
        window_object.activate()


def maximize_window(window_object):
    if not window_object.isMaximized:
        window_object.maximize()


def get_window_size(window_object):
    return window_object.size


def get_window_width(window_object):
    return window_object.width


def get_window_height(window_object):
    return window_object.height


def get_window_top_left(window_object):
    return window_object.topleft


def get_window_top(window_object):
    return window_object.top


def get_window_left(window_object):
    return window_object.left


def get_window_bottom_right(window_object):
    return window_object.bottomright


def locate_on_window(location_image_path):
    try:
        return pyautogui.locateOnScreen(location_image_path)
    except:
        return None


def locate_on_window_center(image_location):
    return pyautogui.center(image_location)


def close_window(window_object):
    window_object.close()
