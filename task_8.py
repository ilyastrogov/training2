# Даны два числа:
#
txt1 = 12345
txt2 = 45678
# Получите кортеж цифр, которые есть и в одном, и в другом числе:
#
# (4, 5)

d = tuple(set(int(elem) for elem in str(txt2))
     & (set(int(elem) for elem in str(txt1))))
print(d)