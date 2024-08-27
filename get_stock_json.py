#!/usr/bin/python3
# -*- coding: utf-8 -*-

# 爬取台灣證券交易所的股價資料
# 資料來源是「台灣證券交易所」的「每日收盤行情」，分類「全部」
# https://www.twse.com.tw/zh/trading/historical/mi-index.html
# 爬取格式為 JSON 格式，並解析資料後存成 csv 檔
# 還沒找過濾掉權證、ETF等資料的方法。


import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import json
import re


def get_date_range(start_date=None, end_date=None):
    """取得日期範圍內的所有日期，若參數為空則取今天的日期"""
    if start_date is None or end_date is None:
        today = datetime.now().strftime('%Y%m%d')
        return [today]
    
    start = datetime.strptime(start_date, '%Y%m%d')
    end = datetime.strptime(end_date, '%Y%m%d')
    date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]
    return [date.strftime('%Y%m%d') for date in date_generated]


def fetch_stock_data(target_date):
    """根據目標日期抓取股價資料"""
    """資料來源是「台灣證券交易所」的「每日收盤行情」，分類「全部」"""
    url_json = f'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={target_date}&type=ALL&response=json'
    # linux headers
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    # windows headers
    #headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    res = requests.get(url_json, headers=headers)
    return res.json()


def parse_stock_data(data):
    """解析抓取到的股價資料"""
    """
    data 是 dict (json)
    data.keys() = dict_keys(['tables', 'params', 'stat', 'date'])

    data['tables'] 是一個 list，裡面有 8 個 dict，每個 dict 代表一個表格

    [
      { 'title': '113年08月23日 價格指數(臺灣證券交易所)', 
        'fields': ['指數', '收盤指數', '漲跌(+/-)', '漲跌點數', '漲跌百分比(%)', '特殊處理註記'], 
        'data': [['寶島股價指數', '25,247.65', "<p style ='color:red'>+</p>", '25.30', '0.10', ''], .... ], 
        'hints': '單位：元、股' }, 

      { 'title': '價格指數(跨市場)', 
        'fields': ['指數', '收盤指數', '漲跌(+/-)', '漲跌點數', '漲跌百分比(%)', '特殊處理註記'], 
        'data': [['臺灣生技指數', '4,419.34', "<p style ='color:green'>-</p>", '17.06', '-0.38', ''], .... ] }, 

      { 'title': '價格指數(臺灣指數公司)', 
        'fields': ['指數', '收盤指數', '漲跌(+/-)', '漲跌點數', '漲跌百分比(%)', '特殊處理註記'], 
        'data': [['金融類日報酬兩倍指數', '44,277.86', "<p style ='color:red'>+</p>", '53.95', '0.12', ''], ....  ] }, 
    
      { 'title': '報酬指數(臺灣證券交易所)', 
        'fields': ['報酬指數', '收盤指數', '漲跌(+/-)', '漲跌點數', '漲跌百分比(%)', '特殊處理註記'], 
        'data': [['寶島股價報酬指數', '37,382.49', "<p style ='color:red'>+</p>", '39.20', '0.10', ''], ....  ] }, 

      { 'title': '報酬指數(跨市場)', 
        'fields': ['報酬指數', '收盤指數', '漲跌(+/-)', '漲跌點數', '漲跌百分比(%)', '特殊處理註記'], 
        'data': [['臺灣生技報酬指數', '5,036.01', "<p style ='color:green'>-</p>", '19.29', '-0.38', ''], ....  ] }, 

      { 'title': '報酬指數(臺灣指數公司)', 
        'fields': ['報酬指數', '收盤指數', '漲跌(+/-)', '漲跌點數', '漲跌百分比(%)', '特殊處理註記'], 
        'data': [['漲升股利150報酬指數', '14,901.49', "<p style ='color:red'>+</p>", '3.39', '0.02', ''], ....  ] },

      { 'title': '113年08月23日 大盤統計資訊', 
        'fields': ['成交統計', '成交金額(元)', '成交股數(股)', '成交筆數'], 
        'data': [['1.一般股票', '293,211,958,389', '4,332,930,403', '2,004,390'], ....  ],
        'hints': '單位：元、股' },

      { 'title': '漲跌證券數合計', 
        'fields': ['類型', '整體市場', '股票'], 
        'data': [['上漲(漲停)', '4,730(28)', '503(10)'], ['下跌(跌停)', '5,880(37)', '388(0)'], ....  ],
        'notes': ['"漲跌價差"為當日收盤價與前一日收盤價比較。', ... '] },

      { 'title': '113年08月23日 每日收盤行情(全部)', 
        'fields': ['證券代號', '證券名稱', '成交股數', '成交筆數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌(+/-)', '漲跌價差', '最後揭示買價', '最後揭示買量', '最後揭示賣價', '最後揭示賣量', '本益比'], 
        'data': [['0050', '元大台灣50', '8,316,460', '11,394', '1,497,506,580', '179.00', '181.35', '178.90', '180.95', '<p style= color:red>+</p>', '0.10', '180.90', '12', '180.95', '97', '0.00'], ..... ],
        'hints': '單位：元、股', 
        'groups': [{'start': 0, 'span': 11, 'title': '(元,股)'}, {'start': 11, 'span': 5, 'title': '(元,交易單位)'}], 
        'notes': ['漲跌(+/-)欄位符號說明:+/-/X表示漲/跌/不比價。', ....] },

      {}
    ]
    """
    """篩選出 title 包含 '每日收盤行情' 的項目"""
    filtered_tables = []
    fields = []
    data_list = []

    filtered_tables = [
        table for table in data['tables'] 
        if '每日收盤行情' in table.get('title', '')
    ]

    if filtered_tables:
        fields = filtered_tables[0]['fields']
        data_list = filtered_tables[0]['data']

        # 清理 data_list 中的 HTML 標籤 '<p style= color:red>+</p>'
        for row in data_list:
            for i in range(len(row)):
                row[i] = clean_html_tags(row[i])
                row[i] = remove_commas(row[i])

    return fields, data_list


def save_to_csv(data_list, fields, date, file_name='stock_data.csv'):
    """將資料轉成 DataFrame 並存成 csv 檔，檔名包含日期"""
    df = pd.DataFrame(data_list, columns=fields)
    dated_file_name = f"{file_name.split('.')[0]}_{date}.csv"
    df.to_csv(dated_file_name, index=False)


def save_raw_data_to_json(data, target_date):
    """保存原始數據到 JSON 文件"""
    filename = f"stock_raw_data_{target_date}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def clean_html_tags(text):
    """移除 HTML 標籤"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def remove_commas(text):
    """移除數字中的逗號"""
    return text.replace(',', '')


def main():
    start_date = None  # 設定開始日期，若為 None 則取今天的日期
    end_date = None  # 設定結束日期，若為 None 則取今天的日期
    #start_date = '20240826' # 設定開始日期，若為 None 則取今天的日期
    #end_date = '20240826'  # 設定結束日期，若為 None 則取今天的日期
    date_range = get_date_range(start_date, end_date)
    
    #all_data = []
    for target_date in date_range:
        data = fetch_stock_data(target_date)
        fields, data_list = parse_stock_data(data)
    
        if data_list:
            save_to_csv( data_list, fields, target_date)  # 保存每個日期的資料
            save_raw_data_to_json(data, target_date)

            print(f"Save data of {target_date} to csv file.")

        time.sleep(5)  # 每次抓取資料後休息 5 秒 (避免被擋)


if __name__ == "__main__":
    main()
