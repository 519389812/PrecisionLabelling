import pandas as pd

from window_handler import *
import ics_data_collector
import ticket_data_collector
from settings import *
from common_func import *
import pypinyin
from itertools import product
import driver_handler
import gsms_handler
import etmanage_handler
import shutil


def create_new_columns(data, args):
    for column in args:
        if column not in data.columns:
            data[column] = ''
    return data


def combine_columns(data):
    if '近一年购买升舱次数' not in data.columns:
        data['近一年购买升舱次数'] = data['近一年购买登机口升舱次数'] + data['近一年购买候补升舱次数'] + data['近一年购买休息室升舱次数']
    if '近三月到期里程' not in data.columns:
        data['近三月到期里程'] = data['本月到期里程'] + data['下月到期里程'] + data['下下月到期里程']
    return data


def get_data():
    while True:
        file_path = open_file_box('选择数据文件', './task', [('csv文件', '.csv')])
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
        if data.shape[0] == 0:
            select = yes_no_box('所选文件无数据。是否重新选择文件？', '无数据')
            if select == "是":
                continue
            else:
                os._exit(0)
        data.replace('\t', '', regex=True, inplace=True)
        data['飞行日期'] = pd.to_datetime(data['飞行日期']).dt.strftime('%Y-%m-%d')
        data.fillna('', inplace=True)
        data = combine_columns(data)
        data = create_new_columns(data, additional_data_columns + labels)
        data = reset_columns(data, labels)
        return data, file_path


def save_data(data, file_path):
    data['会员卡号'] = data['会员卡号'].apply(lambda x: '\t' + x)
    data['OC航班号'] = data['OC航班号'].apply(lambda x: '\t' + x)
    data['电子客票号'] = data['电子客票号'].apply(lambda x: '\t' + x)
    data.to_csv(file_path, index=False)


def get_target_index(data, date):
    target_index = data[(data['客票状态'] == 'O') & (data['OC承运人'] == 'CZ') & (data['飞行日期'] == date) & data['航段始发机场'].isin(client_stations) == True].index
    if len(target_index) == 0:
        alert_box('无符合条件数据，程序退出。', '无数据')
        os._exit(0)
    return target_index


def pick_data(data, target_index):
    data.replace('\t', '', regex=True, inplace=True)
    target_data = data.loc[target_index, :]
    picked_data = target_data[(target_data['LCSCJ'] == '是') | (target_data['LCSCF'] == '是') | (target_data['LCGQ'] == '是') | (target_data['XFSC'] == '是') | (target_data['XFDZ'] == '是') | (target_data['PJBMG'] == '是') | (target_data['XLPS'] == '是') | (target_data['BX'] == '是') | (target_data['TS'] == '是')]
    return picked_data


def reset_init_status(data, picked_data, target_index, file_path):
    data.loc[target_index.difference(picked_data.index), '查询'] = '非标签旅客'
    data.loc[target_index.difference(picked_data.index), '备注'] = '非标签旅客'
    data.loc[picked_data[picked_data['查询'] == '非标签旅客'].index, '查询'] = ''
    data.loc[picked_data[picked_data['备注'] == '非标签旅客'].index, '备注'] = ''
    save_data(data, file_path)
    return data


def describe_data(picked_data, comment_only):
    num_of_data = picked_data.shape[0]
    if not comment_only:
        unhandled_data = picked_data[(picked_data['查询'] == '') | ((picked_data['查询'] == '是') & (picked_data['备注'] == ''))]
    else:
        unhandled_data = picked_data[(picked_data['备注'] == '') & (picked_data['姓名'] != '') & (picked_data['航段始发机场'].isin(client_auth_stations) == True)]
    if unhandled_data.shape[0] == 0:
        alert_box('筛选出符合条件的数据 %d 条，所有数据已经处理完毕，程序退出' % num_of_data, '完毕')
        os._exit(0)
    else:
        alert_box('筛选出符合条件的数据 %d 条，其中已处理的数据有 %d 条，未处理的数据有 %d 条。' % (num_of_data, num_of_data - unhandled_data.shape[0], unhandled_data.shape[0]), '概况')
        return unhandled_data


def reset_columns(data, args):
    for column in args:
        data[column] = ''
    return data


