from time import sleep, time, strftime, localtime
from settings import test
from pprint import pprint
import get_lib
import add_lib
import komtet
import verification


# Формируем чек для пробития
def configure_check(order_id, intent):
    details = get_lib.get_order_details(order_id)
    goods = get_lib.get_goods_of_order(order_id)
    check = {'intent': intent,
             'external_id': str(order_id) + '-' + intent,
             'sno': 0,
             'user': 'it-service@fguppromservis.ru' if test else get_lib.get_email(order_id),
             'positions': [],
             'payments': [{'sum': float(details[7]),
                           'type': 'card'}],
             'client': {'name': f'Заказ № {order_id}, {details[1]}', 'inn': ''},
             'payment_address': 'https://fsin-shop.ru'}
    sum_goods = 0
    for good in goods:
        if good[-1] != '':
            print(good[-1])
            for mark in get_lib.get_mark(good[-1]):
                if '(21)' in mark[0]:
                    code = mark[0][:29]
                else:
                    code = mark[0][:21]
                # code = get_lib.mark_base64(mark[0])
                # code = mark[0][2:25].replace('21', '') if mark[0][0:2] == '01' else mark[0][0:21]
                item = {'id': good[0],
                        'name': good[1],
                        'price': good[2],
                        'quantity': mark[1],
                        'total': good[2] * mark[1],
                        'vat': str(good[5]),
                        'nomenclature_code': {'code': code},
                        'supplier_info': {'phones': [good[8], ], 'name': good[9].strip(), 'inn': good[10].strip()}
                        if good[7] == 1 else {},
                        'calculation_method': 'full_payment',
                        'calculation_subject': 'product_practical'}
                check['positions'].append(item)
                sum_goods += item['total']
        else:
            item = {'id': good[0],
                    'name': good[1],
                    'price': round(good[2], 2),
                    'quantity': good[3],
                    'total': good[4],
                    'vat': str(good[5]),
                    'supplier_info': {'phones': [good[8], ], 'name': good[9].strip(), 'inn': good[10].strip()}
                    if good[7] == 1 else {},
                    'calculation_method': 'full_payment',
                    'calculation_subject': 'product'}
            check['positions'].append(item)
            sum_goods += item['total']
    print(f'Сумма чека: {details[7]}, сумма по товарам: {sum_goods}')
    if sum_goods != details[7]:
        check['payments'][0]['sum'] = round(float(sum_goods), 2)
        print(f'Сумма чека: {details[7]}, сумма по товарам: {sum_goods}, будет пробита сумма по товарам')
    # pprint(check)
    return check


# Пробиваем чеки, заносим данные в промежуточную базу
def check_type(order_id, intent):
    response = komtet.send_komtet(configure_check(order_id, intent))
    result = response.json()
    err = []
    pprint(f'Результат: {result}')
    try:
        check_id = result['uuid']
        komtet_id = result['id']
        print(f'Заказ {order_id} принят без ошибки, komtet_id: {komtet_id}')
        add_lib.add_check_db(str(order_id), check_id, intent)
    except Exception:
        error_massage = result['title']
        check_id = result['task']['uuid']
        komtet_id = result['task']['id']
        print(f'Заказ {order_id} принят c ошибкой, {error_massage}, komtet_id: {komtet_id}')
        add_lib.add_check_db(str(order_id), check_id, intent, error_massage)

    sleep(15)
    try:
        check_status = komtet.get_check_status(komtet_id)
    except Exception:
        print(f'Не удалось запросить реквизиты чека заказа {order_id}, komtet_id: {komtet_id}')
    try:
        # if check_status['fpd'] != None:
        add_lib.add_check_db_full(check_status['ecr_reg_number'], check_status['fpd'],
                                  check_status['check_number'], check_status['check_number_in_shift'],
                                  check_status['shift_number'], check_status['fn_number'],
                                  check_status['check_date'], check_status['total'],
                                  check_status['check_url'], check_id)
        print(f'Чек заказа № {order_id} успешно пробит, информация добавлена в таблицу Checks')
    except Exception as ex:
        print(f'Не удалось загрузить реквизиты чека заказа {order_id}, komtet_id: {komtet_id}')
        print(f'{ex.args} komtet_id: {komtet_id}')
        with open("log.txt", "w") as file:
            file.write(f'{komtet_id} {check_id}\n')
        err.append(komtet_id)
    print('-' * 80)
    return err


# Добавление в промежуточную БД информации о оплате заказа
def write_payments(order_id):
    sber_id = get_lib.get_sber_id(order_id)
    add_lib.write_payment(sber_id)


def mass_check():
    orders = get_lib.get_orders_for_checks()
    # print(orders)
    start_time = time()
    count = 0
    check_errors = []
    for order_id in orders[0:100]:
        sleep(1)
        count += 1
        print(f'Итерация {count}, Заказ номер: {order_id}')
        write_payments(order_id)
        check_error = check_type(order_id, 'sell')
        print(check_error)
        if len(check_error) != 0:
            check_errors.append(check_error)
    print(check_errors)
    # if len(check_errors) != 0:
    #     for err in check_errors:
    #         check_status = komtet.get_check_status(err[0])
    #         add_lib.add_check_db_full(check_status['ecr_reg_number'], check_status['fpd'],
    #                                 check_status['check_number'], check_status['check_number_in_shift'],
    #                                 check_status['shift_number'], check_status['fn_number'],
    #                                 check_status['check_date'], check_status['total'],
    #                                 check_status['check_url'], 'd40e2979-b6e3-4594-b426-e86cdba83f36')
    print(f'Время выполнения: {time() - start_time}')


# Цикл пробития
def typing():
    while True:
        start_time = strftime('%H:%M:%S', localtime())
        print(start_time)
        sleep(60)
        # try:
        #     if '04:00:00' < start_time < '23:00:00':
        #         print(f'Идет работа, {start_time}')
        #         mass_check()
        # except Exception:
        #     break
        if '04:00:00' < start_time < '23:00:00':
            print(f'Идет работа, {start_time}')
            mass_check()


if __name__ == '__main__':
    pprint(configure_check(334230, 'sell'))
    # write_payments(334230)
    # check_type(334230, 'sell')
    # typing()
    # print(strftime('%H:%M:%S', localtime()))
    # mass_check()
    # check_status = komtet.get_check_status(106416664)
    # pprint(check_status)
    # add_lib.add_check_db_full(check_status['ecr_reg_number'], check_status['fpd'],
    #                           check_status['check_number'], check_status['check_number_in_shift'],
    #                           check_status['shift_number'], check_status['fn_number'],
    #                           check_status['check_date'], check_status['total'],
    #                           check_status['check_url'], 'd40e2979-b6e3-4594-b426-e86cdba83f36')

