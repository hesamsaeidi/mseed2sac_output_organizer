#!/usr/bin/env python

# This file reads a summary file created by jweed and extract event and stations
# info from that and stores. Then it reads sacfiles prepared in previous steps
# and match them with the event, create Event folder copy sac files in them while
# adding event and station info to the header of the sacfiles.
# Written by Hesam Saeidi May 2021

import re
import os
import obspy
from datetime import datetime, date, timedelta

# time diff between header and summary file should not be more than:
# based on https://www.usgs.gov/natural-hazards/earthquake-hazards/science/earthquake-travel-times?qt-science_center_objects=0#qt-science_center_objects
t_delta = timedelta(minutes=12)

dir_path = os.getcwd()


class Event:
    def __init__(self, lat, lon, dep, etime, edate, mag):
        self.lat = lat
        self.lon = lon
        self.dep = dep
        self.etime = etime
        self.edate = edate
        self.mag = mag

    def path_maker(self):
        path_etime = self.etime
        path_etime = path_etime.replace(':', '.')
        path_edate = self.edate
        path_edate = path_edate.replace('/', '.')
        path = "Event_" + path_edate + "." + path_etime
        return path

    def time_conv(self):
        year = int(self.edate[0:4])
        month = int(self.edate[5:7])
        day = int(self.edate[8:10])
        jday = date(year, month, day).timetuple().tm_yday
        [hour, min, sec, msec] = list(map(int,self.etime.split(':')))

        return year, jday, hour, min, sec, msec




def make_folder(name):
    if not os.path.isdir(name):
        os.mkdir(name)

def envet_info_extractor(line):
    chunks = line.split(',')
    edate = re.search(r'.[0-9]{3}\/.\d?\/.\d?', chunks[1])
    edate = edate.group(0)
    etime = re.search(r'.[0-9]\:.[0-9]\:.[0-9]\.[0-9]{3}', chunks[1])
    etime = etime.group(0).replace('.', ':')

    lat = float(chunks[2])
    lon = float(chunks[3])
    dep = float(chunks[4]) *1000 # convert to km
    mag = float(chunks[5][-3:])
    return lat, lon, dep, etime, edate, mag


ek=0
event_list = []
station_dict = {}
with open("AF_H_04-20-21.summaryNEW", "r") as summary:

    for line in summary:
        line = line.strip()
        if line.startswith('EVENT'):
            lat, lon, dep, etime, edate, mag = envet_info_extractor(line)
            event_list.append(Event(lat, lon, dep, etime, edate, mag))
            ek+=1

        elif line.startswith("STATION"):
            stats = line.split(' ')
            station_dict[stats[1]] = [float(stats[3]), float(stats[4])]


#         elif line.startswith("PHASE"):
#             print('phase')
#         else:
#             print(line)
#
# print(event_list)
# for e in event_list:
#     print(type(e.path_maker()))
#     print(e.lat)
# from pprint import pprint
# pprint(station_dict)
# print(len(event_list))

bigList = os.listdir(dir_path)
for i_dir in bigList:
    if os.path.isdir(i_dir) and i_dir[:3] == "AF.":
        sac_path = os.path.join(dir_path,i_dir)
        sac_path+='/*'
        tr = obspy.read(sac_path, debug_headers=True)
        st_name = tr[0].stats.sac.kstnm.strip()
        st_chn = tr[0].stats.sac.kcmpnm.strip()
        st_days=int(tr[0].stats.sac['nzjday'])
        st_seconds=int(tr[0].stats.sac['nzsec'])
        st_milliseconds=int(tr[0].stats.sac['nzmsec'])
        st_minutes=int(tr[0].stats.sac['nzmin'])
        st_hours=int(tr[0].stats.sac['nzhour'])
        st_years = int(tr[0].stats.sac['nzyear'])
        stream_time = timedelta(
                                days=st_days,
                                hours=st_hours,
                                minutes=st_minutes,
                                seconds=st_seconds,
                                milliseconds=st_milliseconds
                                )


        for e in event_list:
            ev_years, ev_jdays, ev_hours, ev_min, ev_secs, ev_msecs = e.time_conv()
            event_time = timedelta(
                                    days=ev_jdays,
                                    hours=ev_hours,
                                    minutes=ev_min,
                                    seconds=ev_secs,
                                    milliseconds=ev_msecs
                                    )
            if ev_years == st_years:
                omarker = (event_time - stream_time)
                if abs(omarker) < t_delta:
                    # print(omarker.total_seconds())


                    # print('event: ', e.time_conv(), 'record: ', , '\n')
                    # print('evnet FOUND: ',e.edate, e.etime, '\ntrace: ',st_years, st_days, st_hours, st_minutes, st_seconds, st_milliseconds,"\n\n")

                    [stla, stlo] = station_dict[st_name]
                    ev_path = e.path_maker()
                    st_dir = os.path.join(dir_path,ev_path)
                    trace_name = st_dir + "/" + st_name + "." + st_chn
                    make_folder(st_dir)
                    tr[0].stats.sac.evdp = e.dep
                    tr[0].stats.sac.evla = e.lat
                    tr[0].stats.sac.evlo = e.lon
                    tr[0].stats.sac.mag = e.mag
                    tr[0].stats.sac.stla = stla
                    tr[0].stats.sac.stlo = stlo
                    tr[0].stats.sac.o = omarker.total_seconds()
                    tr.write(trace_name, format='SAC')
