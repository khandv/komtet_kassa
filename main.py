from time import sleep, time, strftime, localtime
from settings import test
from pprint import pprint
import get_lib
import add_lib
import komtet
import verification


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
                 'client': {'name': f'Заказ № {order_id}, {details[1]}', 'inn': ''},
                 'payment_address': 'https://fsin-shop.ru',
                 'additional_user_props': {'name': 'email отправителя',
                                           'value': 'info@promservis.ru'}}
        sum_goods = 0
        for good in goods:
            if good[-1] != '':
                print(good[-1])
                for mark in get_lib.get_mark(good[-1]):
                    # code = get_lib.mark_base64(mark[0])
                    # code = mark[0][2:25].replace('21', '') if mark[0][0:2] == '01' else mark[0][0:21]
                    item = {'id': good[0],
                            'name': good[1],
                            'price': good[2],
                            'quantity': mark[1],
                            'total': good[2] * mark[1],
                            'vat': str(good[5]),
                            # 'nomenclature_code': {'code': verification.normal_mark(mark[0])},
                            'supplier_info': {'phones': [good[8], ], 'name': good[9].strip(), 'inn': good[10].strip()}
                            if good[7] == 1 else {},
                            'calculation_method': 'full_payment',
                            'calculation_subject': 'product_practical'}
                    print(f'{good[1]}, {verification.normal_mark(mark[0])}')
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
        pprint(f"В чеке {len(check['positions'])} позиции")
        return check
    except Exception as error:
        print('Ошибка в configure_check: ', error)
        return False