def labelling_matched_data(data, target_index):
    target_data = data.loc[target_index, :]
    for city_pair in list(upgrade_miles.index):
        index_ = target_data[((target_data['OC实际母舱位'] == 'Y') | (target_data['OC实际母舱位'] == 'W')) & (target_data['航段'] == city_pair) & (target_data['可用里程余额'] >= upgrade_miles.loc[city_pair, 'miles_y_to_j'])].index
        data.loc[index_, 'LCSCJ'] = '是'
        if upgrade_miles.loc[city_pair, 'miles_j_to_f'] != 0:
            index_ = target_data[(target_data['OC实际母舱位'] == 'J') & (target_data['航段'] == city_pair) & (target_data['可用里程余额'] >= upgrade_miles.loc[city_pair, 'miles_j_to_f'])].index
            data.loc[index_, 'LCSCF'] = '是'
            index_ = target_data[((target_data['OC实际母舱位'] == 'Y') | (target_data['OC实际母舱位'] == 'W')) & (target_data['航段'] == city_pair) & (target_data['可用里程余额'] >= upgrade_miles.loc[city_pair, 'miles_y_to_f'])].index
            data.loc[index_, 'LCSCF'] = '是'
            index_ = target_data[(target_data['近一年购买升舱次数'] == 'J') & (target_data['航段'] == city_pair)].index
            data.loc[index_, 'XFSC'] = '是'
    index_ = target_data[(target_data['航段性质'] == '国内') & ((target_data['OC实际母舱位'] == 'Y') | (target_data['OC实际母舱位'] == 'W')) & (target_data['OC实际子舱位'] != 'X') & (target_data['可用里程余额'] >= upgrade_miles.loc['OTHER-OTHER', 'miles_y_to_j'])].index
    data.loc[index_, 'LCSCJ'] = '是'
    index_ = target_data[target_data['近三月到期里程'] >= 6000].index
    data.loc[index_, 'LCGQ'] = '是'
    index_ = target_data[(target_data['近一年购买升舱次数'] > 0) & ((target_data['OC实际母舱位'] == 'Y') | (target_data['OC实际母舱位'] == 'W')) & (target_data['OC实际子舱位'] != 'X') & (target_data['航段性质'] == '国内')].index
    data.loc[index_, 'XFSC'] = '是'
    index_ = target_data[(target_data['近一年购买升舱次数'] > 0) & ((target_data['OC实际母舱位'] == 'Y') | (target_data['OC实际母舱位'] == 'W')) & (target_data['航段性质'] != '国内')].index
    data.loc[index_, 'XFSC'] = '是'
    index_ = target_data[(target_data['近一年购买一人多座次数'] > 0)].index
    data.loc[index_, 'XFDZ'] = '是'
    index_ = target_data[target_data['差旅类票价不敏感旅客'] == '是'].index
    data.loc[index_, 'PJBMG'] = '是'
    return data


def create_label(row):
    label = 'CKIN '
    for l in labels:
        if row[l] == '是':
            label += l + ' '
    return label


def check_or_comment(data, picked_data, file_path, comment_only):
    try:
        for index_, row in picked_data.iterrows():
            label = create_label(row)
            station = row['航段始发机场']
            flt_num = row['OC承运人'] + row['OC航班号']
            flt_date = row['飞行日期']
            flt_date = change_ics_date_format(flt_date)
            ticket = row['电子客票号']
            if not comment_only:
                if row['姓名'] == '':
                    keyboard_write_etkd(ticket)
                    text = copy_text(x_start, y_start, x_end, y_end)
                    if not text_has_ticket(text):
                        data.loc[index_, '查询'] = '未能提取客票'
                        data.loc[index_, '备注'] = '未能提取旅客'
                        continue
                    ticket_data = ticket_data_collector.details_extract(text)
                    if ticket_data:
                        if ticket_data['first_name'] != '':
                            pax_name = ticket_data['last_name'] + '/' + ticket_data['first_name']
                        else:
                            pax_name = ticket_data['last_name']
                    else:
                        data.loc[index_, '查询'] = '客票信息提取异常'
                        data.loc[index_, '备注'] = '未能提取旅客'
                        continue
                    data.loc[index_, '姓名'] = pax_name
                    data.loc[index_, '查询'] = '是'
            else:
                pax_name = row['姓名']
            if station in client_auth_stations:
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
                    data.loc[index_, '备注'] = '是'
                else:
                    data.loc[index_, '备注'] = '未能提取旅客'
            else:
                data.loc[index_, '查询'] = '非用户所在场站'
    # except:
    #     pass
    finally:
        save_data(data, file_path)


