"""
1. user to domain
2. lda gensim model
3. mallet gensim model
4. doc2vec model
5. feature file
6. output file
"""

import sys
from tqdm import tqdm
from gensim.models import ldamodel
import gensim
import matutils2 as matutils
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy import spatial

print 'initialize tf idf'
tfidf_domain = TfidfVectorizer(lowercase=False, preprocessor=None).fit_transform(
    map(lambda x: x.strip().split('\t')[-1], open(sys.argv[1]).readlines()))

user_to_words = dict()

user_to_lda_bow = dict()
user_to_domains = dict()

print 'loading lda model gensim'
model = ldamodel.LdaModel.load(sys.argv[2])
print 'loading gensim doc2vec'
doc2vecmodel = gensim.models.doc2vec.Doc2Vec.load(sys.argv[4])

index = 0
user_to_domain_count = dict()
print 'loading user to domain file'
with open(sys.argv[1], 'r') as infile:
    for line in tqdm(infile):
        splits = line.strip().split("\t")
        uid = splits[0]
        words = splits[1].split()
        user_to_words[uid] = model.id2word.doc2bow(words)
        user_to_lda_bow[uid] = model[user_to_words[uid]]

        user_to_domains[uid] = index
        user_to_domain_count[uid] = set(splits[1].split())
        index += 1

user_to_topic = dict()
print 'loading topic to vec mallet'

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

            share_facts = len(user_to_domain_count[u1] & user_to_domain_count[u2])
            union_facts = len(user_to_domain_count[u1] | user_to_domain_count[u2])

            vect1 = tfidf_domain[user_to_domains[u1]].toarray()[0]
            vect2 = tfidf_domain[user_to_domains[u2]].toarray()[0]
            tfidf_sim = 1 - spatial.distance.cosine(vect1, vect2)

            vect1 = user_to_topic[u1]
            vect2 = user_to_topic[u2]
            topic_sim = 1 - spatial.distance.cosine(vect1, vect2)

            vec1 = doc2vecmodel.docvecs[u1]
            vec2 = doc2vecmodel.docvecs[u2]

            doc2vec_sim = 1 - spatial.distance.cosine(vec1, vec2)

            bow1 = user_to_words[u1]
            bow2 = user_to_words[u2]

            lda_bow1 = user_to_lda_bow[u1]
            lda_bow2 = user_to_lda_bow[u2]

            hellinger_score = matutils.hellinger(lda_bow1, lda_bow2)  # hellinger(lda_bow2, lda_bow1)

            cosine_score = matutils.cossim(lda_bow1, lda_bow2)
            jaccard_word_score = matutils.jaccard(bow1, bow2)
            jaccard_lda_score = matutils.jaccard(lda_bow1, lda_bow2)

            outfile.write("{} {} {} {} {} {} {} {} {} {}\n".format(line.strip(),
                                                                   share_facts, float(share_facts) / union_facts,
                                                                   tfidf_sim,
                                                                   topic_sim,
                                                                   hellinger_score,
                                                                   cosine_score,
                                                                   jaccard_word_score,
                                                                   jaccard_lda_score,
                                                                   doc2vec_sim))
    outfile.close()
    i += 2
