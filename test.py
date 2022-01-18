# import hmac, hashlib
import requests
import add_lib
import settings
from settings import mysql_settings
import base64
import pymysql
from pprint import pprint
import functools


# Этот декоратор заново запускает функцию в случае возникновения исключений. Кол-во максимум = max_tries
def retry(max_tries):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for n in range(1, max_tries + 1):
                # noinspection PyBroadException
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if n == max_tries:
                        raise
        return wrapper
    return decorator


# def get_orders():
#     sql = 'select order_id \
#         from u0752174_delfin_exchange.oc_order_starta \
#         where LAST_STATE = 1 and STATUS_ORDER = 3 and order_id > 110 and order_id not in \
#         (select order_id from u0752174_delfin_exchange.Checks)'
#     connection = pymysql.connect(**mysql_settings)
#     cursor = connection.cursor()
#     cursor.execute(sql)
#     orders = cursor.fetchall()
#     return [x[0] for x in orders]

@retry(max_tries=100)
def get_check_for_payments():
    sql = 'select order_id from u0752174_delfin_exchange.Checks where date(date_time) = "2021-12-21"'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
        return [x[0] for x in result]


# Получение ID сбербанка из БД сайта (уникальный номер в системе)
@retry(max_tries=10)
def get_sber_id(order_id):
    sql = f'SELECT value \
            FROM u0752174_fsin_new.b_sale_order_props_value \
            where ORDER_ID = {order_id} and ORDER_PROPS_ID = 10;'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchone()[0]


# запрос в сбер по sber_id
@retry(max_tries=10)
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


def write_payments(checks):
    for check in checks:
        sber_id = get_sber_id(check)
        add_lib.write_payment(sber_id)
        # order_from_sber = get_order_from_sber(sber_id)
        # pprint(order_from_sber)


def write_payments_test(check):
    sber_id = get_sber_id(check)
    # order_from_sber = get_order_from_sber(sber_id)
    add_lib.write_payment(sber_id)
    # pprint(order_from_sber)


# pprint(write_payments_test(338555))
write_payments(get_check_for_payments())
# pprint(get_order_from_sber('942b6e4e-8add-713c-bb86-5c55020c5ad7'))
