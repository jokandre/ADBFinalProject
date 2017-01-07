# coding=utf-8
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


def ida(diary):
	stopwords = []
	doc_terms = []
	with open('stopwords.txt', 'r') as f:
		stopwords = set(f.read().lower().split('\n'))

	vocab = joblib.load(open('lda-vocab.pkl', 'rb'))
	lda = joblib.load(open('lda-n8-2.pkl', 'rb'))

	trigram_vectorizer = CountVectorizer(ngram_range=(2,3),token_pattern=r'([\u4e00-\u9fa5]{1}|)', vocabulary=vocab, stop_words=stopwords, analyzer='word')
	diary = [diary]
	doc_terms = trigram_vectorizer.fit_transform(diary)
	score = lda.transform(doc_terms)
	return list(score[0])