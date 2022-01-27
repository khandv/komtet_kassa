from colorama import Fore, Style
from colorama import init
from re import search
from auto import check_type
from pprint import pprint
import get_lib
import rbs


def processing():
    init()
    while True:
        # Ввод номера заказа
        order_number_input = input("Введите номер заказа ('0'- выход) : ")
        # Проверка на пустой ввод, ввод не цифры и 0 - выход
        if search(r'\D+', order_number_input) or order_number_input == '':
            print(Fore.RED + 'Номер заказа состоит только из цифр.' + Style.RESET_ALL)
            continue
        elif int(order_number_input) == 0:
            exit()
        order_details = get_lib.get_order_details(int(order_number_input))
        # pprint(order_details)
        shop = get_lib.get_shop(order_details[8])
        region = get_lib.get_region(shop[1])
        # Печатаем детали заказа
        print('%-20s%s' % ('Заказ №', order_details[0]))
        print('%-20s%s' % ('Дата заказа', order_details[4]))
        print('%-20s%s' % ('Статус', get_lib.get_status_order(int(order_number_input))))
        print('%-20s%s' % ('Клиент', order_details[1]))
        print('%-20s%s' % ('Получатель', order_details[2]))
        print('%-20s%s' % ('E-mail', get_lib.get_email(int(order_number_input))))
        print('%-20s%s' % ('Регион', region[0]))
        print('%-20s%s' % ('Магазин', shop[0]))
        print('=' * 55, 'Товар ' + '=' * 55)
        order_goods = get_lib.get_goods_of_order(order_number_input)
        counter = 1
        position_total = 0
        print('%-4s%-80s%-10s%-10s%-10s' % ('№', 'Позиция', 'Кол-во', 'Цена', 'Сумма'))
        # pprint(order_goods)
        for good in order_goods:
            print('%-4d%-80s%-10.2f%-10.2f%-10.2f%-5s' % (counter, good[1], good[3], good[2], good[4], str(good[6])))
            counter += 1
            position_total += good[4]
        print('=' * 55, 'Оплаты ' + '=' * 54)
        sber_id = get_lib.get_sber_id(int(order_number_input))
        payment_state = rbs.get_order_from_sber(sber_id)
        holded_sum = float(payment_state['paymentAmountInfo']['approvedAmount'] / 100)
        finish_sum = float(payment_state['paymentAmountInfo']['depositedAmount'] / 100)
        refunded_amount = float(payment_state['paymentAmountInfo']['refundedAmount'] / 100)
        if payment_state['orderStatus'] == 2:
            payment_state_ru = 'Выполнено'
            color_state = Fore.GREEN
        if payment_state['orderStatus'] == 1:
            payment_state_ru = 'Холдирование'
            color_state = Fore.YELLOW
        if payment_state['orderStatus'] == 3:
            payment_state_ru = 'Отмена'
            color_state = Fore.RED
        if payment_state['orderStatus'] == 4:
            payment_state_ru = 'Возврат'
            # if holded_sum != 0:
            #     payment_state_ru = 'Полный возврат'
            # else:
            #     payment_state_ru = 'Частичный возврат'
            color_state = Fore.CYAN
        print('%-20s%s' % ('Статус', color_state + payment_state_ru + Style.RESET_ALL))
        # Вынимаем и выводим оплаты

        print('%-20s%s' % ('Холдирование', holded_sum))
        print('%-20s%s' % ('Завершение', finish_sum))
        print('%-20s%s' % ('Возврат', refunded_amount))
        print('%-20s%s' % ('Разница', holded_sum - finish_sum))
        print('=' * 55, 'Чеки ' + '=' * 56)
        checks = get_lib.get_checks_order(int(order_number_input))
        check_count = 0

        for check in checks:
            operation = 'Продажа' if check['type_of_check'] == 'sell' else 'Возврат'
            print('%-10s%-10.2f %-25s%s' % (operation, check['total'], check['date_time'], check['url']))
            check_count += 1
            check_total = check['total']

        print('=' * 53, ' Проверки ' + '=' * 53)
        delta = float(payment_state['paymentAmountInfo']['depositedAmount'] / 100) - order_details[7]
        print('%-20s%s' % ('Сумма oc_orders', order_details[7]))
        print('%-20s%s' % ('Сумма по строкам', position_total))
        print('%-20s%s' % ('Сумма по банку', finish_sum))

        if check_count == 1:
            print('%-20s%s' % ('Сумма по чеку', check_total))
            print('%-20s%s' % ('Переплата', delta))

        if delta > 0:
            if input('Провести возврат на сумму %.2f?: ' % delta) == 'Y':
                # вызываем метод refund_order из rbs.py (возврат)
                res = rbs.refund_order(order_details.sber_id, delta)
                print(res.content)

        if input('Сформировать чек? ') == 'Y':
            intent_check = 'sellReturn' if input('Тип чека:\n1-Приход\n2-Возрат\n?>') == '2' else 'sell'
            # if input('Отключить контроль суммы? ') == 'Y':
            #     order_details.good = True
            # else:
            #     order_details.good = False
            # if input('Корректировать External_id? ') == 'Y':
            #     correct = True
            # else:
            #     correct = False
            if intent_check == 'sellReturn':
                if input('Провести возврат на %.2f руб. через банк? ' % finish_sum) == 'Y':
                    rbs.refund_order(sber_id, finish_sum)
            # print(intent_check)
            check_type(order_number_input, intent_check)
        else:
            order_details = None
            continue


if __name__ == '__main__':
    processing()
