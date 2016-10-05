"""
extract more fact and domain features, but considering only the same day
"""

import sys
from tqdm import tqdm
from datetime import datetime
import matutils2 as matutils

print 'load fact to domain'
fact_to_domain = dict()
with open(sys.argv[2], 'r') as infile:
    for line in tqdm(infile):
        fid, did = line.strip().split()
        fact_to_domain[fid] = did
###############################################

# load facts file
print "load facts file"
user_facts = dict()
user_domains = dict()

with open(sys.argv[1], 'r') as infile:
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
        if uid not in user_facts:
            user_facts[uid] = dict()
            user_domains[uid] = dict()
        if day not in user_facts[uid]:
            user_facts[uid][day] = dict()
            user_domains[uid][day] = dict()
        if fid not in user_facts[uid][day]:
            user_facts[uid][day][fid] = 0
        did = fact_to_domain[fid]
        if did not in user_domains[uid][day]:
            user_domains[uid][day][did] = 0
        user_facts[uid][day][fid] += 1
        user_domains[uid][day][did] += 1


#######################################

def extract_daily_facts(user_1_facts, user_2_facts):
    """

    :param user_1_facts:
    :param user_2_facts:
    :return:
    """
    f1 = 0
    f2 = 0
    f3 = 1.0
    f4 = 1.0
    num_days = 0
    for day in user_1_facts:
        if day in user_2_facts:
            num_days += 1
            facts1 = user_1_facts[day]
            facts2 = user_2_facts[day]
            jaccard1 = matutils.jaccard(facts1.items(), facts2.items())
            jaccard2 = matutils.jaccard(facts1, facts2)
            f1 += jaccard1
            f2 += jaccard2
            f3 = min(f3, jaccard1)
            f4 = min(f4, jaccard2)

    if num_days > 0:
        f1 = float(f1) / num_days
        f2 = float(f2) / num_days
    else:
        f1 = -999
        f2 = -999
        f3 = -999
        f4 = -999
    return f1, f2, f3, f4, float(num_days) / (len(user_1_facts) + len(user_2_facts) - num_days)


i = 3
while i < len(sys.argv):
    outfile = open(sys.argv[i + 1], 'w')
    with open(sys.argv[i], 'r') as infile:
        for line in tqdm(infile):
            tokens = line.strip().split()
            u1, u2 = tokens[0].split(",")

            f1, f2, f3, f4, f5 = extract_daily_facts(user_facts[u1], user_facts[u2])
            f6, f7, f8, f9, f10 = extract_daily_facts(user_domains[u1], user_domains[u2])

            outfile.write(
                "{} {} {} {} {} {} {} {} {} {} {}\n".format(line.strip(), f1, f2, f3, f4, f5, f6, f7, f8, f9, f10))
    outfile.close()
    i += 2
