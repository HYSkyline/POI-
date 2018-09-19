# -*- coding:utf-8 -*-

import Levenshtein
from math import *
import copy
import sys

# 待清洗文件改名为sample01.csv，字段要求见59-70行(不要OBJECTID)
# 同路径下sample04.csv为最终结果
earth_radius = float(6378137)
center_lnglat = '121.46924729440329,31.232535212299126'
similarity_std = 0.89
add = '开封'
part_list = [add + '市', add, '有限公司', '公司']
clip_list = ['(出入口)', '（出入口）', '门)', '门）']
divide_option = 1000

center_lng = float(center_lnglat.split(',')[0])
center_lat = float(center_lnglat.split(',')[1])


def main(mode):
    print 'Link Start!'
    print u'このさんプロセスあぃます.'
    print '--' * 6

    global center_lng, center_lat, divide_option
    lng_dist = lng_distance(divide_option, center_lat)
    lat_dist = lat_distance(divide_option)
    grid_parms = [[0, 0], [lng_dist / 2, 0], [0, lat_dist / 2]]

    if mode == 'check':
        for clean_i in range(3):
            # print 'Process: (' + str(clean_i) + '/3).'
            grid_dict = get_poidata('sample0' + str(clean_i + 1) + '.csv', lng_dist, lat_dist, padding=grid_parms[clean_i])
            grid_clean, grid_checklist = grid_check(grid_dict)
            data_check(grid_clean, 'sample0' + str(clean_i + 2) + '.csv', grid_checklist, 'check0' + str(clean_i + 1) + '.csv')
        checkout_merge('check00.csv')
    elif mode == 'clean':
        for clean_i in range(3):
            # print 'Process: (' + str(clean_i) + '/3).'
            grid_dict = get_poidata('sample0' + str(clean_i + 1) + '.csv', lng_dist, lat_dist, padding=grid_parms[clean_i])
            grid_clean = grid_clear(grid_dict)
            data_output(grid_clean, 'sample0' + str(clean_i + 2) + '.csv')
    print '--' * 6
    print 'Link Logout.'


def get_poidata(dataname, lng_divide, lat_divide, padding):
    global center_lng, center_lat
    poi_dict = {}
    grid_dict = {}
    cid = 0
    with open(dataname, 'r') as f:
        for line in f:
            if cid == 0:
                cid += 1
                continue
            poi_dict['pid'] = line.split(',')[0]
            poi_dict['poi_name'] = line.split(',')[1]
            poi_dict['poi_type'] = line.split(',')[2]
            poi_dict['poi_typecode'] = line.split(',')[3]
            poi_dict['poi_lng'] = float(line.split(',')[4])
            poi_dict['poi_lat'] = float(line.split(',')[5])
            poi_dict['poi_padlng'] = float(line.split(',')[4]) + padding[0]
            poi_dict['poi_padlat'] = float(line.split(',')[5]) + padding[1]
            poi_dict['poi_tel'] = line.split(',')[6]
            poi_dict['poi_pname'] = line.split(',')[7]
            poi_dict['poi_cname'] = line.split(',')[8]
            poi_dict['poi_aname'] = line.split(',')[9][:-1]

            x_index = int((poi_dict['poi_padlng'] - center_lng) / lng_divide)
            y_index = int((poi_dict['poi_padlat'] - center_lat) / lat_divide)
            grid_id = str(x_index) + 'xy' + str(y_index)

            if grid_id in grid_dict.keys():
                grid_dict[grid_id].append(copy.deepcopy(poi_dict))
            else:
                grid_dict[grid_id] = [copy.deepcopy(poi_dict)]
    # print '--' * 6
    # print 'file read.'
    # print '--' * 6
    return grid_dict


def grid_clear(grid_dict):
    global similarity_std
    process_i = 0
    for grid_i in range(len(grid_dict.keys())):
        grid = grid_dict.keys()[grid_i]
        if len(grid_dict[grid]) > 1:
            for i in range(len(grid_dict[grid]) - 1, -1, -1):
                if check_poiname(grid_dict[grid][i]['poi_name']):
                    poi_name = poi_name_cur(grid_dict[grid][i]['poi_name'])
                    for top_i in range(i - 1, -1, -1):
                        poi_name_top = poi_name_cur(grid_dict[grid][top_i]['poi_name'])
                        name_dist = Levenshtein.distance(poi_name, poi_name_top)
                        similarity = 1 - float(name_dist) / float(len(poi_name))
                        if name_dist < 2 or similarity > similarity_std:
                            # print poi_name + ' == ' + poi_name_top + ' :  ' + str(similarity)
                            grid_dict[grid].remove(grid_dict[grid][i])
                            break
                else:
                    grid_dict[grid].remove(grid_dict[grid][i])
        if (grid_i + 1) * 100 / len(grid_dict.keys()) > process_i:  # 当前进度变化
            process_i = (grid_i + 1) * 100 / len(grid_dict.keys())
            processbar_general(process_i)
    print ''
    return grid_dict


