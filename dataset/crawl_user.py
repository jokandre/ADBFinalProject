# coding=utf-8
from time import sleep
import json
import requests
import urllib
import re
from pyquery import PyQuery as pq
import sqlite3
import sys
from datetime import datetime
import random

base_url='https://www.ptt.cc'

class Comment:
	def __init__(self, data):
		(
			self.id,
			self.user_id,
			self.push_tag,
			self.content,
			self.article_id,
			self.timestamp
		) = data

	def save(self):
		c.execute('INSERT INTO Comment VALUES (?,?,?,?,?,?)', (self.id, self.user_id, self.push_tag, self.content, self.article_id, self.timestamp))
		conn.commit()

class User:
	friend_list = set()

	def __init__(self, data):
		(
			self.id,
			self.gender,
			self.email,
			self.name,
			self.nickname,
			self.access_token,
			self.user_ip
		) = data

	def add_friend(self, friend):
		if self.id == friend.id:
			return
		if friend.id not in self.friend_list:
			c.execute('INSERT INTO User_Friends VALUES (?,?,?)',(None, self.id, friend.id))
			self.friend_list.add(friend.id)

	def save(self):
		c.execute('INSERT INTO User VALUES (?,?,?,?,?,?,?)', (self.id, self.gender, self.email, self.name, self.nickname, self.access_token, self.user_ip))
		conn.commit()

	def update_detail(self):
		c.execute('UPDATE User SET nickname = ?, user_ip = ? WHERE id=?', (self.nickname, self.user_ip, self.id))
		conn.commit()



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
			self.Lon,
			self.Lat
		) = data

	def updateArticle(self, updateData):
		(
			self.Updated_Date,
			self.Content,
			self.Push_Content,
			self.Published_Timestamp,
			self.User_ID,
			self.User_Nickname,
			self.Img_List,
			tmp
		) = updateData
		#print(u"UPDATE Article_Directory SET Updated_Date='%s', Content='%s', Push_Content='%s', Published_Timestamp='%s', User_ID='%s', User_Nickname='%s', Img_List='%s' WHERE Aid = %d)" % updateData)
		c.execute("UPDATE Article_Directory SET Updated_Date=?, Content=?, Push_Content=?, Published_Timestamp=?, User_ID=?, User_Nickname=?, Img_List=? WHERE Aid=?", updateData)
		conn.commit()

def getArticles():
	Articles = []
	for row in c.execute(u"Select * From Article_Directory Where Content IS NOT NULL"):
		Articles.append(Article(row))
	return Articles

def updatePushCount(article):
	if(article.Push_Content==None):return
	push_replies = json.loads(article.Push_Content)
	push_count = 0
	for push_content in push_replies:
		push_count += 1 if push_content['push_tag'] == u'推' else 0
		push_count -= 1 if push_content['push_tag'] == u'噓' else 0
	if(article.Push == str(push_count).encode('utf-8')):
		print('Aid %d stays push at %s'%(article.Aid, article.Push))
		return
	else:
		print('Aid %d from push %s to %d' %(article.Aid, article.Push, push_count))
		c.execute("UPDATE Article_Directory SET Push=? WHERE Aid=?",(push_count, article.Aid))
		conn.commit()

user_counter = 30000
name_list = {}
def get_user(name, nickname='', user_ip=''):
	global user_counter, name_list

	try:
		if name_list[name]:
			if name_list[name].nickname=='' and name_list[name].user_ip == '' and user_ip != '':
				name_list[name].nickname = nickname
				name_list[name].user_ip = user_ip
				name_list[name].update_detail()
			return name_list[name]
	except:
		data = (
			user_counter,
			'female' if random.randrange(0, 2) == 0 else 'male',
			'imported%i@ptt.cc'%user_counter,
			name,
			nickname,
			'imported_password',
			user_ip
		)
		name_list[name] = User(data)
		name_list[name].save()
		user_counter += 1
		return name_list[name]



def crawl_user(article):
	#author

	author = get_user(article.User_ID, article.User_Nickname, article.User_IP)
	last_commenter_id = ''
	cache_com = []
	counter = 1
	for comment in json.loads(article.Push_Content):
		commenter = get_user(comment['user_id'])
		author.add_friend(commenter)
		if last_commenter_id == commenter:
			cache_com[-1].content += '\n'+comment['content']
		else:
			print(article.Aid*10000+counter)
			data=(
				article.Aid*10000+counter,
				comment['user_id'],
				comment['push_tag'],
				comment['content'],
				article.Aid,
				comment['timestamp'])
			counter += 1
			cache_com.append(Comment(data))

	for comment in cache_com:
		comment.save()

conn = sqlite3.connect('data/ptt_category.db')
c = conn.cursor()
Articles = getArticles()
#Articles = getArticlesByDateRange(('2016-01-01', '2016-01-02'))
#updatePushCount(Articles[1])

i=0
for article in Articles:
	i+=1;
	print('Dealing %d out of %d' % (i, len(Articles)))
	crawl_user(article)

c.close()
	


