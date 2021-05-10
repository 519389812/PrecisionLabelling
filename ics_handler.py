import pyautogui
import pyperclip
import re


def locate_top_left(top_left_image_path):
    top_left_location = pyautogui.locateOnScreen(top_left_image_path)
    top_left_location = pyautogui.center(top_left_location)
    return top_left_location


def keyboard_write(command: str, clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1, count: int = 1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_si(username: str, password: str, level: str, office: str, clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.3, count: int = 1):
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    pyautogui.write('si', interval=interval)
    keyboard_press('f12', interval=interval, count=count)
    pyautogui.write('%s/%s/%s/%s' % (username, password, level, office), interval=interval)
    keyboard_press(execute_press)


def keyboard_write_so(clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1, count: int = 1):
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    pyautogui.write('so', interval=interval)
    keyboard_press(execute_press)


def keyboard_write_ft(flt_num: str, flt_date: str, station: str = 'CAN', clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1, count: int = 1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'ft%s/%s/%s' % (flt_num, flt_date, station)
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_pd(flt_num: str, flt_date: str, *additions: str, cabin_class='', station: str = 'CAN', clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'pd%s/%s' % (flt_num, flt_date)
    command += cabin_class + '*'
    command += station
    if additions:
        for addition in additions:
            command += ',' + addition
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_pr(count: int, clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'pr' + str(count) + 'pd'
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_fb(flt_num: str, flt_date: str, cabin_class, bn: str, station: str = 'CAN', clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1, count: int = 1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'pr%s/%s' % (flt_num, flt_date)
    if cabin_class:
        command += cabin_class + '*'
    else:
        command += '*'
    command += station + ',' + 'bn' + bn
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_pn(count: int = 1, clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'pn' + str(count)
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_pl(count: int = 1, clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'pl' + str(count)
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_pf(count: int = 1, clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'pf' + str(count)
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_pu(*additions: str, clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1, count: int = 1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'pu' + str(count)
    if additions:
        for addition in additions:
            command += ',' + addition
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_pre_pu(*additions: str, clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1, count: int = 1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'pu#' + str(count)
    if additions:
        for addition in additions:
            command += ',' + addition
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_write_etkd(tkt_num: str, clean_screen_press: list = None, set_soe_press: str = 'esc', execute_press: str = 'f12', interval: float = 0.1) -> None:
    keyboard_clean_screen(clean_screen_press)
    keyboard_press(set_soe_press)
    command = 'etkd:tn/' + tkt_num
    pyautogui.write(command, interval=interval)
    keyboard_press(execute_press)


def keyboard_press(*keys: str, interval: float = 0.2, count: int = 1) -> None:
    if len(keys) == 1:
        pyautogui.press(keys[0], presses=count, interval=interval)
    else:
        pyautogui.press(list(keys), interval=interval)


def keyboard_key_up(key, interval: float = 0.2) -> None:
    pyautogui.keyUp(key, interval=interval)


def keyboard_key_down(key, interval: float = 0.2) -> None:
    pyautogui.keyDown(key, interval=interval)


def keyboard_hot_key(*keys: str, interval: float = 0.2) -> None:
    eval('pyautogui.hotkey(%s, interval=%f)' % (str(keys)[1:-1], interval))


def keyboard_clean_screen(key_list: list = None, interval: float = 0.2) -> None:
    if key_list is None:
        key_list = ['ctrl', 'a']
    eval('pyautogui.hotkey(%s, interval=%f)' % (str(key_list)[1:-1], interval))


# >>> pyautogui.moveTo(100, 100, 2, pyautogui.easeInQuad)     # start slow, end fast
# >>> pyautogui.moveTo(100, 100, 2, pyautogui.easeOutQuad)    # start fast, end slow
# >>> pyautogui.moveTo(100, 100, 2, pyautogui.easeInOutQuad)  # start and end fast, slow in middle
# >>> pyautogui.moveTo(100, 100, 2, pyautogui.easeInBounce)   # bounce at the end
# >>> pyautogui.moveTo(100, 100, 2, pyautogui.easeInElastic)  # rubber band at the end
def mouse_move(x: int, y: int, duration: float = 0.1) -> None:
    pyautogui.moveTo(x, y, duration=duration)


def mouse_drap(x: int, y: int, button: str = 'left', duration: float = 0.4) -> None:
    pyautogui.dragTo(x, y, button=button, duration=duration, tween=pyautogui.easeOutQuad)


def mouse_click(button: str = 'left', clicks: int = 3, interval: float = 0.2):
    pyautogui.click(button=button, clicks=clicks, interval=interval)


def mouse_up(button: str = 'left', x: int = None, y: int = None, duration: float = 0.2):
    if x and y:
        pyautogui.mouseUp(button=button, x=x, y=y, duration=duration)
    else:
        pyautogui.mouseUp(button=button, duration=duration)


def mouse_down(button: str = 'left', x: int = None, y: int = None, duration: float = 0.2):
    if x and y:
        pyautogui.mouseDown(button=button, x=x, y=y, duration=duration)
    else:
        pyautogui.mouseDown(button=button, duration=duration)


def mouse_scroll(clicks: int = 3, x: int = None, y: int = None, duration: float = 0.2):
    if x and y:
        pyautogui.mouseDown(clicks=clicks, x=x, y=y, duration=duration)
    else:
        pyautogui.mouseDown(clicks=clicks, duration=duration)


def mouse_position():
    return pyautogui.position()


def text_copy():
    keyboard_hot_key('ctrl', 'c')


def text_paste():
    return pyperclip.paste()


def text_find_index(text):
    index_list = re.findall(r'\d+\.', text)
    if index_list:
        return index_list[0][:-1], index_list[-1][:-1]
    else:
        return None


def text_has_flight(text):
    if 'FLT NBR' in text or 'NEED INITIALIZE' in text:
        return False
    else:
        return True


def text_has_ticket(text):
    if 'GET TICKET FROM' in text:
        return False
    else:
        return True


def text_has_number(text):
    if 'ENTRY NBR' in text:
        return False
    else:
        return True
