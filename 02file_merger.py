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
        st = obspy.read(i_dir+"/*")
        # print(st)
        if len(st) > 1:
            call_merge(st, i_dir)
