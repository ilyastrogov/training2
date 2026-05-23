# def infinite_sequence():
#     n = 0
#     while True:
#         yield n
#         n += 1
# g = infinite_sequence()
# for _ in range(1000):
#     # print(next(g), end=" ")
#     print(next(g))

import time
import re

# pattern = r"[,!?–]"  # ищет запятую, восклицательный или вопросительный знак

# if re.search(pattern, text):
    # return [name, age, country]

# name, age, country = get_user_data()


class NumbersError(Exception):
    pass

class EvenError(NumbersError):
    pass

class CheckEven:
    def no_even(self, number):
        # print(number + 1)
        if number % 2 == 0:
            return True
        raise EvenError(number)

# Пример использования
# numbers = [3, 5, 8, 9]
# def cycle():
# for number in numbers:
#
#     try:
#         # if no_even(number):
#         print("Сумма чисел:", no_even())
#     except EvenError as e:
#         # print(e)
#         # pass
#     # finally:
#         continue
    # for i in list(e):

    # print(f"Произошла ошибка: {e}")

str_text = ('Ярославский, вокзал шибал свежестью '
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
                             'Но ведь она и страх может унюхать. Илья стал смотреть в пустоту, '
                             'чтобы мимо цепких глаз, чтобы не примагнититься к ним. Стал думать '
                             'ни о чем, чтобы ничем не пахнуть.')


class TextSplitBySpace:
    def __init__(self, text_one):
        self.text_two = text_one.split()
    def split_by_space(self):
        return self.text_two

class SendingWord(TextSplitBySpace, CheckEven):
    def sending(self):
        text_list = self.split_by_space()
        index = -2
        for _ in range(len(text_list) // 2):
            index += 2
            yield text_list[index]
            # print(text_list[index][len(text_list[index]) - 1:])
            # yield self.split_by_space()[index]
            # try:
            #     self.no_even(index)
            #     yield word

            # except EvenError:
            #     continue
start_time1 = time.time()
active_sand_word = SendingWord(str_text)
# words_list = active_sand_word.sending()
new_str = ''
for word in active_sand_word.sending():
    new_str += word + ' '
print(new_str)
end_time1 = time.time()
execution_time = end_time1 - start_time1
print(f"Время выполнения: {round(execution_time, 6)} секунд")
# g = infinite_sequence()
#
# for _ in range(1):
#     # f = next(g(next(g(str_text))))
#     # r = f.replace(' ', '', 1)
#     print(next(g).replace(' ', ''))


