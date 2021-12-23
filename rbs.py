import settings
import requests
from pprint import pprint
import functools


# Этот декоратор заново запускает функцию в случае возникновения исключений. Кол-во максимум = max_tries
def retry(max_tries):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for n in range(1, max_tries + 1):
                # noinspection PyBroadException
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if n == max_tries:
                        raise

        return wrapper

    return decorator


# запрос в сбер по sber_id
@retry(max_tries=100)
def get_order_from_sber(sber_id):
    # try:
    url = 'https://securepayments.sberbank.ru/payment/rest/getOrderStatusExtended.do'
    params = {'orderId': sber_id,
              'userName': settings.sb_login,
              'password': settings.sb_password}
    req = requests.get(url, params=params)
    return req.json()
    # except Exception as error:
    #     print('Нет ответа от сервера сбербанка', error)


# Запрос возврата средств оплаты заказа. используетс при возврате
@retry(max_tries=100)
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