def grid_check(grid_dict):
    global similarity_std
    process_i = 0
    grid_checklist = []
    for grid_i in range(len(grid_dict.keys())):
        grid = grid_dict.keys()[grid_i]
        if len(grid_dict[grid]) > 1:
            for i in range(len(grid_dict[grid]) - 1, -1, -1):
                if check_poiname(grid_dict[grid][i]['poi_name']):
                    poi_name = poi_name_cur(grid_dict[grid][i]['poi_name'])
                    for top_i in range(i - 1, -1, -1):
                        poi_name_top = poi_name_cur(grid_dict[grid][top_i]['poi_name'])
                        name_dist = Levenshtein.distance(poi_name, poi_name_top)
                        similarity = 1 - float(name_dist) / float(len(poi_name))
                        if name_dist < 2 or similarity > similarity_std:
                            grid_checklist.append(grid_dict[grid][i])
                            grid_dict[grid].remove(grid_dict[grid][i])
                            break
                else:
                    grid_checklist.append(grid_dict[grid][i])
                    grid_dict[grid].remove(grid_dict[grid][i])
        if (grid_i + 1) * 100 / len(grid_dict.keys()) > process_i:           # 当前进度变化
            process_i = (grid_i + 1) * 100 / len(grid_dict.keys())
            processbar_general(process_i)
    print ''
    return grid_dict, grid_checklist


def lnglat_distance(lng1, lat1, lng2, lat2):
    global earth_radius
    radlat1 = radians(lat1)
    radlat2 = radians(lat2)
    lng_plus = radians(lng1) - radians(lng2)
    lat_plus = radians(lat1) - radians(lat2)
    lnglat_plus = 2 * asin(sqrt(pow(sin(lat_plus/2), 2) + cos(radlat1) * cos(radlat2) * pow(sin(lng_plus / 2), 2)))

    return abs(lnglat_plus * earth_radius)


def lng_distance(dist, lat):
    global earth_radius
    radlat = radians(lat)
    return degrees(2 * asin(float(dist) / earth_radius / 2 / cos(radlat)))


def lat_distance(dist):
    global earth_radius
    return degrees(float(dist) / earth_radius)


def poi_name_cur(pname):
    for each in part_list:
        pname.strip(each)
    return str(pname)


def check_poiname(pname):
    global clip_list
    for each in clip_list:
        if each in pname:
            return False
    return True


def data_output(grid_dict, fname):
    f = open(fname, 'w')
    f.writelines('id,name,type,typecode,lng,lat,tel,pname,cname,aname\n')
    for grids in grid_dict:
        for each in grid_dict[grids]:
            output_str = each['pid'] + ',' + each['poi_name'] + ',' + each['poi_type'] + ',' + \
                each['poi_typecode'] + ',' + str(each['poi_lng']) + ',' + str(each['poi_lat']) + ',' + \
                each['poi_tel'] + ',' + each['poi_pname'] + ',' + each['poi_cname'] + ',' + each['poi_aname']
            if output_str[-1:] == '\n':
                output_str = output_str[:-1]
            elif output_str == '\n':
                continue
            f.writelines(output_str + '\n')
    f.close()


def data_check(grid_dict, fname, grid_check, fcname):
    f = open(fname, 'w')
    f.writelines('id,name,type,typecode,lng,lat,tel,pname,cname,aname\n')
    for grids in grid_dict:
        for each in grid_dict[grids]:
            f.writelines(
                each['pid'] + ',' +
                each['poi_name'] + ',' +
                each['poi_type'] + ',' +
                each['poi_typecode'] + ',' +
                str(each['poi_lng']) + ',' +
                str(each['poi_lat']) + ',' +
                each['poi_tel'] + ',' +
                each['poi_pname'] + ',' +
                each['poi_cname'] + ',' +
                each['poi_aname'] + '\n'
            )
    f.close()
    f = open(fcname, 'w')
    for each in grid_check:
        f.writelines(
            each['pid'] + ',' +
            each['poi_name'] + ',' +
            each['poi_type'] + ',' +
            each['poi_typecode'] + ',' +
            str(each['poi_lng']) + ',' +
            str(each['poi_lat']) + ',' +
            each['poi_tel'] + ',' +
            each['poi_pname'] + ',' +
            each['poi_cname'] + ',' +
            each['poi_aname'] + '\n'
        )
    f.close()


def checkout_merge(fm_name):
    f_merge = open(fm_name, 'w')
    f_merge.writelines('id,name,type,typecode,lng,lat,tel,pname,cname,aname\n')
    for i in range(3):
        f = open('check0' + str(i + 1) + '.csv')
        contents = f.readlines()
        f.close()
        for each in contents:
            f_merge.writelines(each)
    f_merge.close()


def processbar_general(process_i):
    process_k = process_i
    if process_i % 2 == 1:
        process_string = '>' * (process_i // 2) + ' ' * ((100 - process_k) // 2 + 1)
    else:
        process_string = '>' * (process_i // 2) + ' ' * ((100 - process_k) // 2)
    sys.stdout.write('\r' + process_string + '[%s%%]' % (process_k))
    sys.stdout.flush()


if __name__ == '__main__':
    main(mode='check')
