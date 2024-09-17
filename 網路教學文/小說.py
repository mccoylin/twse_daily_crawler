#!/usr/bin/python3
# -*- coding: utf-8 -*-


# [Python網路爬蟲] 透過 POST 請求和觀察 JavaScript Ajax 來取得金庸小說章回列表
# https://www.youtube.com/watch?v=3ofL2Wkax0M
#
# 作者放在 github 上的程式碼及後續處理的教學程式碼
# https://github.com/telunyang/python_web_scraping/blob/master/cases/ixdzs_jinyong_post_requests.ipynb
#
# 使用 Chrome F12 觀察網頁的 Request Headers，找到 payload 的資料
# 觀察網頁的 HTML 結構，找到要爬取的資料
# 爬取網站的網址是 https://ixdzsw.com/novel/html/
# 
# 程式時間是 2024-09-17，若網站改版，程式可能會失效
#
# 想要取得小說的內容，最快的方法是該本小說的目錄頁面裡，有個「TXT 下載」的按鈕，可以直接下載整本小說。
# 下載的小說檔案是一個 txt 檔案，編碼為 "GB 2312" 裡面有小說的內容，可以直接使用。


import requests 
from bs4 import BeautifulSoup as bs
import json
import os
import re
import pprint
import lxml
# 我的電腦一直跟我說找不到
# from fake_useragent import UserAgent


# 愛下電子書的網站
prefix = 'https://tw.ixdzs.com'

# 我的電腦一直跟我說找不到 fake_useragent
# ua = UserAgent(user_external_data = True)

# 我的電腦一直跟我說找不到 fake_useragent, 改成我的系統使用的 user-agent
my_headers = {
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' 
}



# 取得小說的主要連結
def getMainLinks(url, my_headers):
    # 清除 list
    listData = []

    res = requests.get(url = url, headers = my_headers)
    print(res.status_code)
    #print(res.text)

    #soup = bs(res.text, 'html')
    soup = bs(res.text, 'lxml')

    # 取得的小說書名
    list_noval_name = [
        '倚天屠龍記', 
        # '連城訣', '碧血劍', '鹿鼎記', '書劍恩仇錄', 
        # '俠客行', '神鵰俠侶', '射鵰英雄傳'
    ]

    for noval_name in list_noval_name:
        # 定位到小說的主要連結
        listMainLinks = soup.select_one(f'a[href][title={noval_name}]')
        listData.append({
            'title':listMainLinks['title'],
            'link': listMainLinks['href'],
            'sub': []       # 放置小說的章節連結
        })

    # 取得小說的章節連結
    # {'link': '/read/856/', 'sub': [], 'title': '倚天屠龍記'},

    # pprint.pprint(listData)

    return listData


# 取得小說的連結
def getSubLinks(listData):
    global prefix, my_headers
    pattern = re.compile(r'/read/(\d+)')

    # {'link': '/read/856/', 'sub': [], 'title': '倚天屠龍記'},
    for data in listData:
        # 篩選出連結中的數字
        match = pattern.search(data['link'])
        if not match:
            continue

        # 組合出送到 server 的資料
        bid = match.group(1) 
        payload = {
            'bid': bid
        }

        # 和教學時的網址不一樣，是因為網站改版了
        bid_url = 'https://ixdzsw.com/novel/html/'
        res = requests.post(url = bid_url, headers = my_headers, data = payload)
        if res.status_code != 200:
            print('error')
            continue
        # print(res.text)

        # 看到的 html 內容
        # <li>卷一</li>
        # <li><a href="/read/856/p2.html">第一回　天涯思君不可忘</a></li>

        # 解出 html 的內容
        soup = bs(res.text, 'html.parser')
        li = soup.find_all( 'li')

        for tag in li:
            # print(tag.a)
            if tag.a:
                data['sub'].append({
                    'title': tag.a.text,
                    'link': prefix + tag.a['href'],
                    'content': ''
                })

    return listData



def save_json(folderPath, listData):
    # 寫入 json 檔案
    file_path = folderPath + '/ixdzs_金庸_post_requests.json'
    with open(file_path, 'w', encoding='utf-8') as file:
        # 教學的程式碼是用 json.dump，但是我用 json.dump 會出錯, 原因是沒有加上 fp
        # file.write(json.dump(listData, ensure_ascii=False, indent=4))
        json.dump(listData, file, ensure_ascii=False, indent=4)


def get_b00k_content(listData):
    global my_headers

    for book in listData:
        for url in book['sub']:
            res = requests.get(url['link'], headers = my_headers)
            # print(res.text)
         
            # 解出 html 的內容
            soup = bs(res.text, 'html.parser')
            # print(f'soup : {type(soup)}')

            # 網頁裡小說內容的是包含在 <article class="page-content">  裡面
            # <article class="page-content">
            # ........
            # </article>

            #text = soup.select_one('article')
            text = soup.select_one('article.page-content')
            # print(f'text : {type(text)}')
            # print(f'{text}')

            # <section>
            # <h3>第一回 風雪驚變</h3>
            # ..... 文字內容 .....
            # </section>

            t1 = text.find_all('section')
            # print(f't1 : {type(t1)}')
            # print(f'{t1}')

            # 小說的章節標題
            # <h3>第一回 風雪驚變</h3>
            # 底下的三種寫法都可以
            # title_text = soup.select_one('article.page-content h3')
            # title_text = text.select_one('article.page-content h3')
            title_text = text.select_one('h3')
            # print (f'title_text : {type(title_text)}, {title_text.text}')

            # 小說的內容
            # <p>　　“嘭”的一聲，大門推開，一個身影急急忙忙地進來了。進來的是一個少年人，只見他身穿青衫，眉清目秀，氣宇軒昂，正是武當派的弟子。</p>
            content = text.select('p')

            # 需要處理的內容
            # content [0]
            # <p class="abg">     </p>
            #
            # content [-1]   
            # <p class="abg">
            #
            # <div id="compass-fit-4326306"></div>
            # <script charset="UTF-8">
            #   (function(){
            #     var _lgy_lw = document.createElement("script");
            #     _lgy_lw.type = "text/javascript";
            #     _lgy_lw.charset = "UTF-8";
            #     _lgy_lw.async = true;
            #     _lgy_lw.src= "https://nt.compass-fit.jp/lift_widget.js?adspot_id=4326306";
            #     var _lgy_lw_0 = document.getElementsByTagName("script")[0];
            #     _lgy_lw_0.parentNode.insertBefore(_lgy_lw, _lgy_lw_0);
            #   })();
            # </script>
            # </p>

            # print(f'content : {type(content)} {content[1:-1]}')

            # content 的type 是 str, 要把 list 轉成 str，不然會出錯        
            for test in content[1:-1]:
                # print(f'test : {type(test)}, {test.text}')
                url['content'] += test.text

            print(url['content'])

        #print(f'{book["title"]} : {book["sub"]["content"]}')

    return listData


if __name__ == '__main__':


    # 放置小說的資料
    listData = []

    # 金庸小說的網址 
    url = prefix + '/author/金庸'

    # 放置檔案的路徑
    folderPath = '金庸'
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    listData = getMainLinks(url, my_headers)

    listData = getSubLinks(listData)

    listData = get_b00k_content(listData)

    save_json(folderPath, listData)
