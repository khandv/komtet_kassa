from datetime import datetime
import settings
import requests
import json
from datetime import datetime, timedelta

debug = True

__debug = False
payments = []
pays = {}
time_loads = {}

order_status = {
    0: 'Нет оплаты',
    1: "Холдирование",
    2: "Выполнено",
    3: "Отмена",
    4: "Возврат",
}

# формируем словарь pays (см. ниже) из логов с ftp reg.ru Зачем? нигде не нашел использования
def download_rbs_log(file_path):

    from ftplib import FTP
    out = 'rbs_log.log'
    try:
        ftp = FTP('server40.hosting.reg.ru', 'u0647730', '2G1d8W3n')
        with open(out, 'wb') as f:
            ftp.retrbinary('RETR ' + file_path, f.write)
    except Exception as e:
        print(e)
    finally:
        ftp.close()
    f = open(out, 'r', encoding='utf-8')
    lines = f.readlines()
    read_req, read_resp = False, False
    order_id = ''
    sb_order_id = ''
    for line in lines:
        # обрабатываются строки. по 3 шт. Если в 1-й находит 'sberbank.ru/payment/rest/registerPreAuth.do'
        # то обрабатывается следующая: read_req = True (строка запроса)
        # затем следующая: read_resp = True (строка ответа)
        # после обработки из строки формируется файл json
        if read_req:
            read_req, read_resp = False, True
            answer = line[line.find('{'):].replace('\\', '')
            answer = answer.replace('"{"','{"')
            answer = answer.replace('"}"', '"}')

            answer = json.loads(answer)
            order_id= str(answer['orderNumber'])
            order_id = order_id[:order_id.find('_')]
            continue
            #print('Запрос ', json.dumps(line))

        if read_resp:
            try:
                answer = line[line.find('{'):].replace('\\', '')
                answer = json.loads(answer)
                sb_order_id = answer['orderId']
            except:
                continue
            # заполняем словарь pays: ключ - order_id из запроса read_req к значению sb_order_id из ответа read_resp
            pays[int(order_id)] = sb_order_id
            read_resp = False
        # если в линии находит строку 'sberbank.ru/payment/rest/registerPreAuth.do', то обрабатывается след. строка, см. выше
        if line.find('sberbank.ru/payment/rest/registerPreAuth.do') > 0:
            read_req = True

# запрос в сбер по id_sb (sber_id), возвращает результат в json. используется в bitrix.py
def get_order_extended(id_sb):
    _URL = '%sgetOrderStatusExtended.do?orderId=%s&userName=%s&password=%s' % (_sb_URL, id_sb, _sb_login, _sb_password)

    zap = requests.get(_URL)
    res = zap.json()
    # print (res)
    return res

# запрос деталей заказа. используется ниже в функции get_order_status(order_id)
def get_order_details(order_id_sb):
    __URL = 'https://securepayments.sberbank.ru/payment/rest/getOrderStatusExtended.do'
    if __debug:
        print(__URL)
    zap = requests.get(__URL, params={'orderId': order_id_sb, 'password': _sb_password, 'userName': _sb_login})
    res = zap.json()
    try:
        return res
    except:
        print('')

# возвращает статус заказа. где используется? нигде не фигурирует
def get_order_status(order_id):
    pay = get_order_details(order_id)
    if pay['errorCode'] != '0':
        raise str(pay)
    return order_status[int(pay['orderStatus'])]
    print(json.dumps(pay))

# запрос отмены оплаты заказа. где используется? нигде не фигурирует
def cancel_order(order_id):
    __URL = 'https://securepayments.sberbank.ru/payment/rest/reverse.do'
    result = requests.get(__URL, params={'orderId': order_id, 'password': _sb_password, 'userName': _sb_login})
    r = result.json()
    return r

# запрос завершения оплаты заказа. где используется? нигде не фигурирует
def close_order(order_id, amount):
    URL = 'https://securepayments.sberbank.ru/payment/rest/deposit.do'
    total = int(amount * 100)
    result = requests.get(URL, params={'orderId': order_id, 'password': _sb_password, 'userName': _sb_login, 'amount': total})
    return result

# Запрос возврата средств оплаты заказа. используется в auto.py при возврате
def refund_order(order_id, amount):
    URL = 'https://securepayments.sberbank.ru/payment/rest/refund.do'
    total = int(amount * 100)
    result = requests.get(URL, params={'orderId': order_id, 'password': _sb_password, 'userName': _sb_login, 'amount':total})
    return result
