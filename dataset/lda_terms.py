# coding=utf-8
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import sqlite3
import sys
#from gensim import corpora, models
#import gensim
from datetime import datetime

conn = sqlite3.connect('data/ptt_category.db')
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

	def update_scores(self, scores):
		updateData = [self.Aid,] + scores
		c.execute("INSERT INTO Article_Category VALUES (?,?,?,?,?,?,?,?,?)", updateData)
		conn.commit()

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(",".join(['%s %.4f'%(feature_names[i].replace(' ', ''),topic[i])
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
        
    print()

def getArticlesByDateRange():
	Articles = []
	for row in c.execute(u"SELECT * FROM Article_Directory WHERE Content IS NOT NULL And Board='%s' And Category = '%s' And Is_Reply = 0 " % (board, cate)):
		Articles.append(Article(row))
	return Articles


def ida(articles):
	stopwords = []
	doc_terms = []
	with open('ch_stopwords.txt', 'r') as f:
		stopwords = set(f.read().lower().split('\n'))

	#print('stopwords', stopwords[:10])
	vocab = joblib.load(open('lda-vocab.pkl', 'rb'))
	trigram_vectorizer = CountVectorizer(ngram_range=(2,3),token_pattern=r'([\u4e00-\u9fa5]{1}|)', vocabulary=vocab, stop_words=stopwords, analyzer='word')
	analyzer = trigram_vectorizer.build_analyzer()
	article_contents = map(lambda x: x.Content, articles)
	doc_terms = trigram_vectorizer.fit_transform(article_contents)

	pkl_file = open('lda-n8-2.pkl', 'rb')
	lda = joblib.load(pkl_file)

	print_top_words(lda, trigram_vectorizer.get_feature_names(), 100)
	

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
