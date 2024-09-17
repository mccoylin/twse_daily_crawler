#!/usr/bin/python3
# -*- coding: utf-8 -*-


# 取自網路上的教學文章
# Python爬取公開資訊觀測站資料
# https://medium.com/@norahsu/python%E7%88%AC%E5%8F%96%E5%85%AC%E9%96%8B%E8%B3%87%E8%A8%8A%E8%A7%80%E6%B8%AC%E7%AB%99%E8%B3%87%E6%96%99-4fc13d3b587a
#
# 文章裡可以看到如何爬取公開資訊觀測站的資料。
#
# 待解決問題：
# [Running] /usr/bin/python3 "/home/mccoy/working_copy/github/twse_daily_crawler/tempCodeRunnerFile.python"
# tempCodeRunnerFile.python:32: FutureWarning: Passing literal html to 'read_html' is deprecated and will be removed in a future version. To read from a literal string, wrap it in a 'StringIO' object.
#   html_df = pd.read_html(r.text)[3].fillna("")


import requests
import pandas as pd
import time


def get_data_df(url, stockNo):
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    #    url = "https://mops.twse.com.tw/mops/web/ajax_t05st09_2"
    #    stockNo = 2884
    form_data = {
            'encodeURIComponent': 1
            , 'step': 1
            , 'firstin': 1
            , 'off': 1
            , 'queryName': 'co_id'
            , 'inpuType': 'co_id'
            , 'TYPEK': all
            , 'isnew': False
            , 'co_id': stockNo
            , 'date1': 100
            , 'date2': 110
            , 'qryType': 1
            }

    r = requests.post(url, data=form_data, headers=headers ) 
    html_df = pd.read_html(r.text)[3].fillna("")
    return html_df


start_time = time.time()
df = get_data_df("https://mops.twse.com.tw/mops/web/ajax_t05st09_2", 2884)
end_time = time.time()
print(df)
print("Time: ", end_time - start_time)
