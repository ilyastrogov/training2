# Дано некоторое число:

number = 3514286970351428697035142869703514286970
# Отсортируйте цифры этого числа. В нашем случае должно получится следующее:

# 12345
num_str = [int(elem) for elem in str(number)]
number1 = 0

for e in range(len(num_str) - 1):
    for i in range(len(num_str) - 1):
        if num_str[i] > num_str[i + 1]:
            num_str[i], num_str[i + 1] = num_str[i + 1], num_str[i]
            # print(num_str)
    number1 = int(''.join(str(elem) for elem in num_str))
print(number1)
# print(number1)

# 1 Понять почему нельзя изменить измененный номер
# 2 Что-бы дважды изменить строку нужно создать её через список
new_num = [int(elem) for elem in str(number1)]
for e in range(len(new_num) - 1):
    for i in range(len(new_num) - 1):
        if new_num[i] < new_num[i + 1]:
            new_num[i], new_num[i + 1] = new_num[i + 1], new_num[i]
            # print(num_str)
    number = int(''.join(str(elem) for elem in new_num))
    # print(number)
print(number)