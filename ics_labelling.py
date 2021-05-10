from ics_handler import *
from box_body import *
from window_handler import *
import os
import configparser
import ics_data_collector
import ticket_data_collector
from settings import *
from common_func import *
import pandas as pd
import pypinyin
from itertools import product
from settings import check_airports


upgrade_miles = pd.read_excel('%s%supgrade_miles.xlsx' % (source_dir, os.sep))
upgrade_miles.fillna('', inplace=True)
upgrade_miles['city_pair'] = upgrade_miles['departure'] + '-' + upgrade_miles['destination']
upgrade_miles.set_index(['city_pair'], inplace=True)


def get_data():
    while True:
        file_path = open_file_box('选择数据文件', './task', [('csv文件', '.csv')])
        date = get_date()
        try:
            data = pd.read_csv(file_path, converters={'会员卡号': str, '飞行日期': str, 'OC航班号': str, '电子客票号': str}, encoding='gbk')
        except:
            try:
                data = pd.read_csv(file_path, converters={'会员卡号': str, '飞行日期': str, 'OC航班号': str, '电子客票号': str})
            except:
                select = yes_no_box('读取数据失败，请检查所选文件是否正确，或者文件内容是否经人为更改。是否重新选择文件？', '文件读取失败')
                if select == "是":
                    continue
                else:
                    os._exit(0)
        data.replace('\t', '', regex=True, inplace=True)
        data['飞行日期'] = pd.to_datetime(data['飞行日期']).dt.strftime('%Y-%m-%d')
        data.fillna('', inplace=True)
        if data.shape[0] == 0:
            select = yes_no_box('所选文件无数据。是否重新选择文件？', '无数据')
            if select == "是":
                continue
            else:
                os._exit(0)
        data = create_new_columns(data, '已查', '标签', '姓名')
        picked_data = filtering_data(data, date)
        if picked_data.shape[0] == 0:
            select = yes_no_box('所选文件无符合条件数据。是否重新选择文件？', '无服务条件数据')
            if select == "是":
                continue
            else:
                os._exit(0)
        data.loc[data[data['飞行日期'] == date].index.difference(picked_data.index), '已查'] = '不符合条件'
        data.loc[picked_data[picked_data['已查'] == '不符合条件'].index, '已查'] = ''
        picked_data = filtering_data(data, date)
        save_data(data, file_path)
        return data, picked_data, file_path


def create_new_columns(data, *args):
    for column in args:
        if column not in data.columns:
            data[column] = ''
    return data


def save_data(data, file_path):
    data['会员卡号'] = data['会员卡号'].apply(lambda x: '\t' + x)
    data['OC航班号'] = data['OC航班号'].apply(lambda x: '\t' + x)
    data['电子客票号'] = data['电子客票号'].apply(lambda x: '\t' + x)
    data.to_csv(file_path, index=False)


def create_filter_condition():
    filter_condition = []
    for index_ in list(upgrade_miles.index):
        filter_condition.append("((data['OC母舱位'] == 'Y') & (data['航段性质'] != '国内') & (data['航段'] == '%s') & (data['可用里程余额'] >= upgrade_miles.loc['%s', 'miles_y_to_j']))" % (index_, index_))
        if upgrade_miles.loc[index_, 'miles_j_to_f'] != '':
            filter_condition.append("((data['OC母舱位'] == 'J') & (data['航段性质'] != '国内') & (data['航段'] == '%s') & (data['可用里程余额'] >= upgrade_miles.loc['%s', 'miles_j_to_f']))" % (index_, index_))
    filter_condition = ' | '.join(filter_condition)
    filter_condition += " | ((data['航段性质'] == '国内') & (data['OC母舱位'] == 'Y') & (data['OC子舱位'] != 'X') & (data['可用里程余额'] >= 20000))"
    filter_condition += "| (data['近三月到期里程'] >= 6000)"
    filter_condition += "| (data['近一年购买升舱次数'] > 0) | (data['近一年购买一人多座次数'] > 0) | (data['差旅类票价不敏感旅客'] == '是')"
    filter_condition = "data[%s]" % filter_condition
    return filter_condition


def filtering_data(data, date):
    data.replace('\t', '', regex=True, inplace=True)
    data = data[(data['OC承运人'] == 'CZ') & (data['飞行日期'] == date) & data['OD始发机场'].isin(list(check_airports.keys())) == True]
    if '近一年购买升舱次数' not in data.columns:
        data['近一年购买升舱次数'] = data['近一年购买登机口升舱次数'] + data['近一年购买候补升舱次数'] + data['近一年购买休息室升舱次数']
    if '近三月到期里程' not in data.columns:
        data['近三月到期里程'] = data['本月到期里程'] + data['下月到期里程'] + data['下下月到期里程']
    filter_condition = create_filter_condition()
    data = eval(filter_condition)
    return data


