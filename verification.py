from math import modf


# Проверка весового товара
def verif_weight(quantity):
    if modf(quantity)[0] != 0:
        return True


# Генерация HEX вида кода марки
def mark_to_tag(mark_code_raw):
    for i in ('(21)', '(01)'):
        mark_code_raw = mark_code_raw.replace(i, '')
    gtin = int(mark_code_raw[0:14])
    gtin_hex = str((hex(gtin)).upper()[2:])
    # добавляет ведущие нули до 12 знаков
    if len(gtin_hex) < 12:
        gtin_hex = '0' * (12 - len(gtin_hex)) + gtin_hex
    # добавляет префикс
    prefix = '0005'
    gtin_hex = prefix + gtin_hex
    gtin_hex = ''.join(gtin_hex[i:i + 2] for i in range(0, len(gtin_hex), 2))
    mark_hex = ''
    mark = mark_code_raw[14:21]
    for i in mark:
        mark_hex = mark_hex + hex(ord(i))[2:]
    mark_hex = ''.join(mark_hex[i:i + 2] for i in range(0, len(mark_hex), 2))
    mark_to_send = gtin_hex + mark_hex
    return mark_to_send


if __name__ == '__main__':
    pass
