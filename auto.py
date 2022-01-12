from time import sleep, time, strftime, localtime
from settings import test
from pprint import pprint
import get_lib
import add_lib
import komtet
import verification


# Формируем чек для пробития
def configure_check(order_id, intent):
    try:
        details = get_lib.get_order_details(order_id)
        goods = get_lib.get_goods_of_order(order_id)
        check = {'intent': intent,
                 'external_id': str(order_id) + '-' + intent + 'work',
                 'sno': 0,
                 'user': 'it-service@fguppromservis.ru' if test else get_lib.get_email(order_id),
                 'positions': [],
                 'payments': [{'sum': float(details[7]),
                               'type': 'card'}],
                 'client': {'name': f'{order_id}', 'inn': ''},
                 'payment_address': 'https://fsin-shop.ru',
                 'additional_user_props': {'name': 'email продавца',
                                           'value': 'info@fguppromservis.ru'}}
        sum_goods = 0
        for good in goods:
            if good[-1] != '':
                # print(good[-1])
                for mark in get_lib.get_mark(good[-1]):
                    # code = get_lib.mark_base64(mark[0])
                    # code = mark[0][2:25].replace('21', '') if mark[0][0:2] == '01' else mark[0][0:21]
                    item = {'id': good[0],
                            'name': good[1],
                            'price': good[2],
                            'quantity': mark[1],
                            'total': good[2] * mark[1],
                            'vat': str(good[5]),
                            'nomenclature_code': {'code': verification.normal_mark(mark[0])},
                            'supplier_info': {'phones': [good[8], ], 'name': good[9].strip(), 'inn': good[10].strip()}
                            if good[7] == 1 else {},
                            'calculation_method': 'full_payment',
                            'calculation_subject': 'product_practical'}
                    # print(f'{good[1]}, {verification.normal_mark(mark[0])}')
                    check['positions'].append(item)
                    sum_goods += item['total']
                    with open(f"marks_{strftime('%d-%m-%Y', localtime())}.txt", "a") as file:
                        file.write(f'{verification.normal_mark(mark[0])}\n')
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
        pprint(f'В чеке {len(check["positions"])} позиции')
        return check
    except Exception as error:
        print('Ошибка в configure_check: ', error)


# Пробиваем чеки, заносим данные в промежуточную базу
def check_type(order_id, intent):
    check = configure_check(order_id, intent)
    # pprint(check)
    response = komtet.send_komtet(check)
    result = response.json()
    # noinspection PyBroadException
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
        # print('-' * 80)
        # exit()
    sleep(7)
    while True:
        check_status = komtet.get_check_status(komtet_id)
        if type(check_status) is dict:
            add_lib.add_check_db_full(check_status['ecr_reg_number'], check_status['fpd'],
                                      check_status['check_number'], check_status['check_number_in_shift'],
                                      check_status['shift_number'], check_status['fn_number'],
                                      check_status['check_date'], check_status['total'],
                                      check_status['check_url'], check_id)
            print(f'Информация по чеку заказа № {order_id} добавлена в таблицу Checks')
            break
        else:
            # print('Чек еще не пробит')
            sleep(2)
    print('-' * 80)


# Добавление в промежуточную БД информации о оплате заказа
def write_payments(order_id):
    sber_id = get_lib.get_sber_id(order_id)
    add_lib.write_payment(sber_id)


def mass_check():
    orders = get_lib.get_orders_for_checks()
    if len(orders) != 0:
        start_time = time()
        count = 0
        print('=' * 80)
        print(f'Пошла жара, {strftime("%H:%M:%S", localtime())}')
        print(f'В очереди {len(orders)} чеков')
        print('-' * 80)
        for order_id in orders:
            count += 1
            print(f'Итерация {count}, Заказ номер: {order_id}')
            write_payments(order_id)
            check_type(order_id, 'sell')
        print(f'{strftime("%H:%M:%S", localtime())}, \
                Время выполнения: {time() - start_time}, \
                Было пробито {count} чеков')
        print('=' * 80)
    else:
        print('Нет чеков для пробития')


# Цикл пробития
def typing():
    while True:
        start_time = strftime('%H:%M:%S', localtime())
        if '04:00:00' < start_time < '23:00:00':
            mass_check()
        sleep(60)


if __name__ == '__main__':
    # pprint(configure_check(334478, 'sell'))
    # pprint(configure_check(334478, 'sell'))
    # write_payments(329237)
    typing()
    # print(strftime('%H:%M:%S', localtime()))
    # mass_check()
    # pprint(check_status)
    # check_type(334562, 'sell')
    # check_id = result['uuid']
