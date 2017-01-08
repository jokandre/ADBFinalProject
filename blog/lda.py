# coding=utf-8
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import math
import sys
reload(sys)
sys.setdefaultencoding('utf_8')

def lda(diary):
	stopwords = []
	doc_terms = []
	with open('blog/api/data/stopwords.txt', 'r') as f:
		stopwords = set(f.read().lower().split('\n'))

	vocab = joblib.load('blog/api/data/lda-vocab.pkl')
	lda = joblib.load('blog/api/data/lda-n8-2.pkl')

	trigram_vectorizer = CountVectorizer(ngram_range=(2,3),token_pattern=ur'([\u4e00-\u9fa5]{1}|)', vocabulary=vocab, stop_words=stopwords, analyzer='word')
	diary = [diary]
	doc_terms = trigram_vectorizer.fit_transform(diary)
	score = lda.transform(doc_terms)
	return list(map(lambda x: '%.16f'%(x*math.sqrt(1/8)),score[0]))
