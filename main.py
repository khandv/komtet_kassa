from datetime import date, datetime, timedelta
from time import sleep
import get_lib
from pprint import pprint
import add_lib
import verification


def configure_check(order_id, intent):
    check = {}
    details = get_lib.get_order_details(order_id)
    goods = get_lib.get_goods_of_order(order_id)
    check['intent'] = intent
    check['external_id'] = str(order_id) + intent
    check['sno'] = 0
    check['user'] = get_lib.get_email(order_id)
    for good in goods:



        mark_code_raws = get_lib.get_mark(good[-1])




    #pprint(details)
    pprint(goods)
    pprint(check)

    # return check


if __name__ == '__main__':
   configure_check(331578, 'sell')
