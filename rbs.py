import settings
import requests
from pprint import pprint


# запрос в сбер по sber_id
def get_order_from_sber(sber_id):
    try:
        url = 'https://securepayments.sberbank.ru/payment/rest/getOrderStatusExtended.do'
        params = {'orderId': sber_id,
                  'userName': settings.sb_login,
                  'password': settings.sb_password}
        req = requests.get(url, params=params)
        return req.json()
    except Exception as error:
        print('Нет ответа от сервера сбербанка', error)


# Запрос возврата средств оплаты заказа. используетс при возврате
def refund_order(order_id, amount):
    url = 'https://securepayments.sberbank.ru/payment/rest/refund.do'
    total = int(amount * 100)
    params = {'orderId': order_id,
              'password': settings.sb_password,
              'userName': settings.sb_login,
              'amount': total}
    return requests.get(url, params=params)


if __name__ == '__main__':
    pprint(get_order_from_sber('2bf23569-aa35-7292-a741-8612020c5ad7'))
    print(get_order_from_sber('2bf23569-aa35-7292-a741-8612020c5ad7')['errorCode'] == '0')
