#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# 臺灣證券交易所 OpenAPI V1.0
# https://openapi.twse.com.tw/
#
# API 分類：公司治理
# API Name：​suspendListingCsvAndHtml
# 終止上市公司
# 
#
# https://openapi.twse.com.tw/#/公司治理/get_company_suspendListingCsvAndHtml
#


import requests
import datetime 


# API Name：​suspendListingCsvAndHtml
# 終止上市公司
# requests.Get
# Parameters：No parameters
# Responses： Code =	200	
# {
#   "DelistingDate": "string",
#   "Company": "string",
#   "Code": "string"
# }
#
# Responses headers:  
#     connection: keep-alive  content-disposition: attachment;filename=suspendListingCsvAndHtml.json  content-encoding: gzip  content-type: application/json  date: Wed, 16 Oct 2024 20:41:25 GMT  etag: W/"670edc91-43b1"  last-modified: Tue, 15 Oct 2024 21:20:17 GMT  server: nginx  transfer-encoding: chunked 
#
# 傳入參數:
#   headers: headers
#   AD: 轉成西元年
def get_company_suspendListingCsvAndHtml(headers:str, AD:bool=True) -> list:

    base_url = r'https://openapi.twse.com.tw/v1'
    api_name = r'/opendata/suspendListingCsvAndHtml'

    res = requests.get(url=f'{base_url}{api_name}', headers=headers, timeout=10)  

    if res.status_code != requests.codes.ok: 
        print('Error: ', res.status_code)
        return

    # 試著印出第一筆資料
    # print(res.json()[0])

    #  如果有需要，另行處理 headers
    print(res.headers)

    json = res.json()

    for j in json:
        # 轉成西元年 
        year , month, day = j['DelistingDate'].split('/')
        year = int(year) + 1911
        delisting_date = datetime.datetime.strptime(f'{year}/{month}/{day}', '%Y/%m/%d').date()
        j['DelistingDate'] = delisting_date
        j['Company'] = j['Company'].strip() # 去除前後空白
        # print(f"{j['Company']}, {j['Code']}, {j['DelistingDate']}")

    return json


if __name__ == '__main__':
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    json = get_company_suspendListingCsvAndHtml(headers, AD=True)       # AD = True, 轉成西元年

    print('API Name : suspendListingCsvAndHtml')
    print('終止上市公司')
    print('資料筆數: ', len(json))

    for j in json:
        print(f"{j['Company']}, {j['Code']}, {j['DelistingDate']}")
        print('---')

