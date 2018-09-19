# -*- coding:utf-8 -*-

import os

path = 'data/'
process = len(os.listdir(path))

for i in range(process + 1, 100):
	print '--> ' + str(i)
	f = open(path + str(i) + '.csv', 'w')
	if i % 5 == 0:
		raise NameError
