import os
import pandas as pd
import configparser
from box_body import open_file_box, ask_box, yes_no_box
import re


comment_only = False

check_stations = ['CAN', 'URC', 'PKX', 'SYX', 'PVG', 'HAK', 'SHA']
ics_auth_stations = ['CAN']
additional_data_columns = ['标签', '姓名', '查询', '备注']  # 改动需调整源码
labels = ['LCSCJ', 'LCSCF', 'LCGQ', 'XFSC', 'XFDZ', 'PJBMG']  # 改动需调整filter


config_dir = 'config'
config_file = '%s%sconfig.ini' % (config_dir, os.sep)
task_dir = 'task'
source_dir = 'source'

upgrade_miles = pd.read_excel('%s%supgrade_miles.xlsx' % (source_dir, os.sep))
upgrade_miles.fillna(0, inplace=True)
upgrade_miles['city_pair'] = upgrade_miles['departure'] + '-' + upgrade_miles['destination']
upgrade_miles.set_index(['city_pair'], inplace=True)

config_init = {
    'app': [
        {'app_path': ''},
        {'title_keyword': 'eTerm'}
    ],
    'location': [
        {'paste_start_location_image_path': 'config\paste_start_location_image.png'},
        {'paste_start_location': '4,142'},
        {'paste_end_location_offset': '635,370'}
    ],
    'user': [
        {'station': ''}
    ]
}


def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


for dir_ in [config_dir, task_dir, source_dir]:
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


def reload_config_station():
    return list(filter(None, config.get('user', 'station').split('/')))


check_config_file()
config = reload_config()
app_path = reload_config_value('app', 'app_path')
title_keyword = config.get('app', 'title_keyword')
stations = reload_config_station()


def set_app_path():
    app_path = open_file_box(filetypes=[('.', '*.*')])
    config.set('app', 'app_path', app_path)
    with open(config_file, 'w') as f:
        config.write(f)


def set_ics_auth_station():
    while True:
        stations = ask_box('请输入您使用的场站（格式为：CAN，输入多个时：CAN/PKX/URC）：', '场站设置').strip('/').upper()
        pattern = re.compile(r'^([A-Z]{3}/?)+$')
        if pattern.match(stations):
            config.set('user', 'station', stations)
            with open(config_file, 'w') as f:
                config.write(f)
                break
        else:
            select = yes_no_box('输入格式不正确，是否重新输入？', '格式错误')
            if select == '否':
                os._exit(0)
