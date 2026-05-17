# Дан следующий словарь:
import time
dct = {
	1: {
		1: {
			1: 111,
			2: 112,
			3: 113,
		},
		2: {
			1: 121,
			2: 122,
			3: 123,
		},
	},
	2: {
		1: {
			1: 211,
			2: 212,
			3: 213,
		},
		2: {
			1: 221,
			2: 222,
			3: 223,
		},
	},
	3: {
		1: {
			1: 311,
			2: 312,
			3: 313,
		},
		2: {
			1: 321,
			2: 322,
			3: 323,
		},
	},
}
# Найдите сумму элементов этого словаря.

start_time = time.time()
class SumNumbers:

    def sum_number(self):
        result = 0
        for elem_numbers in dct.values():
            for elem in elem_numbers.values():
                result += sum(elem.values())

        return f"Один делитель: {result}"

class PrintPosition1(SumNumbers):

    def __str__(self):

        return f'{super().sum_number()}'
d = PrintPosition1()

print(d)
end_time = time.time()
execution_time = end_time - start_time
print(f"Время выполнения: {round(execution_time, 6)} секунд")