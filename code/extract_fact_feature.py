"""
params:
    1. user_to_facts
    2. lda gensim model
    3. mallet lda
    4. doc2vec
    5. features file
    6. outputfile
"""

import sys
from tqdm import tqdm
from gensim.models import ldamodel
import matutils2 as matutils
from scipy import spatial
import gensim

user_to_words = dict()
user_to_lda_bow = dict()
user_to_fact_count = dict()

print 'loading gensim lda model'
model = ldamodel.LdaModel.load(sys.argv[2])
print 'loading doc2vec model'
doc2vecmodel = gensim.models.doc2vec.Doc2Vec.load(sys.argv[4])

print 'loading user_to_fact file'
with open(sys.argv[1], 'r') as infile:
    for line in tqdm(infile):
        splits = line.strip().split("\t")
        uid = splits[0]
        words = splits[1].split()
        user_to_words[uid] = model.id2word.doc2bow(words)
        user_to_lda_bow[uid] = model[user_to_words[uid]]

        user_to_fact_count[uid] = set(splits[1].split())

user_to_topic = dict()
print 'loading topic to vec using mallet'
with open(sys.argv[3], 'r') as infile:
    for line in tqdm(infile):
        splits = line.strip().split("\t")
        r = splits[1].rfind("/")
        uid = splits[1][r + 1:]
        user_to_topic[uid] = map(lambda x: float(x), splits[2:])

i = 5
while i < len(sys.argv):
    outfile = open(sys.argv[i + 1], 'w')
    with open(sys.argv[i], 'r') as infile:
        for line in tqdm(infile):
            splits = line.strip().split()
            u1, u2 = splits[0].split(",")

            share_facts = len(user_to_fact_count[u1] & user_to_fact_count[u2])
            union_facts = len(user_to_fact_count[u1] | user_to_fact_count[u2])
            vect1 = user_to_topic[u1]
            vect2 = user_to_topic[u2]
            topic_sim = 1 - spatial.distance.cosine(vect1, vect2)

            bow1 = user_to_words[u1]
            bow2 = user_to_words[u2]

            lda_bow1 = user_to_lda_bow[u1]
            lda_bow2 = user_to_lda_bow[u2]

            hellinger_score = matutils.hellinger(lda_bow1, lda_bow2)  # hellinger(lda_bow2, lda_bow1)

            cosine_score = matutils.cossim(lda_bow1, lda_bow2)
            jaccard_word_score = matutils.jaccard(bow1, bow2)
            jaccard_lda_score = matutils.jaccard(lda_bow1, lda_bow2)

            vec1 = doc2vecmodel.docvecs[u1]
            vec2 = doc2vecmodel.docvecs[u2]

            doc2vec_sim = 1 - spatial.distance.cosine(vec1, vec2)

            outfile.write("{} {} {} {} {} {} {} {} {}\n".format(line.strip(),
                                                                share_facts, float(share_facts) / union_facts,
                                                                topic_sim,
                                                                hellinger_score, cosine_score,
                                                                jaccard_word_score, jaccard_lda_score,
                                                                doc2vec_sim))

    outfile.close()
    i += 2
