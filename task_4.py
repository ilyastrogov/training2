# Выведите в консоль все числа в
# промежутке от 10 до 1000,
# сумма первой и второй цифры которых равна пяти.

class SearchNumbers:

    def search_numbers(self):
        return [number for number in range(14, 510)
                if int(str(number)[0]) + int(str(number)[1]) == 5]

class PrintPosition2(SearchNumbers):

    def __str__(self):

        return (f"Все числа впромежутке от 10 до 1000, "
                f"сумма первой и второй цифры которых равна пяти "
                f"{super().search_numbers()}")
d = PrintPosition2()

print(d)
