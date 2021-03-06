import pymysql
import base64
from settings import mysql_settings
import functools
# from pprint import pprint


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

def connection():
    try:
        connection = pymysql.connect(**mysql_settings)
    except Exception as error:
        print('Не удалось подключиться к БД\nОтвет сервера: ', error)
    return connection

# Получение списка заказов для пробития
@retry(max_tries=100)
def get_orders_for_checks():
    sql = 'select order_id \
        from admin_exchange.oc_order_starta \
        where LAST_STATE = 1 and STATUS_ORDER = 3 and order_id > 110 and order_id not in \
        (select order_id from admin_exchange.Checks);'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        orders = cursor.fetchall()
    return [x[0] for x in orders]


# Получение деталей заказа
@retry(max_tries=100)
def get_order_details(order_id):
    sql = f'SELECT order_id, FIO, FIO_RECIPIENT, RECIPIENT_BIRTH, \
            DATE_ORDER, STATUS_ORDER, TEXT_CANCEL, TOTAL, ID_SHOP \
            FROM admin_exchange.oc_order_starta \
            where order_id = {order_id};'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        if cursor.rowcount == 0:
            raise Exception('Отсутствует информация о заказе')
        return cursor.fetchone()


# Получение магазина
@retry(max_tries=100)
def get_shop(shop_id):
    sql = f'select name, parent_id \
            from admin_exchange.oc_store_category \
            where category_id = {shop_id};'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchone()


# Получение региона
@retry(max_tries=100)
def get_region(region_id):
    sql = f'select name \
            from admin_exchange.oc_store_category \
            where category_id = {region_id};'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchone()


# Получение адреса эл.почты покупателя из БД сайта
@retry(max_tries=100)
def get_email(order_id):
    sql = f'select email \
            from admin_bitrix.b_user \
            where id in \
            (select user_id \
            from admin_bitrix.b_sale_order \
            where ID = {order_id});'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchone()[0]


# Получение статуса заказа из БД сайта
@retry(max_tries=100)
def get_status_order(order_id):
    sql = f'SELECT STATUS_ID \
            FROM admin_bitrix.b_sale_order \
            where ID = {order_id}'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        status_order = cursor.fetchone()[0]
    if status_order == 'P':
        return 'В работе'
    if status_order == 'F':
        return 'Выполнен'
    elif status_order == 'OT':
        return 'Отменён'


# Получение ID сбербанка из БД сайта (уникальный номер в системе)
@retry(max_tries=100)
def get_sber_id(order_id):
    sql = f'SELECT value \
            FROM admin_bitrix.b_sale_order_props_value \
            where ORDER_ID = {order_id} and ORDER_PROPS_ID = 10;'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchone()[0]


# Получение информации о чеках заказа (вывод - список словарей чеков)
@retry(max_tries=100)
def get_checks_order(order_id):
    sql = f'select type, check_id, fd_number, number_in_shift, \
            shift_number, date_time, total, url \
            from admin_exchange.Checks \
            where order_id = {order_id};'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        check_from_db = cursor.fetchall()
    check_list = []
    for i in check_from_db:
        if i[2] is not None:
            check_dict = {'type_of_check': i[0],
                          'fd_number': i[2],
                          'number_in_shift': i[3],
                          'shift_number': i[4],
                          'date_time': i[5],
                          'total': i[6],
                          'url': i[7]}
            check_list.append(check_dict)
    return check_list


# Узнаем номер заказа из БД битрикса-сайта по sber_id
@retry(max_tries=100)
def get_order_id_by_sber_id(sber_id):
    sql = f'select order_id \
            from admin_bitrix.b_sale_order_props_value \
            where VALUE = "{sber_id}"'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchone()[0]


# Получение товаров из промежуточной БД, возвращает кортеж из кортежей товаров
@retry(max_tries=100)
def get_goods_of_order(order_id):
    sql = f'SELECT DF_CODE, NAME,PRICE, QUANTITY, PRODUCT_SUM, NDS, ISCHANGE, \
            commission, comissioner_phone, comissioner_name, comissioner_inn, ORDER_PRODUCT_GUID \
            FROM admin_exchange.oc_order_products_starta \
            where quantity > 0 and order_id = {order_id} and ischange = 1'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return cursor.fetchall()


# Получение кода марикровки по guid продукта, возвращает кортеж кортежей марка + количество
@retry(max_tries=100)
def get_mark(product_guid):
    sql = f'select mark, quantity \
            from admin_exchange.oc_order_marks_starta \
            where ORDER_PRODUCT_GUID = "{product_guid}"'
    connection = pymysql.connect(**mysql_settings)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    marks = list(list(res) for res in result)
    return marks


def mark_base64(mark):
    mark_byte = mark.encode('ascii')
    base64_bytes = base64.b64encode(mark_byte)
    return base64_bytes.decode('ascii')


if __name__ == '__main__':
    pass
    # print(get_orders_for_checks())
    # print(get_order_details(331587))
    # print(get_shop(get_order_details(331587)[8]))
    # print(get_region(get_shop(get_order_details(331587)[8])[1]))
    # print(get_email(331579))
    # print(get_status_order(331587))
    # print((get_sber_id(334283)))
    # print(get_checks_order(331941))
    # print(get_order_id_by_sber_id('9a820daa-d4a9-7685-84f6-b327020c5ad7'))
    # print(datetime.fromtimestamp(1639057669192 / 1000))
    # pprint(get_goods_of_order(333802))
    # pprint(get_mark('6AE00908-18D5-4B90-88A8-63E4D5B0DE7B'))
    # for mark in get_mark('6AE00908-18D5-4B90-88A8-63E4D5B0DE7B'):
    # print(mark_base64(mark[0]))
