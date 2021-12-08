import hmac, hashlib
import requests
import json
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

print(get_orders())


