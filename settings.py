import os


config_dir = 'config'
raw_dir = 'raw'
task_dir = 'task'
source_dir = 'source'


def make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


for dir_ in [config_dir, task_dir, source_dir]:
    make_dir(dir_)


check_airports = {
    'CAN': True,
    'URC': False,
    'PKX': False,
    'SYX': False,
    'PVG': False,
    'HAK': False,
    'SHA': False
}
