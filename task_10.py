# Дано число. Проверьте, что у этого числа
# есть только один делитель, кроме него самого и единицы.
import time


start_time = time.time()
class SearchDivider:

    def search_word(self, number):
        # result = [divider for divider in range(2, number)
        #           if (number / divider).is_integer()]
        result = []
        for divider in range(2, number):
            if (number / divider).is_integer():
                result.append(divider)
                if len(result) > 1:
                    return f"Много делителей: {result}"
        return f"Один делитель: {result}"

class PrintPosition1(SearchDivider):

    def __str__(self):

        return f'{super().search_word(int(input('Введите число для проверки: ')))}'
d = PrintPosition1()

print(d)
end_time = time.time()
execution_time = end_time - start_time
print(f"Время выполнения: {round(execution_time, 6)} секунд")

start_time1 = time.time()
def check(n):
    k = 2
    while k * k <= n:
        if n % k == 0:
            if n // k != k:
                return False
            else:
                return True
        k += 1
    return False


print(check(int(input("n="))))
end_time1 = time.time()
execution_time = end_time1 - start_time1
print(f"Время выполнения: {round(execution_time, 6)} секунд")