import settings
import requests


# запрос в сбер по id_sb (sber_id), возвращает результат в json. используется в bitrix.py
def get_order_extended(id_sb):
    url = 'https://securepayments.sberbank.ru/payment/rest/getOrderStatusExtended.do'
    params = {'orderId': id_sb,
              'userName': settings.sb_login,
              'password': settings.sb_password}
    req = requests.get(url, params=params)
    return req.json()


# Запрос возврата средств оплаты заказа. используется в auto.py при возврате
def refund_order(order_id, amount):
    url = 'https://securepayments.sberbank.ru/payment/rest/refund.do'
    total = int(amount * 100)
    params = {'orderId': order_id,
              'password': settings.sb_password,
              'userName': settings.sb_login,
              'amount': total}
    return requests.get(url, params=params)


if __name__ == '__main__':
    pass
