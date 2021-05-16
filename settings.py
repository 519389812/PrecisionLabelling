import os
import pandas as pd
import configparser
from box_body import open_file_box


label_only = False

check_stations = ['CAN', 'URC', 'PKX', 'SYX', 'PVG', 'HAK', 'SHA']
ics_auth_stations = ['CAN']


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


check_config_file()
config = reload_config()
app_path = reload_config_value('app', 'app_path')
title_keyword = config.get('app', 'title_keyword')


def set_app_path():
    app_path = open_file_box(filetypes=[('.', '*.*')])
    config.set('app', 'app_path', app_path)
    with open(config_file, 'w') as f:
        config.write(f)
