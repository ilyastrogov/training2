string_for = '''
	text1
	text2
	text3
	text4
	text5
'''
res = string_for.split()
print(res)
print('  ', '\n   '.join(res))

lst = [
	{
		1: (1, 2, 3),
		2: (1, 2, 3),
		3: (1, 2, 3),
	},
	{
		1: (1, 2, 3),
		2: (1, 2, 3),
		3: (1, 2, 3),
	},
	{
		1: (1, 2, 3),
		2: (1, 2, 3),
		3: (1, 2, 3),
	},
]
res = 0
for dict_num in lst:
    for elem in dict_num.values():
        res += sum(elem)
print(res)
x = 'X'
print([[number for number in range(1, 4)] for _ in range(5)])