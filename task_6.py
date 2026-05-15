# Дан словарь:
#


dict_numbers = {
	'a': 1,
	'b': 2,
	'c': 3,
	'd': 4,
}
# Получите список его значений:
#
# [1, 2, 3, 4]
class ListValue:

    def search_value(self):
        return list(dict_numbers.values())

class PrintPosition1(ListValue):

    def __str__(self):
        return f'Список значений: {super().search_value()}'
d = PrintPosition1()

print(d)