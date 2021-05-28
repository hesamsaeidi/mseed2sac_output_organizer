#!/usr/bin/env python
# import re
import os
import obspy
import numpy as np
# from datetime import datetime, date, timedelta

def call_merge(st, dir):
    last_id = len(st) -1
    st.sort(['starttime'])
    sac_file_name = st[0].id + '.' + st[0].stats.starttime.strftime('%Y%m%d-%H%M%S') + '.' + st[last_id].stats.endtime.strftime('%Y%m%d-%H%M%S') + '.merged'
    st.merge(method=0, fill_value='interpolate', interpolation_samples=0)
    path = dir + '/' + sac_file_name
    # print(path)
    st.write(path, format='SAC')


def make_folder(name):
    if not os.path.isdir(name):
        os.mkdir(name)

dir_path = os.getcwd()
bigList = os.listdir(dir_path)
for i_dir in bigList:
    if os.path.isdir(i_dir) and i_dir[:3] == "AF.":
        dir_list = os.listdir(i_dir)
        if len(dir_list) > 1:
            for f in dir_list:
                if f.find('.merged') != -1:
                    new_name = os.path.join(i_dir,f.replace('merged', 'SAC'))
                    old_name = os.path.join(i_dir, f)
                    os.rename(old_name,new_name)
                else:
                    os.remove(os.path.join(i_dir,f))
        elif len(dir_list) == 1:
            new_name = os.path.join(i_dir,dir_list[0]+'.SAC')
            old_name = os.path.join(i_dir,dir_list[0])
            os.rename(old_name,new_name)
