from settings import connection
import get_lib
import rbs
from pprint import pprint
from _datetime import datetime


# Добавление в базу данных информации о пробитом чеке / не проверено
def add_check_db(order_id, check_id, type_check='Приход', error=''):
    sql = "insert into u0752174_delfin_exchange.Checks(order_id, check_id,type, error)" \
          "values(%d, '%s', '%s', '%s')" % (order_id, check_id, type_check, error)
    with connection():
        cursor = connection().cursor()
        cursor.execute(sql)
        connection().commit()


# Записывает транзакцию в промежуточную базу данных / не проверено
def write_payment(sber_id):
    order_id = get_lib.get_order_id_by_sber_id(sber_id)
    payment_details = rbs.get_order_from_sber(sber_id)
    pprint(order_id)
    pprint(payment_details)
    if payment_details['errorCode'] == '0':
        # pass
        sql = f"insert into u0752174_delfin_exchange.payments( \
                    status, date_time, transaction, hold, \
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
        with connection():
            cursor = connection().cursor()
            cursor.execute(sql)
            connection.commit()


if __name__ == '__main__':
    pass
    # write_payment('2bf23569-aa35-7292-a741-8612020c5ad7')
