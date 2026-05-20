from datetime import date, time, datetime, timedelta
print(datetime.now())
import time
import re
import random
import copy
# Дана некоторая строка со словами:

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
# Удалите из этой строки каждое второе слово. В нашем случае должно получится следующее:
start_time = time.time()
class ForDict:

    def sum_number(self):

        # symbols = str.maketrans('`~!@#$%^&*()_+="№?.></*-–', '                         ')
        # without_symbols = string_for_search.translate(symbols).split()

        res1 = ''
        list_of_space = []
        for elem in string_for_search:
            if not elem.isalpha():
                if res1 != '':
                    list_of_space.append(res1)
                    res1 = ''
                list_of_space.append(elem)
            else:
                res1 += elem

        count = 0
        dict_word_number = {}
        for elem1 in list_of_space:
            if elem1.isalpha():
                count += 1
                if count % 2 != 0:
                    dict_word_number[count] = elem1
            else:
                if elem1 == ' ':
                    continue
                else:
                    key = random.uniform(0.000001, 0.9)
                    dict_word_number[key] = elem1

        # new_dict = copy.deepcopy(dict_word_number)
        # all_keys_dict_word = new_dict.keys()

        new_string_text = ''
        c = 1
        for word_symbol in dict_word_number.values():
            if c == 1:
                new_string_text += word_symbol
                c += 1
            else:
                if word_symbol.isalpha():
                    new_string_text += ' ' + word_symbol
                else:
                    new_string_text += word_symbol



        return new_string_text
class PrintPosition1(ForDict):

    def __str__(self):

        return f'{super().sum_number()}'
d = PrintPosition1()
print(string_for_search)
print(d)
end_time = time.time()
execution_time = end_time - start_time
print(f"Время выполнения: {round(execution_time, 6)} секунд")