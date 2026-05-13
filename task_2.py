# Дана некоторая строка.
# Найдите позицию первого нуля в строке.
string_to_nule = 'asdlkj sdf0 sdffsdxcvx0 sdfsd'
# Вариант 1
# class FirstLetter:
#
#     def search_letter(self, letter):
#         for i in string_to_nule:
#             if letter == i:
#                 break
#         return f"Позицию первого нуля в строке: {string_to_nule.index(letter)}"
#
#     def __str__(self):
#         letter = input('Введите символ для поиска: ')
#         return FirstLetter.search_letter(self, letter)
#
# search_first_letter = FirstLetter()
# print(search_first_letter)

# Вариант 2
class FirstLettr2:

    def search_letter2(self, letter):
        for i in string_to_nule:
            if letter == i:
                break
        return f"Позицию первого нуля в строке: {string_to_nule.index(letter)}"

class PrintPosition(FirstLettr2):

    def __str__(self):
        return super().search_letter2(input('Введите символ для поиска: '))
d = PrintPosition()
print(d)
# class Cookie:
#     def __init__(self, flavor, filling):
#         self.flavor = flavor  # Атрибут экземпляра: вкус
#         self.filling = filling  # Атрибут экземпляра: начинка
#
#     def show_info(self):
#         return f"Печенье\n Вкус: {self.flavor}\nНачинка: {self.filling}"
#
#
# vanilla_cookie = Cookie("ваниль", "клубника")
# print(vanilla_cookie.show_info())