def login_etmanage(driver):
    session = driver_handler.new_session()
    while True:
        etmanage_handler.login_by_headless(driver, session)
        if etmanage_handler.is_login(session):
            break
        else:
            choice = yes_no_box('登录emg失败，是否重新登录？', 'emg登录')
            if choice == '是':
                continue
            else:
                alert_box('您正在退出程序，感谢使用', '退出程序')
                os._exit(0)


def login_gsms(driver):
    session = driver_handler.new_session()
    while True:
        gsms_handler.login_by_headless(driver, session)
        if gsms_handler.is_login(session):
            break
        else:
            choice = yes_no_box('登录gsms失败，是否重新登录？', 'gsms登录')
            if choice == '是':
                continue
            else:
                alert_box('您正在退出程序，感谢使用', '退出程序')
                os._exit(0)


def get_download_pax_flt_list(data, date):
    data = data[(data['客票状态'] == 'O') & (data['OC承运人'] == 'CZ') & (data['飞行日期'] == date) & (data['航段性质'] == '国际')]
    data = data.drop_duplicates(['OC航班号'])
    flt_list = data[['OC航班号', '飞行日期']]
    return flt_list


def download_pax(flt_list):
    pax = pd.DataFrame(None)
    if flt_list.shape[0] > 0:
        need_close_driver = False
        try:
            for _, flt in flt_list.iterrows():
                if not os.path.exists('%s%s%s_%s.xls' % (pax_dir, os.sep, flt['飞行日期'], flt['OC航班号'])):
                    if 'driver' not in locals():
                        driver = driver_handler.new_driver('FireFox', pax_temporary_dir)
                        need_close_driver = True
                        login_etmanage(driver)
                        break
            for _, flt in flt_list.iterrows():
                if not os.path.exists('%s%s%s_%s.xls' % (pax_dir, os.sep, flt['飞行日期'], flt['OC航班号'])):
                    etmanage_handler.call_pax_list(driver, flt['OC航班号'], flt['飞行日期'])
                    rename_last_downloaded_file(pax_temporary_dir, pax_dir, '%s_%s.xls' % (flt['飞行日期'], flt['OC航班号']))
                pax_per_flt = pd.read_html('%s%s%s_%s.xls' % (pax_dir, os.sep, flt['飞行日期'], flt['OC航班号']), encoding='gbk')[0]
                pax_per_flt.rename(columns=pax_per_flt.loc[1], inplace=True)
                pax_per_flt.drop([0, 1], inplace=True)
                pax_per_flt.reset_index(drop=True, inplace=True)
                pax_per_flt['票号'] = pax_per_flt['票号'].str.replace('-', '')
                pax_per_flt['旅客证件'] = pax_per_flt['旅客证件'].str.split(':').str[-1]
                pax = pd.concat([pax, pax_per_flt], ignore_index=True, join='outer')
        finally:
            if need_close_driver:
                driver_handler.close_driver(driver)
        pax.dropna(subset=['旅客证件'], inplace=True)
    return pax


def rename_last_downloaded_file(temporary_dir, destination_dir, new_file_name, time_out=60):

    def get_last_downloaded_file_path(temporary_dir):
        count = 0
        while not os.listdir(temporary_dir):
            time.sleep(1)
            count = count_time(count)
        return max([os.path.join(temporary_dir, f) for f in os.listdir(temporary_dir)], key=os.path.getctime)

    def count_time(count):
        count += 1
        if count > time_out:
            alert_box('下载文件失败，请检查网络连接', '错误')
            os._exit(0)
        return count

    count = 0
    while '.part' in get_last_downloaded_file_path(temporary_dir):
        time.sleep(1)
        count = count_time(count)
    shutil.move(get_last_downloaded_file_path(temporary_dir), os.path.join(destination_dir, new_file_name))


