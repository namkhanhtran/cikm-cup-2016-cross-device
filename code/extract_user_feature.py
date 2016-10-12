"""
Merge codes for generating user features
"""
import sys
from tqdm import tqdm
from datetime import datetime

fact_to_domain = dict()
print 'load fact to domain'
with open(sys.argv[2], 'r') as infile:
    for line in tqdm(infile):
        fact, domain = line.strip().split()
        fact_to_domain[fact] = domain

user_to_facts = dict()
user_to_days = dict()
user_to_domains = dict()
user_to_hours = dict()

user_to_ts = dict()

print 'load facts'
with open(sys.argv[1], 'r') as infile:
    header = True
    for line in tqdm(infile):
        if header is True:
            header = False
            continue
        uid, fid, ts, _ = line.strip().split("\t")
        try:
            ts_date = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')
        except:
            ts_date = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')

        day = ts.split()[0]
        day = day.replace("-", "")
        hour = str(ts_date.hour)
        if uid not in user_to_facts:
            user_to_facts[uid] = []
            user_to_days[uid] = []
            user_to_domains[uid] = []
            user_to_hours[uid] = []
            user_to_ts[uid] = []

        user_to_facts[uid].append(fid)
        user_to_domains[uid].append(fact_to_domain[fid])
        user_to_days[uid].append(day)
        user_to_hours[uid].append(hour)
        user_to_ts[uid].append(ts_date)


def compute_distance(timefacts):
    """

    :param timefacts:
    :return:
    """
    timefacts.sort()
    distance = []

    def f(d1, d2):
        d = abs(d2 - d1)
        return d.days * 24 + float(d.seconds) / 3600.0

    for i in range(0, len(timefacts) - 1):
        d1 = timefacts[i]
        d2 = timefacts[i + 1]
        distance.append(f(d1, d2))

    return distance


with open(sys.argv[3], 'w') as outfile:
    for uid in tqdm(user_to_facts):
        n_facts = float(len(user_to_facts[uid]))
        n_distinct_facts = float(len(set(user_to_facts[uid])))
        n_distinct_domains = float(len(set(user_to_domains[uid])))

        n_days = float(len(set(user_to_days[uid])))
        n_hours = float(len(set(user_to_hours[uid])))

        distance = compute_distance(user_to_ts[uid])
        maxdist = -999
        meandist = -999
        if len(distance) > 0:
            maxdist = max(distance)
            meandist = sum(distance) / len(distance)

        outfile.write("{}\t{} {} {} {} {} {} {} {} {} {} {}\n".format(uid,
                                                                      n_facts, n_distinct_facts, n_distinct_domains,
                                                                      maxdist, meandist,
                                                                      n_facts / n_days,
                                                                      n_distinct_facts / n_days,
                                                                      n_distinct_domains / n_days,
                                                                      n_facts / n_hours,
                                                                      n_distinct_facts / n_hours,
                                                                      n_distinct_domains / n_hours
                                                                      ))
