# Дан список. Удалите из него элементы с заданным значением.
strings_list = ['asdadafafsfas',
                'asdasddadsa http://',
                'sdadasdadasd',
                'fjhfgjhfj',
                'cvnbcvbcvbvncnvn http://',
                '1cvnbcvbcvbvncnvn http://',
                'rtryrtutyurtyutr']
class DeleteElem:

    def search_letter2(self, letters):

        for string_one_list in [has_http.replace(letters, '$&$') for has_http in strings_list]:

            if '$&$' in string_one_list:
                print(string_one_list)
                strings_list.pop(strings_list.index(string_one_list.replace('$&$', letters)))
        return f"Список строк без элементов с заданным значением: {strings_list}"

class PrintPosition(DeleteElem):

    def __str__(self):
        return super().search_letter2(input('Введите значение: '))
d = PrintPosition()
print(d)