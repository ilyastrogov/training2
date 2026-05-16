# Дан следующий словарь:
import time
dct = {
	1: {
		1: 11,
		2: 12,
		3: 13,
	},
	2: {
		1: 21,
		2: 22,
		3: 23,
	},
	3: {
		1: 24,
		2: 25,
		3: 26,
	},
}
# Найдите сумму элементов этого словаря.

start_time = time.time()
class SumNumbers:

    def sum_number(self):
        result = 0
        for elem_numbers in dct.values():
            result += sum(elem_numbers.values())

        return f"Один делитель: {result}"

class PrintPosition1(SumNumbers):

    def __str__(self):

        return f'{super().sum_number()}'
d = PrintPosition1()

print(d)
end_time = time.time()
execution_time = end_time - start_time
print(f"Время выполнения: {round(execution_time, 6)} секунд")