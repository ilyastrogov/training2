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

def has_http(strings_list):
    index_list = []
    for blin in [line.split('http://') for line in strings_list]:

        if '' not in blin:
            # print(blin)
            index_list.append(blin[0])
            # print(index_list)
    for blin1 in index_list:
        strings_list.pop(strings_list.index(blin1))
    return strings_list


result = has_http(strings_list)

print(strings_list)
