import pandas as pd
import datetime
import os
from settings import task_dir
from box_body import date_box, alert_box


def create_date_list(start_date, end_date):
    date_list = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').to_list()
    return date_list


def get_data_from_file(date):
    files = os.listdir(task_dir)
    for file in files:
        if date in file:
            data = pd.read_csv('%s%s%s' % (task_dir, os.sep, file), encoding='gbk', converters={'会员卡号': str, '飞行日期': str, 'OC航班号': str, '电子客票号': str})
            data.replace('\t', '', regex=True, inplace=True)
            data['飞行日期'] = pd.to_datetime(data['飞行日期']).dt.strftime('%Y-%m-%d')
            data.fillna('', inplace=True)
            return data


def main():
    start_date = date_box('请输入开始日期', '开始日期')
    end_date = date_box('请输入结束日期', '结束日期')
    date_list = create_date_list(start_date, end_date)
    if not date_list:
        alert_box('日期填写有误', '错误')
    data = pd.DataFrame(None)
    for date in date_list:
        data_temp = get_data_from_file(date)
        if data_temp:
            data = pd.concat([data, data_temp], ignore_index=True, join='outer')
        else:
            continue
    if data.shape[0] == 0:
        alert_box('未提取到数据', '错误')



if __name__ == '__main__':
    pass