def create_label(row):
    label = ''
    if row['OC母舱位'] == 'Y' and row['航段性质'] != '国内' and (row['航段'] in list(upgrade_miles.index)):
        if row['可用里程余额'] >= upgrade_miles.loc[row['航段'], 'miles_y_to_j']:
            label += 'LCSC '
    elif row['OC母舱位'] == 'J' and row['航段性质'] != '国内' and (row['航段'] in list(upgrade_miles.index)) and upgrade_miles.loc[row['航段'], 'miles_j_to_f'] != '':
        if row['可用里程余额'] >= upgrade_miles.loc[row['航段'], 'miles_j_to_f']:
            label += 'LCSC '
    elif row['OC母舱位'] == 'Y' and row['航段性质'] == '国内' and row['可用里程余额'] > 20000:
        label += 'LCSC '
    if row['近三月到期里程'] > 0:
        label += 'LCGQ '
    if row['近一年购买升舱次数'] > 0:
        label += 'XFSC '
    if row['近一年购买一人多座次数'] > 0:
        label += 'XFDZ '
    if row['差旅类票价不敏感旅客'] == '是':
        label += 'PJBMG '
    return label


def describe_data(data):
    num_of_data = data.shape[0]
    num_of_unhandled_data = data[data['已查'] == ''].shape[0]
    if num_of_unhandled_data == 0:
        alert_box('筛选出符合条件的数据 %d 条，所有数据已经处理完毕，程序退出' % num_of_data, '完毕')
        os._exit(0)
    else:
        alert_box('筛选出符合条件的数据 %d 条，其中已处理的数据有 %d 条，未处理的数据有 %d 条。' % (num_of_data, num_of_data - num_of_unhandled_data, num_of_unhandled_data), '概况')
        data = data[data['已查'] == '']
        return data


def labelling(data, picked_data, file_path):
    try:
        for index_, row in picked_data.iterrows():
            label = create_label(row)
            if label == '':
                data.loc[index_, '已查'] = '不符合条件'
                continue
            data.loc[index_, '标签'] = label
            station = row['OD始发机场']
            if check_airports[station]:
                flt_num = row['OC承运人'] + row['OC航班号']
                flt_date = row['飞行日期']
                flt_date = change_ics_date_format(flt_date)
                ticket = row['电子客票号']
                keyboard_write_etkd(ticket)
                text = copy_text(x_start, y_start, x_end, y_end)
                if not text_has_ticket(text):
                    data.loc[index_, '已查'] = '未能提取客票'
                    continue
                ticket_data = ticket_data_collector.details_extract(text)
                if ticket_data:
                    if ticket_data['first_name'] != '':
                        pax_name = ticket_data['last_name'] + '/' + ticket_data['first_name']
                    else:
                        pax_name = ticket_data['last_name']
                else:
                    data.loc[index_, '已查'] = '客票信息提取异常'
                    continue
                data.loc[index_, '姓名'] = pax_name
                name_list = [''.join(name) for name in product(*pypinyin.pinyin(pax_name, style=pypinyin.NORMAL, heteronym=True))]
                found = False
                for name in name_list:
                    if not found:
                        if '/' in name:
                            name = name.split('/')
                            name = name[0] + '/' + name[-1][:4]
                        else:
                            name = name[:12]
                        keyboard_write_pd(flt_num, flt_date, '1 %s' % name, cabin_class='', station=station)
                        # text = copy_text(x_start, y_start, x_end, y_end)
                        # if text_find_index(text):
                        #     _, end_index = text_find_index(text)
                        #     for i in range(1, int(end_index) + 1):
                        i = 1
                        while True:
                            keyboard_write_pr(i)
                            text = copy_text(x_start, y_start, x_end, y_end)
                            if text_has_number(text):
                                ics_data = ics_data_collector.details_extract(text)
                                if ics_data:
                                    if ticket == ics_data['tkt']:
                                        label = 'CKIN ' + label
                                        if ics_data['bn'] != '':
                                            keyboard_write_pu(label)
                                        else:
                                            keyboard_write_pre_pu(label)
                                        found = True
                                        break
                                i += 1
                            else:
                                break
                    else:
                        break
                if found:
                    data.loc[index_, '已查'] = '是'
                else:
                    data.loc[index_, '已查'] = '该客票未能提取旅客'
            else:
                data.loc[index_, '已查'] = '未备注'
    # except:
    #     pass
    finally:
        save_data(data, file_path)


if __name__ == "__main__":
    # try:
    alert_box('欢迎使用本程序', '欢迎')
    data, picked_data, file_path = get_data()
    picked_data = describe_data(picked_data)
    app_path = config.get('app', 'app_path')
    title_keyword = config.get('app', 'title_keyword')
    window_object = activate_app(app_path, title_keyword)
    activate_window(window_object)
    maximize_window(window_object)
    x_start, y_start, x_end, y_end = adjust_location()
    switch_input_language()
    login_ics(x_start, y_start, x_end, y_end)
    labelling(data, picked_data, file_path)
    alert_box('备注完毕，结果请查看%s文件，感谢使用！' % file_path, '退出程序')
    # except:
    #     alert_box('程序出现问题，正在退出程序，感谢使用！', '退出程序')
    # finally:
    #     if 'window_object' in locals():
    #         choice = yes_no_box('是否关闭ICS应用？', '退出程序')
    #         if choice == '是':
    #             keyboard_write_so()
    #             close_window(window_object)
