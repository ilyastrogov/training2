# Дан некоторый список, например, вот такой:

numbers_list = [1, 2, 3, 4, 5, 6]
# Поменяйте местами пары элементов этого списка:

# [2, 1, 4, 3, 6, 5]

for i in range(0, len(numbers_list)-1, 2):

    numbers_list[i], numbers_list[i + 1] = numbers_list[i + 1], numbers_list[i]
print(numbers_list)