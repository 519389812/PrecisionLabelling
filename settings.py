import os
import pandas as pd
import configparser
from box_body import open_file_box, ask_box, yes_no_box, alert_box
import re

auth_level = '86'
auth_office = {'CAN': '007', 'KWE': '005', 'HAK': '005', 'SWA': '005', 'SHA': '005', 'PVG': '005', 'CGO': '002', 'URC': '000'}
client_auth_stations = list(auth_office.keys())

additional_data_columns = ['姓名', '查询', '备注']  # 改动需调整源码
labels = ['LCSCJ', 'LCSCF', 'LCGQ', 'XFSC', 'XFDZ', 'PJBMG', 'XLPS', 'TS', 'BX']  # 改动需调整filter

config_dir = 'config'
config_file = '%s%sconfig.ini' % (config_dir, os.sep)
task_dir = 'task'
source_dir = 'source'
sales_dir = 'sales'
driver_dir = 'driver'
flt_dir = 'flt'
pax_dir = 'pax'
result_dir = 'result'
pax_temporary_dir = os.getcwd() + os.sep + 'paxTemporary'
chrome_driver = '%s%schromedriver%s%s%schromedriver.exe' % (driver_dir, os.sep, os.sep, '91', os.sep)
phantomjs_driver = '%s%sphantomjs%s%s%sphantomjs.exe' % (driver_dir, os.sep, os.sep, 'bin', os.sep)
geckodriver_driver = '%s%sgeckodriver%s%s%sgeckodriver.exe' % (driver_dir, os.sep, os.sep, '0.29.1', os.sep)

source_file = '%s%supgrade_miles.xlsx' % (source_dir, os.sep)


def check_file(file):
    if not os.path.exists(file):
        alert_box('缺少 %s 文件' % file, '错误')
        os._exit(0)


config_init = {
    'app': [
        ['app_path', ''],
        ['title_keyword', 'eTerm'],
    ],
    'location': [
        ['paste_start_location_image_path', 'config\paste_start_location_image.png'],
        ['paste_start_location', '4,142'],
        ['paste_end_location_offset', '635,370'],
    ],
    'client': [
        ['comment', '1'],
    ],
}


def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


for dir_ in [config_dir, task_dir, source_dir, sales_dir, driver_dir, pax_dir, result_dir, pax_temporary_dir]:
    make_dir(dir_)


def check_config_file():
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            pass
    config = configparser.ConfigParser()
    config.read(config_file)
    for section, options in config_init.items():
        if not config.has_section(section):  # 检查是否存在section
            config.add_section(section)
            with open(config_file, 'w') as f:
                config.write(f)
        for option, value in options:
            if not config.has_option(section, option):  # 检查是否存在该option
                config.set(section, option, value)
                with open(config_file, 'w') as f:
                    config.write(f)


def reload_config():
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def reload_config_value(section, option):
    return config.get(section, option)


check_config_file()
config = reload_config()
app_path = reload_config_value('app', 'app_path')
title_keyword = config.get('app', 'title_keyword')
comment_only = bool(int(reload_config_value('client', 'comment')))


for file in [source_file, chrome_driver, phantomjs_driver, geckodriver_driver]:
    check_file(file)
upgrade_miles = pd.read_excel(source_file)
upgrade_miles.fillna(0, inplace=True)
upgrade_miles['city_pair'] = upgrade_miles['departure'] + '-' + upgrade_miles['destination']
upgrade_miles.set_index(['city_pair'], inplace=True)

upgrade_miles['miles_y_to_j'] = upgrade_miles['miles_y_to_j'].astype('float64')


def set_app_path():
    app_path = open_file_box('请选择ICS路径', filetypes=[('.', '*.*')])
    config.set('app', 'app_path', app_path)
    with open(config_file, 'w') as f:
        config.write(f)
