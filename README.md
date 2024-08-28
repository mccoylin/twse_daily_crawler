# twse_daily_crawler

# 爬取台灣證券交易所的股價資料

「每日收盤行情(全部)」會過濾掉權證、ETF等資料。<BR>
https://www.twse.com.tw/zh/trading/historical/mi-index.html <BR>
可參考這篇文章：Python 爬蟲教學 - 股票價格資料收集 <BR>
https://www.peteryangblog.com/posts/python-data-collecting-stock-price <BR>

使用方式：<BR>
$ python3 get_stock_json.py <BR>
或是可以指定日期範圍： <BR>
$ python3 get_stock_json.py -s 20240801 -e 20240831 <BR>