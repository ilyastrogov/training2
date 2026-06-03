import dateparser
from datetime import date, timedelta
from dateutil.parser import parse
# class ExpandDate:
#     def __init__(self, date1):
#         self.date1 = date1
#     def expand_the_date(self):
#         map_space = str.maketrans('~`!@#$%^&*()-_–=+":?.,><//''', '                          ')
#         mod_date = self.date1.translate(map_space).split()
#         mod_date[0], mod_date[2] = mod_date[2], mod_date[0]
#
#         return f'{'.'.join(mod_date)}'
# class Result(ExpandDate):
#
#
#     def blin(self):
#         return f'1{self.expand_the_date()}'
#
# d= Result('20.05.2026')
#
# print('2', d.blin())
# print(dateparser.parse('2026.05.07').date().year)

from workalendar.europe import Russia
cal = Russia()
def get_weekend_days(start_date, end_date):
    weekend_days = []
    for day in (start_date + timedelta(x) for x in range((end_date - start_date).days + 1)):
        if day.weekday() >= 5:  # 5 — суббота, 6 — воскресенье
            weekend_days.append(day)
    return weekend_days

# Пример использования
start = date(2026, 5, 1)
end = date(2026, 5, 29)
print(date(2026, 5, 1))
print(date(2026, 5, 29))
print(date.today())
# print(date(2026, 5, 29))
weekend_days_in_period = get_weekend_days(start, end)
for i in weekend_days_in_period:

    print(i)
print(parse(str(dateparser.parse('2026.05.01'))))
print(parse(str(dateparser.parse('2026.05.01'))))
print('2026.05.01'.isdigit())
# # Получаем список выходных дней в заданном периоде
# weekend_days = [date for date in range(cal(start_date), end_date) if date.weekday() >= 5]  # 5 и 6 — суббота и воскресенье
#
# print(weekend_days)

# def get_weekend_days(start_date, end_date):
#     weekend_days = []
#     current_date = start_date
#     while current_date <= end_date:
#         if current_date.weekday() >= 5:  # 5 = суббота, 6 = воскресенье
#             weekend_days.append(current_date)
#         current_date += date.weekday()
#     return weekend_days
# # Создаём календарь для России
#
#
# # Получаем все даты выходных (субботы и воскресенья) в России в 2023 году
# weekends_2023 = cal.get_weekend_days(date(2026, 1, 1), date(2026, 12, 31))
#
# # Выводим список дат выходных
# print(weekends_2023)
# for weekend_date, weekday_name in weekends_2023:
#     print(f"{weekend_date}: {weekday_name}")