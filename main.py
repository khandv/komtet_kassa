from datetime import date, datetime, timedelta
from time import sleep
import get_lib
from pprint import pprint
import komtet
import verification


def configure_check(order_id, intent):
    details = get_lib.get_order_details(order_id)
    goods = get_lib.get_goods_of_order(order_id)
    check = {'intent': intent,
             'external_id': str(order_id) + '-' + intent,
             'sno': 0,
             'user': get_lib.get_email(order_id),
             'positions': [],
             'payments': [details[7], 'card'],
             'client': {'name': details[1], 'inn': ''},
             'payment_address': 'https://fsin-shop.ru'}
    sum_goods = 0
    for good in goods:
        if good[-1] != '':
            print(good[-1])
            for mark in get_lib.get_mark(good[-1]):
                print(mark)
                code = mark[0][2:25].replace('21', '') if mark[0][0:2] == '01' else mark[0][0:21]
                print(code)
                item = {'id': good[0],
                        'name': good[1],
                        'price': good[2],
                        'quantity': mark[1],
                        'total': good[2] * mark[1],
                        'vat': str(good[5]),
                        'nomenclature_code': [code, verification.mark_to_tag(code)],
                        'supplier_info': {'phones': [good[8], ], 'name': good[9].strip(), 'inn': good[10].strip()}
                        if good[7] == 1 else {},
                        'calculation_method': 'full_payment',
                        'calculation_subject': 'product_practical'}
                check['positions'].append(item)
                sum_goods += item['total']
        else:
            item = {'id': good[0],
                    'name': good[1],
                    'price': good[2],
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
    return check

#response = komtet.send_komtet(configure_check(331579, 'sell'))

if __name__ == '__main__':
    pprint(configure_check(331580, 'sell'))
    #pprint(response.text)
