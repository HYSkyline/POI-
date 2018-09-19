# -*- coding:utf-8 -*-

import os
import time

path = 'data/'
previous_process = 0

err_num = 0

for i in range(12):
	current_process = len(os.listdir(path))
	if current_process == previous_process:
		os.system('python2 M.py')
		err_num += 1
	else:
		previous_process = current_process
		err_num = 0
	if err_num > 5:
		print 'finish.'
		exit()
	time.sleep(5)
	i = i - 1
