from settings import mysql_settings
import get_lib
import pymysql
import rbs
from pprint import pprint
from _datetime import datetime


# Добавление в базу данных информации о пробитом чеке / не проверено
def add_check_db(order_id, check_id, type_check='Приход', error=''):
    try:
        connection = pymysql.connect(**mysql_settings)
    except Exception as error:
        print('Не удалось подключиться к БД\nОтвет сервера: ', error)
    sql = f'insert into u0752174_delfin_exchange.Checks(order_id, check_id,type, error) \
            values({order_id}, "{check_id}", "{type_check}", "{error}")'
    with connection:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()


# Записывает транзакцию в промежуточную базу данных / не проверено
def write_payment(sber_id):
    order_id = get_lib.get_order_id_by_sber_id(sber_id)
    payment_details = rbs.get_order_from_sber(sber_id)
    pprint(order_id)
    pprint(payment_details)
    try:
        connection = pymysql.connect(**mysql_settings)
    except Exception as error:
        print('Не удалось подключиться к БД\nОтвет сервера: ', error)
    if payment_details['errorCode'] == '0':
        # pass
        sql = f"insert into u0752174_delfin_exchange.payments \
                    (status, date_time, transaction, hold, \
                    finish, refund, order_id) \
                values( \
                    {payment_details['orderStatus']}, \
                    {str(datetime.fromtimestamp(payment_details['date'] / 1000))}, \
                    {str(payment_details['authRefNum'])}, \
                    {float(payment_details['paymentAmountInfo']['approvedAmount'] / 100)}, \
                    {float(payment_details['paymentAmountInfo']['depositedAmount'] / 100)}, \
                    {float(payment_details['paymentAmountInfo']['refundedAmount'] / 100)}, \
                    {order_id}) \
                ON DUPLICATE KEY UPDATE \
                    status = {payment_details['orderStatus']}, \
                    date_time = {str(datetime.fromtimestamp(payment_details['date'] / 1000))}, \
                    transaction = {str(payment_details['authRefNum'])}, \
                    hold = {float(payment_details['paymentAmountInfo']['approvedAmount'] / 100)}, \
                    finish = {float(payment_details['paymentAmountInfo']['depositedAmount'] / 100)}, \
                    refund = {float(payment_details['paymentAmountInfo']['refundedAmount'] / 100)}"
        with connection:
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()


# Обновление инфы о чеке в таблице Cheks
def add_check_db_full(ecr_reg_number, fpd, check_number,
                      check_number_in_shift, shift_number,
                      fn_mumber, check_date, total):
    try:
        connection = pymysql.connect(**mysql_settings)
    except Exception as error:
        print('Не удалось подключиться к БД\nОтвет сервера: ', error)
    sql = f'update u0752174_delfin_exchange.Checks \
            set ecr_reg_number = "%s", fpd = "%d",fd_number = %d,number_in_shift = %d, \
            shift_number = %d, fn = %d, date_time = "%s", total = %f, url = "%s" \
            where check_id = "%s"' % (a['ecr_reg_number'], a['fpd'], a['check_number'],
                                             a['check_number_in_shift'], a['shift_number'],
                                             a['fn_mumber'], a['check_date'].isoformat(),
                                             a['total'], url, check_id)
    with connection:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()


if __name__ == '__main__':
    order_id = 336402
    intent = 'sell'
    check_id = '7d50ce30-9cde-4bb9-a475-67694f0e9a09'
    error_massage = 'Чек с внешнем идентификатором 336402-sell-test9 существует'
    add_check_db(str(order_id), check_id, intent, error_massage)
    # write_payment('2bf23569-aa35-7292-a741-8612020c5ad7')
