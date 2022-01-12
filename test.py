import hmac, hashlib
import requests
import json
import settings
from settings import mysql_settings
import base64
import pymysql
from pprint import pprint

# url = 'https://kassa.komtet.ru/api/shop/v1/'
# group_code = '12926'



def get_orders():
    sql = 'select order_id \
        from u0752174_delfin_exchange.oc_order_starta \
        where LAST_STATE = 1 and STATUS_ORDER = 3 and order_id > 110 and order_id not in \
        (select order_id from u0752174_delfin_exchange.Checks)'
    cursor = connection().cursor()
    cursor.execute(sql)
    orders = cursor.fetchall()
    return [x[0] for x in orders]

def get_order_from_sber(sber_id):
    # try:
    url = 'https://securepayments.sberbank.ru/payment/rest/getOrderStatusExtended.do'
    params = {'orderId': sber_id,
              'userName': settings.sb_login,
              'password': settings.sb_password}
    req = requests.get(url, params=params)
    return req.json()

def mark_base64(mark):
    mark_byte = mark.encode('ascii')
    base64_bytes = base64.b64encode(mark_byte)
    return base64_bytes.decode('ascii')


pprint(mark_base64('04601653025929zJ!sL"4'))
pprint(get_order_from_sber('942b6e4e-8add-713c-bb86-5c55020c5ad7'))


