# Дан список. Удалите из него элементы с заданным значением.
strings_list = ['asdadafafsfas',
                'asdasddadsa http://',
                'sdadasdadasd',
                'fjhfgjhfj',
                'cvnbcvbcvbvncnvn http://',
                '1cvnbcvbcvbvncnvn http://',
                'rtryrtutyurtyutr']

# class DeleteElem:
#
#     def search_letter2(self, letters):
#
#         for string_one_list in [has_http.replace(letters, '$&$') for has_http in strings_list]:
#
#             if '$&$' in string_one_list:
#                 strings_list.pop(strings_list.index(string_one_list.replace('$&$', letters)))
#         return f"Список строк без элементов с заданным значением: {strings_list}"
#
# class PrintPosition(DeleteElem):
#
#     def __str__(self):
#         return super().search_letter2(input('Введите значение: '))
# d = PrintPosition()
#
# print(d)
# print(strings_list)

class DeleteElem:

    def search_letter2(self, letters):
        list_string_for_delete = [elem_string for
        elem_string in strings_list if letters in elem_string]
        for elem_for_delete in list_string_for_delete:
            strings_list.pop(strings_list.index(elem_for_delete))
        return (f"Список строк без "
                    f"элементов с "
                    f"заданным значением:")

class PrintPosition(DeleteElem):

    def __str__(self):
        return super().search_letter2(input('Введите значение: '))
d = PrintPosition()

print(d)
print(strings_list)

# class DeleteElem2:
#
#     def search_letter2(self, letters):
#         [strings_list.pop(strings_list.index(elem_for_delete)) for elem_for_delete in
#          [elem_string for elem_string in strings_list
#           if letters in elem_string]]
#
# class PrintPosition2(DeleteElem2):
#
#     def __str__(self):
#         super().search_letter2(input('Введите значение для удаления: '))
#         return 'Список строк без элементов с заданным значением:'
# d = PrintPosition2()
# print(strings_list)
# print(d)
# print(strings_list)