def labelling_matched_data_local(data, pax):
    if pax.shape[0] > 0:
        # pax 票号、旅客姓名、旅客证件
        pax.drop(columns=['票联', '旅客类型', '票价', '舱位', '航段', '航段状态', 'I标识', 'D标识', '票价计算', '联系方式', '出票渠道', '代理人编码'], inplace=True)
        ins = pd.read_excel('%s%sINS.xlsx' % (source_dir, os.sep), sheet_name='sheet1', header=0, index_col=0)
        # dly = pd.read_excel('%s%sDLY.xlsx' % (source_dir, os.sep), sheet_name='sheet1', header=0, index_col=0)
        dmg = pd.read_excel('%s%sDMG.xlsx' % (source_dir, os.sep), sheet_name='sheet1', header=0, index_col=0)
        com = pd.read_excel('%s%sCOM.xlsx' % (source_dir, os.sep), sheet_name='sheet1', header=0, index_col=0)

        pax = pd.merge(pax, dmg['证件号'].to_frame().dropna(), how='left', left_on='旅客证件', right_on='证件号').drop_duplicates()
        # pax = pd.merge(pax, dly['证件号'].to_frame().dropna(), left_on='Ppt', right_on='证件号').drop_duplicates()
        pax = pd.merge(pax, ins['被保险人证件号码'].to_frame().dropna(), how='left', left_on='旅客证件', right_on='被保险人证件号码').drop_duplicates()
        pax = pd.merge(pax, com['护照号'].to_frame().dropna(), how='left', left_on='旅客证件', right_on='护照号').drop_duplicates()
        data = pd.merge(data, pax, left_on='电子客票号', right_on='票号', how='left')
        data.fillna('', inplace=True)
        index_ = data[data['证件号'] != ''].index
        data.loc[index_, 'XLPS'] = '是'
        index_ = data[data['被保险人证件号码'] != ''].index
        data.loc[index_, 'BX'] = '是'
        index_ = data[data['护照号'] != ''].index
        data.loc[index_, 'TS'] = '是'
        index_ = data[data['旅客姓名'] != ''].index
        data.loc[index_, '姓名'] = data.loc[index_]['旅客姓名']
        data.drop(columns=['证件号', '被保险人证件号码', '护照号', '票号', '旅客姓名', '旅客证件'], inplace=True)
        index_ = data[(data['客票状态'] == 'O') & ((data['XLPS'] != '') | (data['BX'] != '') | (data['TS'] != '') | (data['LCSCJ'] != '') | (data['LCSCF'] != '') | (data['XFSC'] != '') | (data['LCGQ'] != '') | (data['XFDZ'] != '') | (data['PJBMG'] != '')) & (data['姓名'] != '')].index
        data.loc[index_, '查询'] = '是'
    return data


if __name__ == "__main__":
    date = get_date()
    if not app_path or not client_auth_stations:
        alert_box('欢迎使用本程序！首次使用请根据提示进行初始化设置。', '欢迎')
        set_app_path()
        set_ics_auth_station()
        config = reload_config()
        app_path = reload_config_value('app', 'app_path')
        client_auth_stations = reload_config_client_station('client', 'auth')
    data, file_path = get_data()
    flt_list = get_download_pax_flt_list(data, date)
    pax = download_pax(flt_list)
    target_index = get_target_index(data, date)
    data = labelling_matched_data(data, target_index)
    data = labelling_matched_data_local(data, pax)
    picked_data = pick_data(data, target_index)
    data = reset_init_status(data, picked_data, target_index, file_path)
    picked_data = pick_data(data, target_index)
    picked_data = describe_data(picked_data, comment_only)
    window_object = activate_app(app_path, title_keyword)
    activate_window(window_object)
    maximize_window(window_object)
    x_start, y_start, x_end, y_end = adjust_location()
    switch_input_language()
    login_ics(x_start, y_start, x_end, y_end)
    check_or_comment(data, picked_data, file_path, comment_only)
    alert_box('备注完毕，结果请查看%s文件，感谢使用！' % file_path, '退出程序')
    # except:
    #     alert_box('程序出现问题，正在退出程序，感谢使用！', '退出程序')
    # finally:
    #     if 'window_object' in locals():
    #         choice = yes_no_box('是否关闭ICS应用？', '退出程序')
    #         if choice == '是':
    #             keyboard_write_so()
    #             close_window(window_object)
