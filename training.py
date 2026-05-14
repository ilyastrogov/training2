# Дан список со строками. Оставьте
# в этом списке только те строки,
# которые начинаются на http://.
strings_list = ['asdadafafsfas',
                'asdasddadsa http://',
                'sdadasdadasd',
                'fjhfgjhfj',
                'cvnbcvbcvbvncnvn http://',
                '1cvnbcvbcvbvncnvn http://',
                'rtryrtutyurtyutr']


print(strings_list)

# def has_http():
#     index_list = []
#     for blin in strings_list:
#         # print(blin)
#         if 'http://' not in blin:
#             # print(blin)
#             index_list.append(blin)
#             # print(index_list)
#     for blin1 in index_list:
#         strings_list.pop(strings_list.index(blin1))
#     return strings_list
#
#
# result = has_http()
#
# print(strings_list)
# Второй вариант
def has_http2():
    return [strings_list.pop(strings_list.index(elem_string1)) for elem_string1 in
                  [elem_string for elem_string in strings_list if 'http://' not in elem_string]]
result2 = has_http2()
print(strings_list)