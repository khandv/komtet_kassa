import datetime
import hashlib
import hmac
import json
from pprint import pprint
from settings import shop_id, secret

import requests


mark_code_raw_in = '(01)04610030141190(21)00004v9'


def mark_to_tag(mark_code_raw_in):
    for i in ('(21)', '(01)'):
        mark_code_raw = mark_code_raw_in.replace(i, '')
    prefix = '0005'
    gtin = int(mark_code_raw[0:14])
    gtin_hex = str((hex(gtin)).upper()[2:])
    # добавляет ведущие нули до 12 знаков
    if len(gtin_hex) < 12:
        gtin_hex = '0' * (12 - len(gtin_hex)) + gtin_hex
    # добавляет префикс
    gtin_hex = prefix + gtin_hex
    gtin_hex = ''.join(gtin_hex[i:i + 2] for i in range(0, len(gtin_hex), 2))
    mark_hex = ''
    mark = mark_code_raw[14:21]
    for i in mark:
        mark_hex = mark_hex + hex(ord(i))[2:]
    mark_hex = ''.join(mark_hex[i:i + 2] for i in range(0, len(mark_hex), 2))
    mark_to_send = gtin_hex + mark_hex
    return mark_to_send


def send_komtet(check):
    url = 'https://kassa.komtet.ru/api/shop/v1/queues/12926/task'
    # msg = method + url + body
    msg = 'POST' + url + json.dumps(check)
    signature = hmac.new(secret.encode('utf-8'), msg.encode('utf-8'), digestmod=hashlib.md5).hexdigest()
    headers = {
        'Content-type': 'application/json',
        'Authorization': 'axTea5',
        'X-HMAC-Signature': signature
    }
    return requests.post(url=url, headers=headers, data=json.dumps(check))


# запрос реквизитов чека
def get_check_status(id):
    url = 'https://kassa.komtet.ru/api/shop/v1/' + 'tasks/%s' % id
    print(url)
    msg = 'GET' + url + ''
    signature = hmac.new(secret.encode('utf-8'), msg.encode('utf-8'), digestmod=hashlib.md5).hexdigest()
    headers = {
        'Content-type': 'application/json',
        'Authorization': 'axTea5',
        'X-HMAC-Signature': signature
    }
    a = json.loads(requests.get(url=url, headers=headers).content)
    print(a)
    print(a['state'])
    print(a['fiscal_data']['rn'])
    print(int(a['fiscal_data']['fp']))
    print(int(a['fiscal_data']['i']))
    print(int(int(a['fiscal_data']['shn'])))
    print(int(a['fiscal_data']['fn']))
    print(int(a['fiscal_data']['sh']))
    print(a['fiscal_data']['t'])
    print(float(a['fiscal_data']['s']))

    if a['state'] == 'done':
        # вытаскиваем инфу о чеке из ответа, формируем словарь res
        print('Чек сформирован успешно')
        ecr_registration_number = a['fiscal_data']['rn']
        fpd = int(a['fiscal_data']['fp'])
        check_number = int(a['fiscal_data']['i'])
        check_number_in_shift = int(a['fiscal_data']['shn'])
        fn_mumber = int(a['fiscal_data']['fn'])
        shift_number = int(a['fiscal_data']['sh'])
        check_date = a['fiscal_data']['t']
        total = float(a['fiscal_data']['s'])
        check_url = a['receipt_url']
        res = {
            'ecr_reg_number': ecr_registration_number,
            'fpd': fpd,
            'check_number': check_number,
            'check_number_in_shift': check_number_in_shift,
            'fn_mumber': fn_mumber,
            'shift_number': shift_number,
            'check_date': datetime.datetime.strptime(check_date, '%Y%m%dT%H%M'),
            'total': total,
            'check_url': check_url
        }
        print('-' * 80)
        return res


# get_ofdURL - формирование урла чека из офд. используется в bitrix.py
def get_ofdURL(register_number, fn_number, doc_number, fpd):
    check_url = 'https://check.ofd.ru/rec/7743369591/%s/%s/%s/%s' % (register_number, fn_number, doc_number, fpd)
    return check_url


class Item:
    def __init__(self):
        self.name = ''
        self.price = float(0)
        self.quantity = float(0)
        self.sum = 0
        self.payment_method = "full_payment"
        self.payment_object = "product"
        self.vat = '20'
        self.is_comissioner = False
        self.comission_address = ''
        self.comission_phone = ''
        self.comission_name = ''
        self.comission_inn = ''
        self.code = ''

    def json(self):
        # vat - НДС
        if (self.vat == '20'):
            vat_del = 6
        elif self.vat == '10':
            vat_del = 11
        else:
            pass

        item = {
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'sum': self.sum,
            'payment_method': self.payment_method,
            'payment_object': self.payment_object,
            'vat': {
                'type': self.vat
            }
        }
        if self.mark_row != '':
            item['nomenclature_code'] = mark_to_tag(self.mark_row)
        if self.is_comissioner:
            item['agent_info'] = {'type': 'commission_agent'}

            item['supplier_info'] = {'phones': [self.comission_phone, ],
                                     'name': self.comission_name,
                                     'inn': self.comission_inn}
        if self.vat != '0':
            item['vat']['sum'] = round(self.sum / vat_del, 2)
        return item


pprint(get_check_status(104500087))
# mark_code_raw = '(01)04610030141190(21)00004v9'
# print(mark_to_tag(mark_code_raw))
