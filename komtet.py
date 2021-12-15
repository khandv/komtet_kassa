import datetime
import hashlib
import hmac
import json
from pprint import pprint
from settings import secret, queue
import requests


def send_komtet(check):
    url = 'https://kassa.komtet.ru/api/shop/v1/queues/'+str(queue)+'/task'
    # msg = method + url + body
    msg = 'POST' + url + json.dumps(check)
    signature = hmac.new(secret.encode('utf-8'), msg.encode('utf-8'), digestmod=hashlib.md5).hexdigest()
    headers = {'Content-type': 'application/json',
               'Authorization': 'axTea5',
               'X-HMAC-Signature': signature}
    return requests.post(url=url, headers=headers, data=json.dumps(check))


# запрос реквизитов чека
def get_check_status(check_id):
    url = f'https://kassa.komtet.ru/api/shop/v1/tasks/{check_id}'
    # print(url)
    msg = 'GET' + url + ''
    signature = hmac.new(secret.encode('utf-8'), msg.encode('utf-8'), digestmod=hashlib.md5).hexdigest()
    headers = {'Content-type': 'application/json',
               'Authorization': 'axTea5',
               'X-HMAC-Signature': signature}
    a = json.loads(requests.get(url=url, headers=headers).content)
    # print(a)
    # print(a['state'])
    # print(a['fiscal_data']['rn'])
    # print(int(a['fiscal_data']['fp']))
    # print(int(a['fiscal_data']['i']))
    # print(int(int(a['fiscal_data']['shn'])))
    # print(int(a['fiscal_data']['fn']))
    # print(int(a['fiscal_data']['sh']))
    # print(a['fiscal_data']['t'])
    # print(float(a['fiscal_data']['s']))
    if a['state'] == 'done':
        # вытаскиваем инфу о чеке из ответа, формируем словарь res
        ecr_registration_number = a['fiscal_data']['rn']
        fpd = int(a['fiscal_data']['fp'])
        check_number = int(a['fiscal_data']['i'])
        check_number_in_shift = int(a['fiscal_data']['shn'])
        fn_number = int(a['fiscal_data']['fn'])
        shift_number = int(a['fiscal_data']['sh'])
        check_date = a['fiscal_data']['t']
        total = float(a['fiscal_data']['s'])
        check_url = a['receipt_url']
        res = {'ecr_reg_number': ecr_registration_number,
               'fpd': fpd,
               'check_number': check_number,
               'check_number_in_shift': check_number_in_shift,
               'fn_number': fn_number,
               'shift_number': shift_number,
               'check_date': datetime.datetime.strptime(check_date, '%Y%m%dT%H%M'),
               'total': total,
               'check_url': check_url}
        print('Чек сформирован успешно')
        return res


# get_ofdURL - формирование урла чека из офд. используется в bitrix.py
def get_ofd_url(register_number, fn_number, doc_number, fpd):
    check_url = 'https://check.ofd.ru/rec/7743369591/%s/%s/%s/%s' % (register_number, fn_number, doc_number, fpd)
    return check_url


if __name__ == '__main__':
    pprint(get_check_status(106170874))
    # mark_code_raw = '(01)04610030141190(21)00004v9'
    # print(mark_to_tag(mark_code_raw))
