# -*- coding:utf-8 -*-

from coordTransform_utils import gcj02_to_wgs84
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


'''
used for POI project only.
Format stardard:
....	E		F		......
....	lng 	lat		......
....	120		30		......
!! lnglat must be the 5th and 6th column.
'''

filename = u'ZZ-SUM'


def processbar_general(process_i):
    process_k = process_i
    if process_i % 2 == 1:
        process_string = '>' * (process_i // 2) + ' ' * ((100 - process_k) // 2 + 1)
    else:
        process_string = '>' * (process_i // 2) + ' ' * ((100 - process_k) // 2)
    sys.stdout.write('\r' + process_string + '[%s%%]' % (process_k + 1))
    sys.stdout.flush()

f = open(filename + '.csv', 'r')
file = f.readlines()
titles = file[:1][0]
contents = file[1:]
cols_num = len(titles.split(','))
f.close()

f = open(filename + '_trans.csv', 'w')
f_err = open(filename + '_err.csv', 'w')
f.writelines(titles.replace('LNG', 'lng_trans').replace('LAT', 'lat_trans'))
for i in range(len(contents)):
	# print contents[i]
	# print len(contents[i].split(','))
	try:
		content = contents[i].split(',')
		gcj02lng = content[4]
		gcj02lat = content[5]
		res = gcj02_to_wgs84(float(gcj02lng), float(gcj02lat))
		plng = str(res[0])
		plat = str(res[1])
		f.writelines(','.join(contents[i].split(',')[:4]) + ',' + plng + ',' + plat + ',' + ','.join(contents[i].split(',')[6:]))
		process_i = i * 100 / len(contents)
		processbar_general(process_i)
	except Exception as e:
		print str(i + 2)
		f_err.writelines(str(i + 2) + '\n')
	# exit()
print ''
f_err.close()
f.close()
