from settings import connection


# Добавление в базу данных информации о пробитом чеке / не проверено
def add_check_db(order_id, check_id, type_check='Приход', error=''):
    sql = "insert into u0752174_delfin_exchange.Checks(order_id, check_id,type, error)" \
          "values(%d, '%s', '%s', '%s')" % (order_id, check_id, type_check, error)
    with connection():
        cursor = connection().cursor()
        cursor.execute(sql)
        connection().commit()


if __name__ == '__main__':
    pass
