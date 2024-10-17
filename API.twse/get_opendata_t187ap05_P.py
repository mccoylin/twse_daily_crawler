#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# 臺灣證券交易所 OpenAPI V1.0
# https://openapi.twse.com.tw/
#
# API 分類：公司治理
# API Name：​/opendata​/t187ap05_P
# 公開發行公司每月營業收入彙總表 
#
# https://openapi.twse.com.tw/#/公司治理/get_opendata_t187ap05_P


import requests
import datetime


# API Name：​/opendata​/t187ap05_P
# 公開發行公司每月營業收入彙總表
# Parameters： No parameters
# Responses： Code =	200	
# {
#   "出表日期": "string",
#   "資料年月": "string",
#   "公司代號": "string",
#   "公司名稱": "string",
#   "產業別": "string",
#   "營業收入-當月營收": "string",
#   "營業收入-上月營收": "string",
#   "營業收入-去年當月營收": "string",
#   "營業收入-上月比較增減(%)": "string",
#   "營業收入-去年同月增減(%)": "string",
#   "累計營業收入-當月累計營收": "string",
#   "累計營業收入-去年累計營收": "string",
#   "累計營業收入-前期比較增減(%)": "string",
#   "備註": "string"
# }
#
# 傳入參數。:
# base_url: API 網址
# headers: headers
# AD: 轉成西元年
def get_opendata_t187ap05_P(headers:str, AD:bool=True) -> dict:

    base_url = r'https://openapi.twse.com.tw/v1'
    api_name = r'/opendata/t187ap05_P'

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

    # 轉成西元年
    for j in json:
        # '出表日期': '1131016'
        year , month, day = j['出表日期'][0:3], j['出表日期'][3:5], j['出表日期'][5:]
        year = int(year) + 1911 
        j["出表日期"] = datetime.datetime.strptime(f'{year}/{month}/{day}', '%Y/%m/%d').date()

        # '資料年月': '11309 
        year , month = j['資料年月'][0:3], j['資料年月'][3:]
        j["資料年月"] = f'{(int(year) + 1911)}-{month}'
        # print(j)


    return json


if __name__ == '__main__':

    # 使用範例
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }

    json = get_opendata_t187ap05_P(headers)
    # 不需要轉成西元年
    # json = get_opendata_t187ap05_P(headers, AD=False)

    print('API Name : t187ap05_P')
    print('公開發行公司每月營業收入彙總表')
    print(f'資料筆數: {len(json)}')

    for j in json:
        # 印出所有
        print(f"{j['公司代號']}, {j['公司名稱']}, {j['資料年月']}, {j['營業收入-當月營收']}")
        print('---')

        # 印出公司名稱為 '聯發科' 或 '台積電' 的資料
        if j['公司名稱'] == '聯發科' or j['公司名稱'] == '台積電':
            print(j)


