#!/usr/bin/python3
# -*- coding: utf-8 -*-

# 爬取台灣證券交易所的股價資料
# 「每日收盤行情(全部)」會過濾掉權證、ETF等資料。
# https://www.twse.com.tw/zh/trading/historical/mi-index.html
# 可參考這篇文章：Python 爬蟲教學 - 股票價格資料收集
# https://www.peteryangblog.com/posts/python-data-collecting-stock-price



import pandas as pd
import requests
from datetime import datetime, timedelta
import time


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
    url = f'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?date={target_date}&type=ALL&response=csv'
    # linux headers
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    # windows headers
    #headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    res = requests.get(url, headers=headers)
    return res.text
    #return res.json()


def parse_stock_data(data):
    """解析抓取到的股價資料"""
    """data 每行都帶有換行符號。一共有 8 種資料，分別是：
       "113年08月26日 價格指數(臺灣證券交易所)"\r\n
       "指數","收盤指數","漲跌(+/-)","漲跌點數","漲跌百分比(%)","特殊處理註記",\r\n
       "寶島股價指數","25,316.80","+","69.15","0.27","",\r\n

       "價格指數(跨市場)"\r\n
       "指數","收盤指數","漲跌(+/-)","漲跌點數","漲跌百分比(%)","特殊處理註記",\r\n
       "臺灣生技指數","4,432.91","+","13.57","0.31","",\r\n
       
       "價格指數(臺灣指數公司)"\r\n
       "指數","收盤指數","漲跌(+/-)","漲跌點數","漲跌百分比(%)","特殊處理註記",\r\n
       "金融類日報酬兩倍指數","45,989.65","+","1,711.79","3.87","",\r\n
       
       "報酬指數(臺灣證券交易所)"\r\n
       "報酬指數","收盤指數","漲跌(+/-)","漲跌點數","漲跌百分比(%)","特殊處理註記",\r\n
       "寶島股價報酬指數","37,488.37","+","105.88","0.28","",\r\n
       
       "報酬指數(跨市場)"\r\n
       "報酬指數","收盤指數","漲跌(+/-)","漲跌點數","漲跌百分比(%)","特殊處理註記",\r\n
       "臺灣生技報酬指數","5,051.48","+","15.47","0.31","",\r\n
       
       "報酬指數(臺灣指數公司)"\r\n
       "報酬指數","收盤指數","漲跌(+/-)","漲跌點數","漲跌百分比(%)","特殊處理註記",\r\n
       "漲升股利150報酬指數","14,916.44","+","14.95","0.10","",\r\n
       
       "113年08月26日 大盤統計資訊"\r\n
       "成交統計","成交金額(元)","成交股數(股)","成交筆數",\r\n
       "1.一般股票","327,866,736,955","4,929,843,433","2,212,981",\r\n
       
       "漲跌證券數合計"\r\n
       "類型","整體市場","股票",\r\n
       "上漲(漲停)","6,905(38)","539(15)",\r\n
       "備註:"\r\n
       ""漲跌價差"為當日收盤價與前一日收盤價比較。",\r\n
       
       "113年08月26日 每日收盤行情(全部)"\r\n
       "(元,股)",,,,,,,,,,,"(元,交易單位)",,,,,\r\n
       "證券代號","證券名稱","成交股數","成交筆數","成交金額","開盤價","最高價","最低價","收盤價","漲跌(+/-)","漲跌價差","最後揭示買價","最後揭示買量","最後揭示賣價","最後揭示賣量","本益比",\r\n
       ="0050","元大台灣50","11,798,725","13,941","2,149,783,996","182.40","183.40","180.80","181.25","+","0.30","181.20","4","181.25","1","0.00",\r\n
    """
    s_data = data.split('\n')  # 以換行符號分割資料
    output = []
    for d in s_data:
        _d = d.split('","') # 以(",")分割資料
        length = len(_d)   # 計算分割後的長度
        symbol = _d[0]   # 取得第一個元素

        # 「每日收盤行情(全部)」的資料特性是有 16 個欄位，且第一個元素不是以「=」開頭來過濾掉權證、ETF等資料。
        if length == 16 and not symbol.startswith('='):
            # 去掉每個元素中的 ",\r 和所有的雙引號 "，然後將結果添加到 output 列表中。
            output.append([
                ele.replace('",\r','').replace('"','') 
                for ele in _d
            ])
    return output


def save_to_csv(output, date, file_name='stock_data.csv'):
    """將資料轉成 DataFrame 並存成 csv 檔，檔名包含日期"""
    df = pd.DataFrame(output[1:], columns=output[0])
    dated_file_name = f"{file_name.split('.')[0]}_{date}.csv"
    df.to_csv(dated_file_name, index=False)


def save_raw_data_to_csv(output, date, file_name='stock_data_rawData.csv'):
    """將資料存成 csv 檔"""
    dated_file_name = f"{file_name.split('.')[0]}_{date}.csv"
    with open(dated_file_name, 'w') as f:
        for d in output:
            #f.write(d + '\n')      # 這樣寫會變成每個字元都換行
            f.write(d)


def main():
    # 設定開始日期、結束日期，若為 None 則取今天的日期
    #start_date = '20240826'
    #end_date = '20240826'
    start_date = None  
    end_date = None  
    date_range = get_date_range(start_date, end_date)
    
    #all_data = []
    for target_date in date_range:
        data = fetch_stock_data(target_date)
        output = parse_stock_data(data)
        #all_data.extend(output[1:])  # 合併所有日期的資料
    
        if output:
            save_to_csv(output, target_date)  # 保存每個日期的資料
            save_raw_data_to_csv(data, target_date)

            print(f"Save data of {target_date} to csv file.")

        time.sleep(5)  # 每次抓取資料後休息 5 秒 (避免被擋)


if __name__ == "__main__":
    main()
