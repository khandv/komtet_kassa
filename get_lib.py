from settings import connection


# Получение списка заказов для пробития
def get_orders_for_checks():
    sql = 'select order_id \
        from u0752174_delfin_exchange.oc_order_starta \
        where LAST_STATE = 1 and STATUS_ORDER = 3 and order_id > 110 and order_id not in \
        (select order_id from u0752174_delfin_exchange.Checks);'
    with connection():
        cursor = connection().cursor()
        cursor.execute(sql)
        orders = cursor.fetchall()
        return [x[0] for x in orders]


# Получение деталей заказа
def get_order_details(order_id):
    sql = f'SELECT order_id, FIO, FIO_RECIPIENT, RECIPIENT_BIRTH, \
        DATE_ORDER, STATUS_ORDER, TEXT_CANCEL, TOTAL, ID_SHOP \
        FROM u0752174_delfin_exchange.oc_order_starta \
        where order_id = {order_id};'
    with connection():
        cursor = connection().cursor()
        cursor.execute(sql)
        if cursor.rowcount == 0:
            raise Exception('Отсутствует информация о заказе')
        return cursor.fetchone()


# Получение магазина
def get_shop(shop_id):
    sql = f'select name, parent_id \
        from u0752174_delfin_exchange.oc_store_category \
        where category_id = {shop_id};'
    with connection():
        cursor = connection().cursor()
        cursor.execute(sql)
        return cursor.fetchone()


# Получение региона
def get_region(region_id):
    sql = f'select name \
        from u0752174_delfin_exchange.oc_store_category \
        where category_id = {region_id};'
    with connection():
        cursor = connection().cursor()
        cursor.execute(sql)
        return cursor.fetchone()


# Получение адреса эл.почты покупателя из БД сайта
def get_email(order_id):
    sql = f'select email \
        from u0752174_fsin_new.b_user \
        where id in \
        (select user_id \
        from u0752174_fsin_new.b_sale_order \
        where ID = {order_id});'
    with connection():
        cursor = connection().cursor()
        cursor.execute(sql)
        return cursor.fetchone()[0]


# Получение статуса заказа из БД сайта
def get_status_order(order_id):
    sql = f'SELECT STATUS_ID \
        FROM u0752174_fsin_new.b_sale_order \
        where ID = {order_id}'
    with connection():
        cursor = connection().cursor()
        cursor.execute(sql)
        status_order = cursor.fetchone()[0]
        if status_order == 'P':
            return 'В работе'
        if status_order == 'F':
            return 'Выполнен'
        elif status_order == 'OT':
            return 'Отменён'


# Получение ID сбербанка из БД сайта (уникальный номер в системе)
def get_sber_id(order_id):
    sql = f'SELECT value \
        FROM u0752174_fsin_new.b_sale_order_props_value \
        where ORDER_ID = {order_id} and ORDER_PROPS_ID = 10;'
    with connection():
        cursor = connection().cursor()
        cursor.execute(sql)
        return cursor.fetchone()[0]


# Получение информации о чеках заказа (вывод - список словарей чеков)
def get_checks_order(order_id):
    sql = f'select type, check_id, fd_number, number_in_shift, shift_number, date_time, total \
            from u0752174_delfin_exchange.Checks \
            where order_id = {order_id};'
    with connection():
        cursor = connection().cursor()
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
                          'total': i[6]}
            check_list.append(check_dict)
    return check_list


if __name__ == '__main__':
    pass
