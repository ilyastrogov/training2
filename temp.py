import re

from dateutil.parser import parse

import dateparser

string_for_search = ('Ярославский вокзал шибал свежестью '
             'и тепловозной гарью. После прокисшего '
             'плацкартного пара, после прокуренного '
             'железа тамбуров, подслащенного мочой, – '
             'тут воздух был слишком огромный: кислорода '
             'чересчур, и он сразу чифирем бил в голову.'
             'Москвы тоже было слишком, после елочных '
             'коридоров она приезжим распахивалась как космос. '
             'Укутанные люди прыгали из вагонов через ров на платформу, '
             'выгружали перехваченные липкой лентой сине-клетчатые китайские '
             'баулы, хватали их в обе руки и разгонялись по перронам в '
             'перспективу, как штурмовики на взлет по аэродромным полосам. '
             'Перспектива была дымной, и в дымке приехавшим людям брезжили '
             'дворцы, замки и высотки.Илья больше других не спешил, в потоке не'
             ' греб – давал себя нести. Нюхал московское небо, присматривался '
             'отвыкшими глазами к дали, удивлялся молча. Было ярко, как в детстве. '
             'Тусклая ноябрьская Москва резала глаза.Приехать он в Москву приехал, '
             'но попасть еще не попал. Вокзал был еще пока территорией окружной, '
             'просоленной и засаленной России. Как бангладешское посольство '
             'является во всех смыслах территорией государства Бангладеш.В '
             'конце платформы было сделано сито. Илья его уже издалека '
             'привычно разглядел поверх чужих голов. Серая форма, отъеденные морды,'
             ' глаза рыщущие, цепкие. Наметанные. Раз, раз, раз. И даже собака'
             ' служебная на цепи: полное сходство. Тут, понятно, она не для того. '
             'Тут она просто нюхает себе наркотики, взрывчатку, наверное. '
                     'Но ведь она и страх может унюхать.Илья стал смотреть в пустоту, '
                     'чтобы мимо цепких глаз, чтобы не примагнититься к ним. Стал думать '
                     'ни о чем, чтобы ничем не пахнуть.')

date_str = "13 мая 2026 года"
print(dateparser.parse(date_str).weekday()+1)
# def is_valid_date(date_str):
#     try:
#         date1 = dateparser.parse(date_str)
#         parse(str(date1))
#         return True
#     except ValueError:
#         return False
# print(is_valid_date(date_str))
# text = "abc"
# result = ""
# for char in text:
#     result += char * 3 # добавляем три копии символа
# print(result) # выведет: aaabbbccc

# class DateValidationError(Exception):
#     """Ошибка валидации даты."""
#
#     def __init__(self, date_entered, message):
#         self.date_entered = date_entered
#         self.message = f"{message}: {date_entered}"
#         super().__init__(self.message)
#
#     def get_date(self):
#         return self.date_entered
#
# class CheckDate:
#
#     def logical_processing(self, date_entered):
#         if parse(str(dateparser.parse(date_entered))):
#             return dateparser.parse(date_entered).weekday() + 1
#         else:
#             raise DateValidationError(date_entered, "Слишком большое значение возраста")
#
#
#     def validate_date(self, date_entered):
#         try:
#             # parse(str(dateparser.parse(date_entered)))
#             # return dateparser.parse(date_entered).weekday() + 1
#             self.logical_processing(date_entered)
#         except DateValidationError as e:
#             print(f"Ошибка валидации: {e}")
#             print(f"Некорректный возраст: {e.get_date()}")
# class Result(CheckDate):
#
#     def day_week(self):
#         return super().logical_processing(input('Введите дату: '))

# Обработка исключения

# activation_result = Result()
# print(activation_result.day_week())
class AgeValidationError(Exception):
    """Ошибка валидации возраста."""

    def __init__(self, age, message):
        self.age = age
        self.message = f"{message}: {age}"
        super().__init__(self.message)

    def get_age(self):
        return self.age

class CheckDate:
    def __init__(self, age):
        self.age = age

    @staticmethod
    def day_week_word(number_day):
        day_week_list = ["понедельник", "вторник", "среда", "четверг",
                         "пятница", "суббота", "воскресенье"]
        return day_week_list[number_day - 1]
    def validate_age(self):
        try:
            parse(str(dateparser.parse(self.age)))
            number_day = dateparser.parse(self.age).weekday() + 1
            print(f'{self.day_week_word(number_day)}')
        except ValueError:
            raise AgeValidationError(self.age, "Некорректное введение даты")
        # return True


# Обработка исключения
class Result:
    @staticmethod
    def day_week():
        try:
            d = CheckDate(input('Введите дату: '))
            return d.validate_age()
        except AgeValidationError as e:
            print(f"Ошибка валидации: {e}")
            print(f"Попробуйте ещё: ")
            activation_result1 = Result()
            activation_result1.day_week()

activation_result = Result()
activation_result.day_week()
# class AgeValidationError(Exception):
#     """Ошибка валидации возраста."""
#
#     def __init__(self, age, message):
#         self.age = age
#         self.message = f"{message}: {age}"
#         super().__init__(self.message)
#
#     def get_age(self):
#         return self.age
#
# class CheckDate:
#     def __init__(self, age):
#         self.age = age
#
#     def validate_age(self):
#         if self.age < 0:
#             raise AgeValidationError(self.age, "Возраст не может быть отрицательным")
#         elif self.age > 150:
#             raise AgeValidationError(self.age, "Слишком большое значение возраста")
#         return True
#
#
# # Обработка исключения
# try:
#     d = CheckDate(5000)
#     d.validate_age()
# except AgeValidationError as e:
#     print(f"Ошибка валидации: {e}")
#     print(f"Некорректный возраст: {e.get_age()}")
