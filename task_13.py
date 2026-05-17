import time
# Дан текст:

text = '''
	a-1
	b-2
	c-3
	d-4
	e-5
'''
# Разбейте эту строку в словарь следующим образом:

# {
# 	'a': 1,
# 	'b': 2,
# 	'c': 3,
# 	'd': 4,
# 	'e': 5,
# }

start_time = time.time()
class ForDict:

    def sum_number(self):

        return dict(zip([elem for elem in text if elem.isalpha()], [elem for elem in text if elem.isdigit()]))
class PrintPosition1(ForDict):

    def __str__(self):

        return f'{super().sum_number()}'
d = PrintPosition1()

print(d)
end_time = time.time()
execution_time = end_time - start_time
print(f"Время выполнения: {round(execution_time, 6)} секунд")