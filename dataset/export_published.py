# coding=utf-8

from time import sleep
import json
import requests
import urllib
from pyquery import PyQuery as pq
import sqlite3
import sys
from datetime import datetime
import time
import re
import random
import math
import csv

base_url='https://www.ptt.cc'

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
			self.User_IP,
			self.Lat,
			self.Lon,
			self.Uid,
			_,
			_,
			_,
			_,
			_,
			_
		) = data

	def get_category_list(self):
		return [self.C1, self.C2, self.C3, self.C4, self.C5, self.C6, self.C7, self.C8]

	def get_max_catgeory(self):
		names = ['Complain and Crap','Daily Philosophy','Anxiety and Tiredness','Optimism and Hope','Joy and Blessing','Miss and Regret','Fortitutde and Good night','Idling and Life', 'Others']
		mat = self.get_category_list()
		if mat[0]== mat[1] and mat[2] == mat[3] and mat[1] == mat[2]:
			return names[-1]
		else:
			return names[mat.index(max(mat))]

	def get_perm(self):
		r = random.randint(0, 9)
		return 'public' if r < 5 else 'friends' if r < 8 else 'private'

	def rand_generator(self, target):
		f = str(target).split('.')[1]
		if f:
			while len(f) <= 6:
				f += str(random.randint(0, 9))
			f = float(f) * 0.000001
			return math.floor(target)+f
		else:
			return target

	def get_lat(self):
		return self.rand_generator(self.Lat)

	def get_lon(self):
		return self.rand_generator(self.Lon)

	def get_timestamp(self):
		return time.mktime(time.strptime(self.Published_Timestamp, "%Y-%m-%d %H:%M:%S"))


def getArticlesByDateRange():
	Articles = []
	for row in c.execute(u"SELECT * FROM Article_Directory JOIN User ON Article_Directory.Author= User.name WHERE Content IS NOT NULL And Board='%s' And Category = '%s' And Is_Reply = 0 And Article_Directory.Lat IS NOT NULL AND Article_Directory.Lon IS NOT NULL" % (board, cate)):
		Articles.append(Article(row))
	return Articles

def exportAritcle(article, writter):
	if article.Title == '' : return
	Aid = 'ptt' + str(article.Aid)
	User = str(article.Uid)
	writter.writerow([User, Aid])

conn = sqlite3.connect('data/ptt_category.db')
c = conn.cursor()
board, cate = ('diary', '')
Articles = getArticlesByDateRange()
i=0

with open('data/Published.csv', 'w') as f:
	writter = csv.writer(f)
	writter.writerow(['user_id', 'diary_id'])
	for article in Articles:
		i+=1;
		print('Dealing %d out of %d' % (i, len(Articles)))
		exportAritcle(article, writter)
		
c.close()
	


