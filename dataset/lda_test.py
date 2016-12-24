# coding=utf-8

from sklearn.feature_extraction.text import CountVectorizer
import sqlite3
import sys
from gensim import corpora, models
import gensim
from datetime import datetime

conn = sqlite3.connect('data/ptt.db')
c = conn.cursor()

class Article:
	def __init__(self, data):
		(
			self.Aid, 
			self.Board,
			self.Title,
			self.Url,
			self.Push,
			self.Author,
			self.Published_Date,
			self.Category,
			self.Page,
			self.Is_Reply,
			self.Parent,
			self.Crawled_Date,
			self.Updated_Date,
			self.Content,
			self.Push_Content,
			self.Published_Timestamp,
			self.User_ID,
			self.User_Nickname,
			self.Img_List,
			self.Std_Push,
			self.User_IP
		) = data

def getArticlesByDateRange():
	Articles = []
	for row in c.execute(u"SELECT * FROM Article_Directory WHERE Content IS NOT NULL And Board='%s' And Category = '%s' And Is_Reply = 0 " % (board, cate)):
		Articles.append(Article(row))
	return Articles

def ida(articles):
	stopwords = []
	doc_terms = []
	with open('ch_stopwords.txt', 'r') as f:
		stopwords = f.read().lower().split('\n')

	trigram_vectorizer = CountVectorizer(ngram_range=(2, 3),token_pattern=r'([\u4e00-\u9fa5]{1}|\b[a-zA-Z]+\b)', min_df=0.5, stop_words=stopwords, analyzer='word')
	analyzer = trigram_vectorizer.build_analyzer()

	for article in articles:
		terms = list(map(lambda x: x.replace(' ', ''), analyzer(article.Content))) #get rid of spaces
		#print(terms)
		doc_terms.append(terms)
	
	dictionary = corpora.Dictionary(doc_terms)
	corpus = [dictionary.doc2bow(text) for text in doc_terms]
	ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=8, id2word = dictionary, alpha='auto', eval_every=5, iterations=100, passes=40)
	ldamodel.save('ldamodel%s.mdl'%str(datetime.now())[5:-7])
	print(ldamodel.print_topics(num_topics=8, num_words=10))


board, cate = (sys.argv[1], '')
Articles = getArticlesByDateRange()
i=0
ida(Articles[:100])
'''
for article in Articles:
	i+=1;
	print('Dealing %d out of %d' % (i, len(Articles)))
	crawlArticle(article)
'''
c.close()
