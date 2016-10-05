#!/usr/bin/env python
# -*- coding: utf-8
"""
Extract more features which combines fact - hour, domain - hour, max/min euclide distance
"""

import sys
import math
from tqdm import tqdm

print 'load fact to domain'
fact_to_domain = dict()
with open(sys.argv[2], 'r') as infile:
    for line in tqdm(infile):
        fid, did = line.strip().split()
        fact_to_domain[fid] = did

print 'load facts'
user_fact_hour = dict()
user_domain_hour = dict()
user_hour = dict()
with open(sys.argv[1], 'r') as infile:
    header = True
    for line in tqdm(infile):
        if header is True:
            header = False
            continue
        uid, fid, ts, _ = line.strip().split("\t")
        day = ts.split()[0]
        hour = int(ts.split()[1].split(":")[0])
        if uid not in user_fact_hour:
            user_fact_hour[uid] = dict()
            user_domain_hour[uid] = dict()
            user_hour[uid] = dict()
        if fid not in user_fact_hour[uid]:
            user_fact_hour[uid][fid] = dict()
        did = fact_to_domain[fid]
        if did not in user_domain_hour[uid]:
            user_domain_hour[uid][did] = dict()
        if day not in user_hour[uid]:
            user_hour[uid][day] = dict()

        if hour not in user_fact_hour[uid][fid]:
            user_fact_hour[uid][fid][hour] = 0
        if hour not in user_domain_hour[uid][did]:
            user_domain_hour[uid][did][hour] = 0
        if hour not in user_hour[uid][day]:
            user_hour[uid][day][hour] = 0
        user_fact_hour[uid][fid][hour] += 1
        user_domain_hour[uid][did][hour] += 1
        user_hour[uid][day][hour] += 1


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


def compute_fact_hour(u1, u2):
    max_f = 0.0
    min_f = 1000.0
    avg_f = 0.0
    count = 0

    for fact in user_fact_hour[u1]:
        if fact in user_fact_hour[u2]:
            dist = compute_euclidean_distance(user_fact_hour[u1][fact], user_fact_hour[u2][fact])
            max_f = max(max_f, dist)
            min_f = min(min_f, dist)
            avg_f += dist
            count += 1
    if count > 0:
        avg_f /= count
    else:
        max_f = -999
        min_f = -999
        avg_f = -999

    return max_f, min_f, avg_f


def compute_domain_hour(u1, u2):
    max_f = 0.0
    min_f = 1000.0
    avg_f = 0.0
    count = 0

    for fact in user_domain_hour[u1]:
        if fact in user_domain_hour[u2]:
            dist = compute_euclidean_distance(user_domain_hour[u1][fact], user_domain_hour[u2][fact])
            max_f = max(max_f, dist)
            min_f = min(min_f, dist)
            avg_f += dist
            count += 1
    if count > 0:
        avg_f /= count
    else:
        max_f = -999
        min_f = -999
        avg_f = -999

    return max_f, min_f, avg_f


def compute_hour(u1, u2):
    max_f = 0.0
    min_f = 1000.0
    count = 0
    for day in user_hour[u1]:
        if day in user_hour[u2]:
            dist = compute_euclidean_distance(user_hour[u1][day], user_hour[u2][day])
            max_f = max(max_f, dist)
            min_f = min(min_f, dist)
            count += 1
    if count == 0:
        min_f = -999
        max_f = -999

    return max_f, min_f

index = 3
while index < len(sys.argv):
    outfile = open(sys.argv[index + 1], 'w')
    with open(sys.argv[index], 'r') as infile:
        for line in tqdm(infile):
            tokens = line.strip().split()
            u1, u2 = tokens[0].split(",")

            f1, f2, f3 = compute_fact_hour(u1, u2)
            f4, f5, f6 = compute_domain_hour(u1, u2)
            f7, f8 = compute_hour(u1, u2)
            outfile.write("{} {} {} {} {} {} {} {} {}\n".format(line.strip(), f1, f2, f3, f4, f5, f6, f7, f8))

    outfile.close()
    index += 2
