# -*- coding:utf-8 -*-

import urllib2
import json
import threading
import os
import sys
import time

'''
1.
GRID.csv文件需要构建如下格式
MissionID, NWLNG, NWLAT, SELNG, SELAT
需要去除表格抬头首行

2.
需要新建data文件夹以存放线程数据
需要手动输入GRID文件名称
需要填写项目名称

3.
已完成多线程、断线重连、负载均衡、高速化改造
未完成外部控制
'''

# 确保程序运行环境为UTF-8，避免由于数据内容超出中英文范畴而报错
reload(sys)
sys.setdefaultencoding('utf-8')


def main():
    print 'Link Start!'
    print '--' * 6

    # 确认是否存在进度
    url_list_done = get_startpoint(thread_num)
    # print 'exist point: ' + str(exist_point)
    # print 'exist page:' + str(exist_page)
    # print '--' * 6
    # exit()

    # 计算此次采集的目标URL列表
    url_list = get_target(url_list_done)
    # exit()
    global typecode
    # 构造用于生成完整URL的typecode
    typecode = get_typecode()

    # 开始构造线程池并采集信息
    thread_init(get_info, url_list[:], thread_num)
    # 采集信息汇总, 准备进行文本处理
    res_sum()

    print 'Link Logout.'


def get_startpoint(num):
    # 记录已经完成的格网ID
    mission_id_list =[]
    try:
        for i in range(1, num + 1):
            f = open(data_path + output_file_pre + '-' + str(i) + '.csv', 'r')
            contents = f.readlines()
            f.close()
            if len(contents) > 1:
                print u'线程%d进度读取中...' % i
                for each in contents:
                    spd = each.split(',')[-1]
                    mission_id = int(each.split(',')[-1][:-1])
                    mission_id_list.append(mission_id)
                # print u'线程%d已完成格网数量:%d' % (i, len(mission_id_list))
    except IOError as e:
        # 首次运行程序时没有已存在的采集信息文件, 可以省略此步骤
        pass
    mission_id_list = list(set(mission_id_list))
    # copy_urldone(mission_id_list)
    print u'任务列表重生成中.'
    print '--' * 6
    # print u'共计已完成网格%d个' % len(mission_id_list)
    return mission_id_list


def copy_urldone(url_done_list):
    # 记录已完成的格网并按GRID格式输出, 用于手动检查当前进度(断线重连测试用)
    # 通过input_file_name调用完整列表, 通过url_done_list进行筛选
    f = open(input_file_name, 'r')
    contents = f.readlines()
    f.close()
    # 写入done.csv文件
    f_done = open(output_file_pre + '_done.csv', 'w')
    for each in contents:
        mission_id = int(each.split(',')[0])
        if mission_id in url_done_list:
            f_done.writelines(each)
    f_done.close()
    print u'当前进度汇总完成.'


def get_target(mission_done_list):
    # 已完成格网与全任务列表对比, 反向选出未完成格网
    f = open(input_file_name, 'r')
    contents = f.readlines()
    f.close()
    mission_list = []
    for each in contents:
        mission_id = int(each.split(',')[0])
        if mission_id not in mission_done_list:
            nw_lng = each.split(',')[1]
            nw_lat = each.split(',')[2]
            se_lng = each.split(',')[3]
            se_lat = each.split(',')[4][:-1]
            mission_list.append({
                'id': mission_id,
                'lnglat': nw_lng + ',' + nw_lat + '|' + se_lng + ',' + se_lat
            })
    print u'任务进度(%d/%d)' % (len(mission_done_list), len(contents))
    print '--' * 6
    return mission_list


def get_typecode():
    f = open('typecode.csv', 'r')
    types = f.readlines()
    f.close()
    type_list = []
    for each in types[1:]:
        type_list.append(each.split(',')[0])
    return "|".join(type_list)


def get_info(mission_list, thread_code):
    for i in range(len(mission_list)):
        f = open(data_path + output_file_pre + '-' + str(thread_code) + '.csv', 'a')
        # page_i 遵守 option base 0 规则
        page_i = 0
        while True:
            # 构造URL
            url1 = 'https://restapi.amap.com/v3/place/polygon?key='
            url2 = '&polygon='
            url3 = '&keywords=&types='
            url5 = '&offset=25&extensions=base&output=json'
            url6 = '&page=' + str(page_i)
            url = url1 + api_key + url2 + mission_list[i]['lnglat'] + url3 + typecode + url5 + url6
            # print url
            poi_data = get_json(url)
            if poi_data:
                for each in poi_data:
                    f.writelines((','.join(each) + ',' + str(mission_list[i]['id']) + '\n').encode('gbk'))
                print u'线程%d(%d/%d):\t格网ID:%d, 深度:%d.' % (thread_code, i + 1, len(mission_list), mission_list[i]['id'], page_i + 1)
            else:
                print u'线程%d(%d/%d):\t格网ID:%d, EOF.' % (thread_code, i + 1, len(mission_list), mission_list[i]['id'])
            # 由于offset=25, 因此设定采集信息数量为25时执行翻页
            if len(poi_data) == 25:
                page_i += 1
            else:
                break
            # 避免高并发造成服务器压力
            time.sleep(0.4)
        f.close()


