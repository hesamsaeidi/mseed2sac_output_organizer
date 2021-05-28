#!/usr/bin/env python
# import re
import os
import obspy
import numpy as np
# from datetime import datetime, date, timedelta

def call_merge(merge_list):
    print(merge_list)

def make_folder(name):
    if not os.path.isdir(name):
        os.mkdir(name)


dir_path = os.getcwd()
bigList = os.listdir(dir_path)
station_date_dict = {}
for sacfile in bigList:
    if sacfile[-4:] == '.SAC':
        filename_list = sacfile.split('.')
        # filename_list = ['AF', 'SEK', '', 'BHE', 'M', '2011', '156', '115830', 'SAC']
        # print(filename_list[0:7])
        stataion_key = ','.join([filename_list[1],filename_list[3],filename_list[5],filename_list[6]])
        station_date_dict[stataion_key] = []

for sacfile  in bigList:
    if sacfile[-4:] == '.SAC':
        filename_list = sacfile.split('.')
        key = ','.join([filename_list[1],filename_list[3],filename_list[5],filename_list[6]])
        station_date_dict[key].append(sacfile)

# from pprint import pprint
# pprint(station_date_dict)
# print(len(station_date_dict))
for key in station_date_dict:

    # print(key)
    k_list = key.split(',')
    tmp_path = f'AF.{k_list[0]}..{k_list[1]}.M.{k_list[2]}.{k_list[3]}*'
    dir_tmp_path= tmp_path.replace('*',"").replace('..', '.')
    dir_num = 0
    st = obspy.read(tmp_path)
    st.sort()
    endtime_arr = np.zeros(len(st))
    starttime_arr = np.zeros(len(st))
    for num, trace in enumerate(st):
        starttime_arr[num] = trace.stats.starttime
        endtime_arr[num] = trace.stats.endtime
        if num==0:
            dir_path = dir_tmp_path + '_' + str(dir_num)
            sac_file_name = trace.id + '.' + trace.stats.starttime.strftime('%Y%m%d-%H%M%S') + '.' + trace.stats.endtime.strftime('%Y%m%d-%H%M%S')
            full_path = dir_path + '/' + sac_file_name
            print("num is zero: ",full_path)
            make_folder(dir_path)
            trace.write(full_path, format='SAC')
        else:
            diff = starttime_arr[num] - endtime_arr[num-1]
            if diff < 2: ## same trace ##
                sac_file_name = trace.id + '.' + trace.stats.starttime.strftime('%Y%m%d-%H%M%S') + '.' + trace.stats.endtime.strftime('%Y%m%d-%H%M%S')
                full_path = dir_path + '/' + sac_file_name
                print("num is not zero diff is less than 2:\n",full_path)
                make_folder(dir_path)
                trace.write(full_path, format='SAC')
                print(">>>>>>Threshold>>>>>>",starttime_arr[num] - endtime_arr[num-1])
            else: ##different trace ##
                dir_num += 1
                dir_path = dir_tmp_path + '_' + str(dir_num)
                sac_file_name = trace.id + '.' + trace.stats.starttime.strftime('%Y%m%d-%H%M%S') + '.' + trace.stats.endtime.strftime('%Y%m%d-%H%M%S')
                full_path = dir_path + '/' + sac_file_name
                print("num is not zero diff is big :\n", full_path)
                make_folder(dir_path)
                trace.write(full_path, format='SAC')

                print("(***************************************************************)<><><><>", diff)
