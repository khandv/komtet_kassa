from math import modf


# Проверка весового товара
def verif_weight(quantity):
    if modf(quantity)[0] != 0:
        return True


if __name__ == '__main__':
    pass
