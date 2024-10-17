#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# 臺灣證券交易所 OpenAPI V1.0
# https://openapi.twse.com.tw/
#
# API 分類：公司治理
# API Name：​/opendata​/t187ap46_L_9
# 上市公司企業ESG資訊揭露彙總資料-功能性委員會
#
# https://openapi.twse.com.tw/#/公司治理/get_opendata_t187ap46_L_9
#


import requests
import datetime


# 上市公司企業ESG資訊揭露彙總資料-功能性委員會
# requests.Get
# Parameters：No parameters
# Responses： Code =	200	
# {
#   "出表日期": "string",
#   "報告年度": "string",
#   "公司代號": "string",
#   "公司名稱": "string",
#   "薪酬委員會席次": "string",
#   "薪酬委員會獨立董事席次": "string",
#   "薪酬委員會出席率": "string",
#   "審計委員會席次": "string",
#   "審計委員會出席率": "string"
#   }
#
# 傳入參數:
#   headers: headers
#   AD: 轉成西元年
def get_opendata_t187ap46_L_9(headers:str, AD:bool=True) -> list:

    base_url = r'https://openapi.twse.com.tw/v1'
    api_name = r'/opendata/t187ap46_L_9'

    res = requests.get(url=f'{base_url}{api_name}', headers=headers, timeout=10)  

    if res.status_code != requests.codes.ok: 
        print('Error: ', res.status_code)
        return

    # 試著印出第一筆資料
    # print(res.json()[0])

    json = res.json()

    # 不需要轉成西元年
    if not AD:
        return json

    for j in json:
        # '出表日期': '1130711'
        year , month, day = j['出表日期'][0:3], j['出表日期'][3:5], j['出表日期'][5:]
        year = int(year) + 1911 
        j["出表日期"] = datetime.datetime.strptime(f'{year}/{month}/{day}', '%Y/%m/%d').date()
        # '報告年度': '112'
        year = int(j['報告年度']) + 1911
        j["報告年度"] = f'{year}'


    return json


if __name__ == '__main__':

    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    json = get_opendata_t187ap46_L_9(headers)
    # 不轉成西元年
    # json = get_opendata_t187ap46_L_9(headers, AD=False)

    print('API Name : t187ap46_L_9')
    print('上市公司企業ESG資訊揭露彙總資料-功能性委員會')
    print('資料筆數: ', len(json))

    # 印出公司名稱為 '聯發科' 或 '台積電' 的資料
    for j in json:
        # 印出所有
        # print(j['公司代號'], j['公司名稱'], j['出表日期'])
        # print('---')

        if j['公司名稱'] == '聯發科' or j['公司名稱'] == '台積電':
            print(j)

