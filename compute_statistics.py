#-*—coding:utf8-*-
import numpy as np
import gc
import re
import csv
import codecs
import matplotlib
import matplotlib.pyplot as plt
from decimal import *

# maclist = ("04:a1:51:96:ca:83",
#            "04:a1:51:a3:57:1a",
#            "44:94:fc:82:d9:8e",
#            "04:a1:51:a8:6e:c5",
#            "04:a1:51:96:64:cb",
#            "04:a1:51:a0:65:c0",
#            "04:a1:51:a7:54:f9",
#            "04:a1:51:8e:f1:cb")

try:
    fil2 = codecs.open("statistics.txt", "w", 'utf_8_sig')
    # fil6 = codecs.open("channel_ssid_time.csv", "w", 'utf_8_sig')
    write_record = csv.writer(fil2)
    # write_ssid = csv.writer(fil6)
except Exception:
    print "tranningdata open failed"
    exit()

try:
    fil1 = open("6667.txt", "r")
    fil3 = open("retranstime.txt", "r")
except Exception:
    print "6666 or retranstime open failed."

lines = fil1.readlines()
times = fil3.readlines()

drop = []
queue = []
survey = []
iw = []
beacon = []
data_list = []


class data_linger:

    def __init__(self, is_drop, timex_drop, timex_survery, timex_queue,
                 drop_count, survey_time, time_busy, time_ext_busy,
                 time_rx, time_tx, time_scan,
                 center_freq, noise, bytes, packets, qlen,
                 backlog, drops, requeues, overlimits):
        self.is_drop = is_drop
        self.timex_drop = timex_drop
        self.drop_count = drop_count
        self.timex_survery = timex_survery
        self.survey_time = survey_time
        self.time_busy = time_busy
        self.time_ext_busy = time_ext_busy
        self.time_rx = time_rx
        self.time_tx = time_tx
        self.time_scan = time_scan
        self.center_freq = center_freq
        self.noise = noise
        self.timex_queue = timex_queue
        self.bytes = bytes
        self.packets = packets
        self.qlen = qlen
        self.backlog = backlog
        self.drops = drops
        self.requeues = requeues
        self.overlimits = overlimits


for item in lines:
    length = len(item) - 1
    tmp = int(item[0])
    item = item[3:length]
    item = re.split(", ", item)
    item[0] = int(item[0])
    length = len(item)
    if tmp == 2:
        for i in range(4, length):
            item[i] = int(item[i])
        drop.append(item)
    elif tmp == 3:
        for i in range(3, length - 1):
            item[i] = int(item[i])
        item[length - 1] = float(item[length - 1])
        iw.append(item)
    elif tmp == 4:
        for i in range(2, length):
            item[i] = int(item[i])
        queue.append(item)
    elif tmp == 5:
        for i in range(2, 6):
            item[i] = int(item[i])
        beacon.append(item)
    elif tmp == 6:
        for i in range(2, length):
            item[i] = int(item[i])
        survey.append(item)
    else:
        print "fuck"
drop = sorted(drop)
queue = sorted(queue)
iw = sorted(iw)
survey = sorted(survey)
beacon = sorted(beacon)
last_low_index = -1
last_low_index1 = -1


def BinSearch(array, key, low, high):
    global last_low_index
    mid = int((low + high) / 2)
    if key == array[mid][0]:  # 若找到
        return array[mid]
    if low > high:
        # return False
        return array[last_low_index]
    if key < array[mid][0]:
        return BinSearch(array, key, low, mid - 1)  # 递归
    if key > array[mid][0]:
        last_low_index = mid
        return BinSearch(array, key, mid + 1, high)


def BinSearch_ind(array, key, low, high):
    global last_low_index1
    mid = int((low + high) / 2)
    if key == array[mid][0]:  # 若找到
        return mid
    if low > high:
        # return False
        return last_low_index1
    if key < array[mid][0]:
        return BinSearch_ind(array, key, low, mid - 1)  # 递归
    if key > array[mid][0]:
        last_low_index1 = mid
        return BinSearch_ind(array, key, mid + 1, high)


wait_to_del = set()
for item in times:
    tm = item
    ind = BinSearch_ind(survey, tm, 0, len(survey) - 1)
    (timex_survey, mac_addr, survey_time, time_busy, time_ext_busy,
     time_rx, time_tx, time_scan, center_freq, noise) = survey[ind]
    wait_to_del.add(ind)
    dp = BinSearch(drop, tm, 0, len(drop) - 1)
    drop_count = dp[len(dp) - 1]
    timex_drop = dp[0]
    qu = BinSearch(queue, tm, 0, len(queue) - 1)
    (timex_queue, mac_addr, queue_id, bytes1, packets,
     qlen, backlog, drops, requeues, overlimits) = qu
    # iw1 = BinSearch(iw, tm, 0, len(iw) - 1)
    # be = BinSearch(beacon, tm, 0, len(beacon) - 1)
    dt = data_linger(1, timex_drop, timex_survey, timex_queue,
                     drop_count, survey_time, time_busy, time_ext_busy,
                     time_rx, time_tx, time_scan, center_freq, noise, bytes1,
                     packets, qlen, backlog, drops, requeues, overlimits)
    # print dt.drop_count, dt.survey_time, dt.time_busy
    data_list.append(dt)
    # exit()

wait_to_del = sorted(wait_to_del, reverse=True)

for i in wait_to_del:
    del survey[i]

for item in survey:
    tm = item[0]
    (timex_survey, mac_addr, survey_time, time_busy, time_ext_busy,
     time_rx, time_tx, time_scan, center_freq, noise) = item
    dp = BinSearch(drop, tm, 0, len(drop) - 1)
    drop_count = dp[len(dp) - 1]
    timex_drop = dp[0]
    qu = BinSearch(queue, tm, 0, len(queue) - 1)
    (timex_queue, mac_addr, queue_id, bytes1, packets,
     qlen, backlog, drops, requeues, overlimits) = qu
    # iw1 = BinSearch(iw, tm, 0, len(iw) - 1)
    # be = BinSearch(beacon, tm, 0, len(beacon) - 1)
    dt = data_linger(0, timex_drop, timex_survey, timex_queue,
                     drop_count, survey_time, time_busy, time_ext_busy,
                     time_rx, time_tx, time_scan, center_freq, noise, bytes1,
                     packets, qlen, backlog, drops, requeues, overlimits)
    # print dt.drop_count, dt.survey_time, dt.time_busy
    data_list.append(dt)
    # exit()

del drop, queue, survey, iw, wait_to_del, lines, times

length = len(data_list)

for i in range(0, length):
    found = False
    for j in range(i, length):
        if data_list[j].timex_survery > data_list[i].timex_survery + 1000:
            found = True
            break
    if found is True:
        previous = data_list[i]
        currentd = data_list[j]
        

gc.collect()
if fil1:
    fil1.close()
if fil2:
    fil2.close()
