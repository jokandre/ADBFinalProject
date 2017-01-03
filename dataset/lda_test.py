# coding=utf-8
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import sqlite3
import sys
#from gensim import corpora, models
#import gensim
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

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        '''
        for i in topic.argsort():
        	print(i)
        '''
        
        print(",".join(['%s %.4f'%(feature_names[i].replace(' ', ''),topic[i])
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
        
    print()

def ida(articles):
	stopwords = []
	doc_terms = []
	with open('ch_stopwords.txt', 'r') as f:
		stopwords = set(f.read().lower().split('\n'))

	#print('stopwords', stopwords[:10])

	trigram_vectorizer = TfidfVectorizer(ngram_range=(2,3),token_pattern=r'([\u4e00-\u9fa5]{1}|)', min_df=10, max_df=20, stop_words=stopwords, analyzer='word')
	analyzer = trigram_vectorizer.build_analyzer()

	'''
	for article in articles:
		terms = map(lambda x: x.replace(' ', ''), analyzer(article.Content)) #get rid of spaces
		#terms = set(map(lambda x: x.replace(' ', ''), analyzer(article.Content))) #get rid of spaces
		#terms = list(terms-stopwords)
		doc_terms.append(list(terms))
	'''
	article_contents = map(lambda x: x.Content, articles)
	doc_terms = trigram_vectorizer.fit_transform(article_contents)
	tf_feature_names = trigram_vectorizer.get_feature_names()
	print(len(tf_feature_names), tf_feature_names[100:200])
	
	lda = LatentDirichletAllocation(n_topics=8, max_iter=200, evaluate_every=10, n_jobs=-1, verbose=1, learning_method='online')
	lda.fit(doc_terms)
	joblib.dump(lda, 'lda-n8-2.pkl', compress = 1)
	print_top_words(lda, tf_feature_names, 10)
	

	#print(doc_terms.get_feature_names())
	'''
	dictionary = corpora.Dictionary(doc_terms)
	corpus = [dictionary.doc2bow(text) for text in doc_terms]
	ldamodel = gensim.models.ldamulticore.LdaMulticore(corpus, num_topics=8, id2word = dictionary, eval_every=5 ,iterations=10000, passes=1000)
	ldamodel.save('ldamodel%s.mdl'%str(datetime.now())[5:-7])
	print(ldamodel.print_topics(num_topics=8, num_words=10))
	'''

board, cate = ('diary', '')
Articles = getArticlesByDateRange()
i=0
ida(Articles[:1500])
'''
for article in Articles:
	i+=1;
	print('Dealing %d out of %d' % (i, len(Articles)))
	crawlArticle(article)
'''
c.close()
