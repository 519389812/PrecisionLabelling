import pandas as pd
import os
from settings import task_dir, sales_dir
from box_body import date_box, alert_box


def create_date_list(start_date, end_date):
    date_list = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').to_list()
    return date_list


def get_st_data(date_list, start_date, end_date):
    if '%s_%s_st_total.csv' % (start_date, end_date) in os.listdir(task_dir):
        try:
            st_data = pd.read_csv('%s%s%s_%s_st_total.csv' % (task_dir, os.sep, start_date, end_date), encoding='gbk', converters={'会员卡号': str, '飞行日期': str, 'OC航班号': str, '电子客票号': str})
        except:
            st_data = pd.read_csv('%s%s%s_%s_st_total.csv' % (task_dir, os.sep, start_date, end_date), converters={'会员卡号': str, '飞行日期': str, 'OC航班号': str, '电子客票号': str})
        return st_data
    st_data = pd.DataFrame(None)
    files = os.listdir(task_dir)
    for date in date_list:
        for file in files:
            if date in file:
                try:
                    st_data_temp = pd.read_csv('%s%s%s' % (task_dir, os.sep, file), encoding='gbk', converters={'会员卡号': str, '飞行日期': str, 'OC航班号': str, '电子客票号': str})
                except:
                    st_data_temp = pd.read_csv('%s%s%s' % (task_dir, os.sep, file), converters={'会员卡号': str, '飞行日期': str, 'OC航班号': str, '电子客票号': str})
                st_data_temp.replace('\t', '', regex=True, inplace=True)
                st_data_temp['飞行日期'] = pd.to_datetime(st_data_temp['飞行日期']).dt.strftime('%Y-%m-%d')
                st_data_temp.fillna('', inplace=True)
                if st_data_temp is not None:
                    st_data = pd.concat([st_data, st_data_temp], ignore_index=True, join='outer')
                else:
                    continue
    if st_data.shape[0] == 0:
        alert_box('未提取到st数据', '错误')
        os._exit(0)
    st_data.fillna('', inplace=True)
    st_data.to_csv('%s%s%s_%s_st_total.csv' % (task_dir, os.sep, start_date, end_date))
    return st_data


def get_sales_data(start_date, end_date):
    if '%s_%s_sales_total.csv' % (start_date, end_date) in os.listdir(sales_dir):
        try:
            sales_data = pd.read_csv('%s%s%s_%s_sales_total.csv' % (sales_dir, os.sep, start_date, end_date), encoding='gbk', converters={'关联票号': str})
        except:
            sales_data = pd.read_csv('%s%s%s_%s_sales_total.csv' % (sales_dir, os.sep, start_date, end_date), converters={'关联票号': str})
        return sales_data
    sales_data = pd.DataFrame(None)
    for root, _, files in os.walk(sales_dir):
        for file in files:
            sales_data_temp = pd.read_excel(os.path.join(root, file), skiprows=3, converters={'关联票号': str})
            if sales_data_temp.shape[0] <= 4:
                alert_box('未提取到销售数据', '错误')
                os._exit(0)
            sales_data_temp.drop(sales_data_temp.head(2).index, inplace=True)
            sales_data = pd.concat([sales_data, sales_data_temp], ignore_index=True, join='outer')
    if sales_data.shape[0] == 0:
        alert_box('未提取到st数据', '错误')
        os._exit(0)
    sales_data.fillna('', inplace=True)
    sales_data.to_csv('%s%s%s_%s_sales_total.csv' % (sales_dir, os.sep, start_date, end_date))
    return sales_data


def compare_data(st_data, sales_data):
    data = pd.merge(st_data, sales_data, how='outer', left_on='电子客票号', right_on='关联票号')
    data.fillna('', inplace=True)
    data.to_csv('result.csv')
    return data


def describe_data(data):
    data_marked_count = data[(data['已查'] == '是') | (data['备注'] == '是')].shape[0]
    data_successful_count = data[((data['已查'] == '是') | (data['备注'] == '是')) & (data['关联票号'] != '')].shape[0]
    success_rate = data_successful_count / data_marked_count
    total_count = data[data['UID'] != ''].shape[0]
    total_sales_count = data[(data['UID'] != '') & (data['关联票号'] != '')].shape[0]
    total_sales_rate = total_sales_count / total_count
    with open('result.txt', 'w') as f:
        f.write('备注旅客数：%d\n备注旅客销售成功数：%d\n备注旅客销售成功率：%.2f\n\nst提取旅客总数：%d\nst提取旅客销售数：%d\nst提取旅客销售率：%.2f' % (data_marked_count, data_successful_count, success_rate, total_count, total_sales_count, total_sales_rate))


def main():
    start_date = date_box('请输入开始日期', '开始日期')
    end_date = date_box('请输入结束日期', '结束日期')
    date_list = create_date_list(start_date, end_date)
    if not date_list:
        alert_box('日期填写有误', '错误')
        os._exit(0)
    st_data = get_st_data(date_list, start_date, end_date)
    sales_data = get_sales_data(start_date, end_date)
    data = compare_data(st_data, sales_data)
    describe_data(data)


if __name__ == '__main__':
    main()
