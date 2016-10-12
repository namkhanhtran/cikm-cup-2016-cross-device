#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Computing similarity/distance using time info
    - days
    - hours (Euclidean distance)

1. user to days
2. user to hour
3. facts
4. feature file
5. output file
"""

import sys
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import spatial
import matutils2 as matutils
import math
from datetime import datetime

print 'vectorize tfidf times'
tfidf_days = TfidfVectorizer(lowercase=False, preprocessor=None).fit_transform(
    map(lambda x: x.strip().split('\t')[-1], open(sys.argv[1]).readlines()))

user_to_time_index = dict()
index = 0

user_to_time = dict()
print 'load user_to_days'
with open(sys.argv[1], 'r') as infile:
    for line in tqdm(infile):
        line = line.strip()
        if len(line) == 0:
            continue
        splits = line.split()
        uid = splits[0]
        days = splits[1:]

        user_to_time_index[uid] = index
        index += 1

        user_to_time[uid] = dict()
        for day in days:
            if day not in user_to_time[uid]:
                user_to_time[uid][day] = 0
            user_to_time[uid][day] += 1

user_to_time_id = dict()
for uid in user_to_time:
    user_to_time[uid] = user_to_time[uid].items()
    user_to_time_id[uid] = [u for u, v in user_to_time[uid]]

# ===============user to hour================
user_to_hour = dict()
print 'load user_to_hour'
with open(sys.argv[2], 'r') as infile:
    for line in tqdm(infile):
        line = line.strip()
        if len(line) == 0:
            continue
        splits = line.split()
        uid = splits[0]
        hours = splits[1:]

        user_to_hour[uid] = dict()
        for strhour in hours:
            hour = int(strhour)
            if hour not in user_to_hour[uid]:
                user_to_hour[uid][hour] = 0
            user_to_hour[uid][hour] += 1


def compute_euclidean_distance(hour1, hour2):
    dist = 0.0
    for k in range(0, 24):
        n1 = 0
        n2 = 0
        if k in hour1:
            n1 = hour1[k]
        if k in hour2:
            n2 = hour2[k]
        dist += (n1 - n2) * (n1 - n2)
    return math.sqrt(dist)


def compute_euclidean_datetime_distance(datetime1, datetime2):
    dist = 0.0
    count = 0
    for day in datetime1:
        if day in datetime2:
            count += 1
            dist += compute_euclidean_distance(datetime1[day], datetime2[day])
    if count > 0:
        dist = dist / count
    else:
        dist = -999
    return dist


def compute_cosine_distance(hour1, hour2):
    a = []
    b = []
    for h in range(0, 24):
        if h in hour1:
            a.append(hour1[h])
        else:
            a.append(0)
        if h in hour2:
            b.append(hour2[h])
        else:
            b.append(0)

    return 1 - spatial.distance.cosine(a, b)


def compute_cosine_datetime_distance(datetime1, datetime2):
    dist = 0.0
    count = 0
    for day in datetime1:
        if day in datetime2:
            count += 1
            dist += compute_cosine_distance(datetime1[day], datetime2[day])
    if count > 0:
        dist = dist / count
    else:
        dist = -999
    return dist


# ===========user to time===============
print 'load facts'
user_to_datetime = dict()
with open(sys.argv[3], 'r') as infile:
    header = True
    for line in tqdm(infile):
        if header is True:
            header = False
            continue
        uid, fid, ts, _ = line.strip().split("\t")
        # try:
        #     ts_date = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')
        # except:
        #     ts_date = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')

        day = ts.split()[0]
        day = day.replace("-", "")
        # hour = str(ts_date.hour)
        hour = int(ts.split()[1].split(":")[0])
        if uid not in user_to_datetime:
            user_to_datetime[uid] = dict()
        if day not in user_to_datetime[uid]:
            user_to_datetime[uid][day] = dict()
        if hour not in user_to_datetime[uid][day]:
            user_to_datetime[uid][day][hour] = 0
        user_to_datetime[uid][day][hour] += 1


# ==========compute features============
def compute_dist(ts_list_1, ts_list_2):
    dist_list = 0
    share_time = 0

    total = 0
    for hour in range(0, 24):
        if hour not in ts_list_1 or hour not in ts_list_2:
            if hour in ts_list_1:
                total += ts_list_1[hour]
            if hour in ts_list_2:
                total += ts_list_2[hour]
        else:
            h1 = float(ts_list_1[hour])
            h2 = float(ts_list_2[hour])
            share_time += min(h1, h2)
            total += max(h1, h2)
            # if h1 < 10 and h2 < 10:
            #     continue
            if dist_list < (min(h1, h2) / max(h1, h2)):
                dist_list = min(h1, h2) / max(h1, h2)

    if total > 0:
        share_time = share_time / total
    else:
        share_time = -999
    if dist_list == 0:
        dist_list = -999

    return dist_list, share_time


i = 4

while i < len(sys.argv):
    outfile = open(sys.argv[i + 1], 'w')
    with open(sys.argv[i], 'r') as infile:
        for line in tqdm(infile):
            splits = line.strip().split()
            u1, u2 = splits[0].split(",")

            vect1 = tfidf_days[user_to_time_index[u1]].toarray()[0]
            vect2 = tfidf_days[user_to_time_index[u2]].toarray()[0]
            f1 = 1 - spatial.distance.cosine(vect1, vect2)

            f2 = matutils.jaccard(user_to_time[u1], user_to_time[u2])
            f3 = matutils.jaccard(user_to_time_id[u1], user_to_time_id[u2])

            f4 = compute_euclidean_distance(user_to_hour[u1], user_to_hour[u2])

            f5 = compute_euclidean_datetime_distance(user_to_datetime[u1], user_to_datetime[u2])

            f6 = compute_cosine_distance(user_to_hour[u1], user_to_hour[u2])

            f7 = compute_cosine_datetime_distance(user_to_datetime[u1], user_to_datetime[u2])

            dist_list, share_time = compute_dist(user_to_hour[u1], user_to_hour[u2])

            outfile.write("{} {} {} {} {} {} {} {} {} {}\n".format(line.strip(), dist_list, share_time,
                                                                   f1, f2, f3, f4, f5, f6, f7))

    outfile.close()
    i += 2
