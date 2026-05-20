from datetime import date, time, datetime, timedelta
import time
from dateutil.parser import parse

import dateparser
print(datetime.now())

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


class ValidationError(Exception):
    """Исключение для ошибок валидации данных."""

    def __init__(self, date_entered, message='Некорректный ввод даты'):
        self.date_entered = date_entered
        self.message = message
        super().__init__(self.message)

    def get_date(self):
        return self.date_entered


class DateValidationError(Exception):
    """Ошибка валидации возраста."""

    def __init__(self, date_entered, message):
        self.date_entered = date_entered
        self.message = f"{message}: {date_entered}"
        super().__init__(self.message)

    def get_date(self):
        return self.date_entered

class CheckDate:
    def __init__(self, date_entered):
        self.date_entered = date_entered

    @staticmethod
    def day_week_word(number_day):
        day_week_list = ["понедельник", "вторник", "среда", "четверг",
                         "пятница", "суббота", "воскресенье"]
        return day_week_list[number_day - 1]
    def validate_age(self):
        try:
            parse(str(dateparser.parse(self.date_entered)))
            number_day = dateparser.parse(self.date_entered).weekday() + 1
            print(f'{self.day_week_word(number_day)}')
        except ValueError:
            raise DateValidationError(self.date_entered, "Некорректное введение даты")


class Result:
    @staticmethod
    def day_week():
        try:
            d = CheckDate(input('Введите дату: '))
            return d.validate_age()
        except DateValidationError as e:
            print(f"Ошибка валидации: {e}")
            print(f"Попробуйте ещё: ")
            activation_result1 = Result()
            activation_result1.day_week()
start_time = time.time()
activation_result = Result()
activation_result.day_week()
end_time = time.time()
execution_time = end_time - start_time
print(f"Время выполнения: {round(execution_time, 6)} секунд")