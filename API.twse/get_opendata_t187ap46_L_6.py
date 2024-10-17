#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# 臺灣證券交易所 OpenAPI V1.0
# https://openapi.twse.com.tw/
#
# API 分類：公司治理
# API Name：/opendate/t187ap46_L_6
# 上市公司企業ESG資訊揭露彙總資料-董事會
# 
# 
# https://openapi.twse.com.tw/#/公司治理/get_opendata_t187ap46_L_6
#



import requests
import datetime 


# API Name：​/opendate/t187ap46_L_6
# 上市公司企業ESG資訊揭露彙總資料-董事會
# 
# requests.Get
# Parameters：No parameters
# Responses： Code =	200	
# {
#   "出表日期": "string",
#   "報告年度": 0,
#   "公司代號": "string",
#   "公司名稱": "string",
#   "董事席次(含獨立董事)(席)": "string",
#   "獨立董事席次(席)": "string",
#   "女性董事席次及比率-席": "string",
#   "女性董事席次及比率-比率": "string",
#   "董事出席董事會出席率": "string",
#   "董監事進修時數符合進修要點比率": "string"
# }
# 
#
# 傳入參數:
#   headers: headers
#   AD: 轉成西元年
def get_opendata_t187ap46_L_6(headers:str, AD:bool=True) -> list:

    base_url = r'https://openapi.twse.com.tw/v1'
    api_name = r'/opendata/t187ap46_L_7'

    res = requests.get(url=f'{base_url}{api_name}', headers=headers, timeout=10)  

    if res.status_code != requests.codes.ok: 
        print('Error: ', res.status_code)
        return

    # 試著印出第一筆資料
    # print(res.json()[0])

    json = res.json()

    if not AD:
        return json

    for j in json:
        # '出表日期': '1130711'
        year = int(j['出表日期'][0:3]) + 1911
        month = j['出表日期'][3:5]
        day = j['出表日期'][5:7]
        j["出表日期"] = datetime.datetime.strptime(f'{year}/{month}/{day}', '%Y/%m/%d').date()

        # '報告年度': '112'
        year = int(j['報告年度']) + 1911
        j["報告年度"] = f'{year}'

    return json


if __name__ == '__main__':
    headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }
    json = get_opendata_t187ap46_L_6(headers, AD=True)       # AD = True, 轉成西元年

    print('API Name : /opendate/t187ap46_L_7')
    print('上市公司企業ESG資訊揭露彙總資料-投資人溝通')
    print(f'資料筆數: {len(json)}')

    # 印出前3筆資料
    for index in range(0, 3):
        print(json[index])
        print('------------------------------------')
