#!/usr/bin/python3
# -*- coding: utf-8 -*-

#
# 臺灣證券交易所 OpenAPI V1.0
# https://openapi.twse.com.tw/
#
# API 分類：公司治理
# API Name：​/opendata​/t187ap46_L_8
# 上市公司企業ESG資訊揭露彙總資料-氣候相關議題管理
#
# https://openapi.twse.com.tw/#/公司治理/get_opendata_t187ap46_L_8
#


import requests
import datetime


# API Name：​/opendata​/t187ap46_L_8
# 上市公司企業ESG資訊揭露彙總資料-氣候相關議題管理
# Parameters： No parameters
# Responses： Code =	200	
# {
#   "出表日期": "string",
#   "報告年度": "string",
#   "公司代號": "string",
#   "公司名稱": "string",
#   "董事會與管理階層對於氣候相關風險與機會之監督及治理": "string",
#   "辨識之氣候風險與機會如何影響企業之業務、策略及財務 (短期、中期、長期)": "string",
#   "極端氣候事件及轉型行動對財務之影響": "string",
#   "氣候風險之辨識、評估及管理流程如何整合於整體風險管理制度": "string",
#   "若使用情境分析評估面對氣候變遷風險之韌性，應說明所使用之情境、參數、假設、分析因子及主要財務影響": "string",
#   "若有因應管理氣候相關風險之轉型計畫，說明該計畫內容，及用於辨識及管理實體風險及轉型風險之指標與目標": "string",
#   "使用內部碳定價作為規劃工具，應說明價格制定基礎,若有設定氣候相關目標，應說明所涵蓋之活動、溫室氣體排放範疇、規劃期程，每年達成進度等資訊；若使用碳抵換或再生能源憑證(RECs)以達成相關目標，應說明所抵換之減碳額度來源及數量或再生能源憑證(RECs)數量": "string"
# }
#
# 傳入參數:
#   headers: headers
#   AD: 轉成西元年
def get_opendata_t187ap46_L_8(headers:str, AD:bool=True) -> list:

    base_url = r'https://openapi.twse.com.tw/v1'
    api_name = r'/opendata/t187ap46_L_8'

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
    json = get_opendata_t187ap46_L_8(headers)

    print('API Name : t187ap46_L_8')
    print('上市公司企業ESG資訊揭露彙總資料-氣候相關議題管理')
    print(f'資料筆數: {len(json)}')

    # 印出所有
    for j in json:
        print(j['公司代號'], j['公司名稱'], j['出表日期'])
        print('---')

        # 印出公司名稱為 '聯發科' 或 '台積電' 的資料
        # if j['公司名稱'] == '聯發科' or j['公司名稱'] == '台積電':
        #     print(j)