def get_json(url):
    # print 'start cid: ' + str(content_id)
    # print 'start page_i: ' + str(page_i)
    # print url[86:150]
    # print url
    # print url[-6: ]
    # exit()
    try:
        response = urllib2.urlopen(url, timeout=10)
        data = json.load(response)
        poi_data = []
        # 服务器状态正常, 返回信息可信
        if data['infocode'] == '10000':
            for each in data['pois']:
                poi_data.append([
                    emptylist_data(each['id']),
                    emptylist_data(each['name']),
                    emptylist_data(each['type']),
                    emptylist_data(each['typecode']),
                    # emptylist_data(each['address']),
                    emptylist_data(each['location'].split(',')[0]),
                    emptylist_data(each['location'].split(',')[1]),
                    emptylist_data(each['tel']),
                    emptylist_data(each['pname']),
                    emptylist_data(each['cityname']),
                    emptylist_data(each['adname'])
                ])
            # print 'No.' + str(content_id + 2) + ': ' + grid_i + '-' + str(page_i + 1) + '    data fetched.'
            return poi_data
        elif data['infocode'] == '20003':
            # print u'远程服务器内部错误'
            return []
        elif data['infocode'] == '10003':
            print u'当前工作已超限额.'
            exit()
        elif data['infocode'] == '10004':
            print u'高并发警告.'
            time.sleep(60)
            get_json(url)
        else:
            print u'未知的工作码: ' + data['infocode']
            exit()
    except Exception as e:
        # 记录错误URL地址以手动复核
        err_output(url)
        return []


def emptylist_data(args):
    if args:
        return args
    else:
        return ''


def thread_init(target_function, mission_list, thread_num):  # 根据传入的函数与目标创建多线程模型
    thread_pool = []  # 准备线程池
    function_list = thread_distribute(mission_list, thread_num)  # 计算各个线程的任务列表
    global lock  # 准备线程锁变量
    lock = threading.Lock()  # 创建线程锁,用以确认各个线程的文件操作权限
    thread_code = 0  # 线程码
    for i in range(0, thread_num):  # 对各个需要创建的线程进行遍历
        thread_code += 1  # 线程码变更
        t = threading.Thread(target=target_function, args=[function_list[i], thread_code])  # 创建线程
        thread_pool.append(t)  # 将创建的线程填入线程池
    for t in thread_pool:  # 对多线程进行遍历
        time.sleep(0.1)
        print 'thread start!'
        t.start()  # 开始各个线程
    print '--' * 6
    for t in thread_pool:  # 对多线程进行遍历
        t.join()  # 确认各个线程均已运行完成
    return 0  # 多线程模型运行完成


def thread_distribute(mission_list, thread_num):  # 按照任务列表与线程数量分配任务
    function_list = [[] for i in range(0, thread_num)]  # 创建包含各个线程任务列表的线程列表
    for i in range(0, len(mission_list)):  # 对任务列表进行遍历,将任务轮流分配至各个线程
        index = i % thread_num  # 计算当前线程
        function_list[index].append(mission_list[i])  # 将此任务添加至当前线程的任务列表中
    return function_list  # 返回分配结果


def err_output(url):
    if lock.acquire():
        f_err = open(error_file, 'a')
        f_err.writelines(url + '\n')
        f_err.close()
        lock.release()
    return 0


def res_sum():
    # 各线程结果汇总
    print '--' * 6
    print u'开始合并线程.'
    f_summ = open(data_path + output_file_pre + '-SUM.csv', 'w')
    f_summ.writelines('pid,name,type,typecode,lng,lat,tel,pname,cname,aname,missionid\n')
    for i in range(thread_num):
        f = open(data_path + output_file_pre + '-' + str(i + 1) + '.csv', 'r')
        contents = f.readlines()
        f.close()
        for each in contents:
            f_summ.writelines(each)
        print u'>> 第%02d个文件汇总完成.' % (i + 1)
    print u'线程文件汇总完成.'
    print '--' * 6
    f_summ.close()
    

def get_apikey():
    f_key = open('poi_apikey.config', 'r')
    api_key = f_key.read()
    f_key.close()
    return api_key


if __name__ == '__main__':
    global input_file_name, output_file_pre, data_path, thread_num, api_key
    # input_file_name、output_file_pre需要手动输入
    input_file_name = 'ZZ_GRID.csv'
    output_file_pre = 'ZZ'
    data_path = 'data/'
    thread_num = 8

    error_file = output_file_pre + '_error.log'
    api_key = get_apikey()
    main()
