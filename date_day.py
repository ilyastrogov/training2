from datetime import date, time, datetime, timedelta
import time
from dateutil.parser import parse

import dateparser
print(datetime.now())




# Создаём календарь для России
# cal = Russia()
#
# # Получаем все даты выходных (субботы и воскресенья) в России в 2023 году
# weekends_2023 = cal.WEEKEND_DAYS(date(2023, 1, 1), date(2023, 12, 31))
#
# # Выводим список дат выходных
# for weekend_date, weekday_name in weekends_2023:
#     print(f"{weekend_date}: {weekday_name}")

# from dateutil import parser

# date_str1 = "2024-09-16"  # ISO-формат
# date_str2 = "16 сентября 2024 года"  # более понятный для человека формат
# date_str3 = "09  24 16"  # европейский формат
#
# date1 = parser.parse(date_str1)
# # date2 = parser.parse(date_str2)
# date3 = parser.parse(date_str3)
#
# print(date1)  # напечатает объект datetime
# # print(date2)
# print(date3)



date_str = "16 сентября 2024 года"
print(dateparser.parse(date_str))
# date_obj = parser.parse(date_str, fuzzy_with_tokens=True)
# print(date_obj)  # Вывод: 2024-09-16 00:00:00


# class ValidationError(Exception):
#     """Исключение для ошибок валидации данных."""
#
#     def __init__(self, date_entered, message='Некорректный ввод даты'):
#         self.date_entered = date_entered
#         self.message = message
#         super().__init__(self.message)
#
#     def get_date(self):
#         return self.date_entered


class DateValidationError(Exception):
    """Ошибка валидации даты."""

    def __init__(self, date_entered, message):
        self.date_entered = date_entered
        self.message = f"{message}: {date_entered}"
        super().__init__(self.message)

    def get_date(self):
        return self.date_entered

class Weekends:
    @staticmethod
    def weekends_days(number_day):

        weekend_days = []
        for day in (number_day + timedelta(x) for x in range((date.today() - number_day).days + 1)):
            if day.weekday() >= 5:  # 5 — суббота, 6 — воскресенье
                weekend_days.append(day)
        # new_weekend_days =
        return f"{weekend_days}"

class CheckDate:
    def __init__(self, date_entered):
        self.date_entered = date_entered
    def validate_date(self):
        try:
            parse(self.date_entered)
            # return f'{self.weekends_days(dateparser.parse(self.date_entered).date())}'
            return True
        except ValueError:
            return False
            # raise DateValidationError(self.date_entered, "Некорректное введение даты")

class ExpandDate:
    @staticmethod
    def expand_the_date(date1):
        print('exp', date1)
        map_space = str.maketrans('~`!@#$%^&*()-_–=+":?.,><//''', '                          ')
        mod_date = date1.translate(map_space).split()
        mod_date[0], mod_date[2] = mod_date[2], mod_date[0]
        return dateparser.parse('.'.join(mod_date)).date()

class Result:
    def __init__(self, date1):
        self.date1 = date1
        self.reverse_date1 = ''

    def active_classes(self):
        try:
            CheckDate(self.date1).validate_date()
            self.reverse_date1 = ExpandDate().expand_the_date(self.date1)
            return f'{Weekends().weekends_days(self.reverse_date1)}'
            # return True
        except DateValidationError as e:
            print(f"Ошибка валидации: {e}")
            print(f"Попробуйте ещё: ")
            # activation_result1 = Result(self.date1)
            # activation_result1.day_week()
start_time = time.time()
activation_result = Result('01.04.2026')
print(activation_result.active_classes())
end_time = time.time()
execution_time = end_time - start_time
print(f"Время выполнения: {round(execution_time, 6)} секунд")

if __name__ == '__main__':
    pass