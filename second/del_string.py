# Дана некоторая строка:

numbers_string = '1 22 333 4444 22 5555 1 22222 333 999999 22'
# Удалите из этой строки все подстроки,
# в которых количество символов больше трех.
# В нашем случае должно получится следующее:

# '1 22 333 22 1'
temp_word = ''
index = -1
for e in numbers_string:
    index += 1
    if e.isdigit():

        temp_word += e
    else:
        print(temp_word)

        if len(temp_word) > 3:
            numbers_string = (numbers_string[:index - (len(temp_word) + 1)] +
                              numbers_string[index:])
            print('one', numbers_string)
            index -= (len(temp_word) + 1)
            temp_word = ''
        else:
            temp_word = ''
print(numbers_string)
