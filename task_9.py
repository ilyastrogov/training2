
import time
# Дан список:
numbers_of_lists = \
    [
        [
            [11, 12, 13],
            [14, 15, 16],
            [17, 17, 19],
        ],
        [
            [21, 22, 23],
            [24, 25, 26],
            [27, 27, 29],
        ],
        [
            [31, 32, 33],
            [34, 35, 36],
            [37, 37, 39],
        ],
    ]
# Найдите сумму элементов этого списка.
start_time = time.time()
result = 0
count1 = 0
index1 = 0
index2 = 0
for i in range(27):
    result += numbers_of_lists[index1][index2][count1]
    index1 += 1
    if index1 == 3:
        count1 += 1
        index1 = 0
    if i == 8 or i == 17:
        index2 += 1
        count1 = 0
print(result)
end_time = time.time()
execution_time = end_time - start_time
print(f"Время выполнения: {round(execution_time, 6)} секунд")
# 0.000046

start_time1 = time.time()
total = 0
for lists in numbers_of_lists:
    for sublist in lists:
        total += sum(sublist)
print(total)



end_time1 = time.time()
execution_time1 = end_time1 - start_time1
print(f"Время выполнения: {round(execution_time1, 6)} секунд")
# 0.000012