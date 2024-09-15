#!/usr/bin/python3
# -*- coding: utf-8 -*-


# mysql datatable delete row data script
# 刪除 datatable ｀交易日期｀欄位大於某日期的資料
# 使用方法：
# $ python3 delete_datatable_row.py
#
# 因應 twse_stock 新增「每日收盤行情」資料表時，若有中斷時，造成的日期不對情況。
# 可執行這支程式刪除 ｀交易日期｀欄位大於某日期的資料


import argparse
import mysql.connector
import re


############################################################################################################
# 列出所有符合條件的 mysql datatable 
def list_all_datatable(cursor, db_name, table_name):
    # {
    # 依照條件建立正規表示式
    pattern = re.compile(table_name) 

    cursor.execute("SHOW TABLES")
    result = cursor.fetchall()

    datatable_list = []
    for table in result:
        # print(table[0])
        # 尋找出符合條件的 datatable
        if pattern.search(table[0]):
            # print(f'find : {table[0]}')
            # 加入 list
            datatable_list.append(table[0])

    return datatable_list

    # }     # End of list_all_datatable



############################################################################################################
# Connect to the database
def get_mysql_connection():
    # {
    # 依照自己的設定修改
	return mysql.connector.connect(
		host="127.0.0.1",
		port=3306,
		user="twsetrading",
		password="9$$!;$CISER[2eIm",
        db="twse_stock",
		charset="utf8"
	)
    # }     # End of get_mysql_connection


############################################################################################################
# 刪除 datatable ｀交易日期｀欄位大於某日期的資料
def delete_row_data(cursor, datatable, date):
    # {
    global conn 

    # 依照條件建立正規表示式
    pattern = re.compile(datatable) 

    # 取得 datatable 的欄位名稱
    cursor.execute(f"SHOW COLUMNS FROM {datatable}")
    result = cursor.fetchall()

    # 取得 datatable 的欄位名稱
    column_name = []
    for column in result:
        column_name.append(column[0])

    # 檢查是否有交易日期欄位
    if "交易日期" in column_name:
        # 刪除 datatable ｀交易日期｀欄位大於某日期的資料
        delete_sql = (f"DELETE FROM twse_stock.{datatable} WHERE `交易日期` > '{date}';")
        #print(delete_sql)

        cursor.execute(delete_sql)
        conn.commit()

        print(f'{datatable} {cursor.rowcount} record(s) deleted')

    else:
        print(f"datatable {datatable} 沒有`交易日期`欄位")


    # }     # End of delete_row_data


############################################################################################################
if __name__ == '__main__':
    global conn
    # 建立連線
    conn = get_mysql_connection()
    cursor = conn.cursor()

    # 列出所有符合條件的 mysql datatable
    datatable = list_all_datatable(cursor, "twse_stock", "daily_quotes")

    print(len(datatable))

    # 刪除 datatable ｀交易日期｀欄位大於某日期的資料
    for table in datatable:
        delete_row_data(cursor, table, '2023-10-13')

    cursor.close()
    conn.close()
