from settings import mysql_settings
import get_lib
import pymysql
import rbs
# from pprint import pprint
from _datetime import datetime
import functools

order_status = {0: 'Нет оплаты',
                1: "Холдирование",
                2: "Выполнено",
                3: "Отмена",
                4: "Возврат"}


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


# Добавление в базу данных информации о пробитом чеке / ВЫПОЛНЕНО
@retry(max_tries=100)
def add_check_db(order_id, check_id, type_check='Приход', error=''):
    sql = f'insert into u0752174_delfin_exchange.Checks(order_id, check_id,type, error) \
            values({order_id}, "{check_id}", "{type_check}", "{error}")'
    connection = pymysql.connect(**mysql_settings)
    # with connection:
    with connection.cursor() as cursor:
        # cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()


# Записывает транзакцию в промежуточную базу данных / Проверено
@retry(max_tries=100)
def write_payment(sber_id):
    order_id = get_lib.get_order_id_by_sber_id(sber_id)
    payment_details = rbs.get_order_from_sber(sber_id)
    if payment_details['errorCode'] == '0':
        connection = pymysql.connect(**mysql_settings)
        # with connection:
        with connection.cursor() as cursor:
            sql = f"insert into u0752174_delfin_exchange.payments \
                        (status, date_time, transaction, hold, \
                        finish, refund, order_id) \
                    values( \
                        '{order_status[payment_details['orderStatus']]}', \
                        '{str(datetime.fromtimestamp(payment_details['date'] / 1000))}', \
                        '{str(payment_details['authRefNum'])}', \
                        {float(payment_details['paymentAmountInfo']['approvedAmount'] / 100)}, \
                        {float(payment_details['paymentAmountInfo']['depositedAmount'] / 100)}, \
                        {float(payment_details['paymentAmountInfo']['refundedAmount'] / 100)}, \
                        {order_id}) \
                    ON DUPLICATE KEY UPDATE \
                        status = '{order_status[payment_details['orderStatus']]}', \
                        date_time = '{str(datetime.fromtimestamp(payment_details['date'] / 1000))}', \
                        transaction = '{str(payment_details['authRefNum'])}', \
                        hold = {float(payment_details['paymentAmountInfo']['approvedAmount'] / 100)}, \
                        finish = {float(payment_details['paymentAmountInfo']['depositedAmount'] / 100)}, \
                        refund = {float(payment_details['paymentAmountInfo']['refundedAmount'] / 100)}"
            cursor.execute(sql)
            connection.commit()
            print(f'Информация об оплате заказа № {order_id} добавлена в таблицу payments')


# Обновление инфы о чеке в таблице Cheks
@retry(max_tries=100)
def add_check_db_full(ecr_reg_number, fpd, check_number,
                      check_number_in_shift, shift_number,
                      fn_number, check_date, total, check_url, check_id):
    connection = pymysql.connect(**mysql_settings)
    # with connection:
    with connection.cursor() as cursor:
        sql = f'update u0752174_delfin_exchange.Checks \
                    set ecr_reg_number = "{ecr_reg_number}", fpd = "{fpd}", fd_number = {check_number}, \
                    number_in_shift = {check_number_in_shift}, shift_number = {shift_number}, \
                    fn = "{fn_number}", date_time = "{check_date}", total = {total}, \
                    url = "{check_url}" where check_id = "{check_id}"'
        cursor.execute(sql)
        connection.commit()


if __name__ == '__main__':
    pass
    # order_id = 336402
    # intent = 'sell'
    # check_id = '7d50ce30-9cde-4bb9-a475-67694f0e9a09'
    # error_massage = 'Чек с внешнем идентификатором 336402-sell-test9 существует'
    # add_check_db(str(order_id), check_id, intent, error_massage)
    # write_payment('34792d0d-2bb1-7a40-80d0-7412020c5ad7')
