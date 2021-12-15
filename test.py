import hmac, hashlib
import requests
import json
from settings import mysql_settings
import pymysql

# url = 'https://kassa.komtet.ru/api/shop/v1/'
# group_code = '12926'

def connection():
    # Настройки подключения к базе данных
    settings = {'host': '31.31.198.53',
                'database': 'u0752174_fsin_new',
                'user': 'u0752174_site_ex',
                'password': 'L7y7L1c6',
                'use_unicode': True}
    try:
        connection = pymysql.connect(**settings)
    except Exception as error:
        print('Не удалось подключиться к БД\nОтвет сервера: ', error)
    return connection

def get_orders():
    sql = 'select order_id \
        from u0752174_delfin_exchange.oc_order_starta \
        where LAST_STATE = 1 and STATUS_ORDER = 3 and order_id > 110 and order_id not in \
        (select order_id from u0752174_delfin_exchange.Checks)'
    cursor = connection().cursor()
    cursor.execute(sql)
    orders = cursor.fetchall()
    return [x[0] for x in orders]

def add_check_db_full(ecr_reg_number, fpd, check_number,
                      check_number_in_shift, shift_number,
                      fn_number, check_date, total, check_url):
    try:
        connection = pymysql.connect(**mysql_settings)
    except Exception as error:
        print('Не удалось подключиться к БД\nОтвет сервера: ', error)
    sql = f'update u0752174_delfin_exchange.Checks \
            set ecr_reg_number = "{ecr_reg_number}", fpd = "{fpd}", fd_number = {check_number}, \
            number_in_shift = {check_number_in_shift}, shift_number = {shift_number}, \
            fn = "{fn_number}", date_time = {check_date.isoformat()}, total = {total}, \
            url = "{check_url}" where check_id = "{check_id}"'
    with connection:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()

# print(get_orders())


