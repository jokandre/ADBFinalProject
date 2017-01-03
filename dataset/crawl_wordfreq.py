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
import jieba.analyse

jieba.set_dictionary('dict.txt.big')
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
			self.Std_Push
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

	def insertWordFreq(self, keywords):
		for pair in keywords:
			word = pair[0]
			weight = pair[1]

			result = (None, word, weight, self.Aid)

			c.execute("INSERT INTO Article_WordFreq VALUES (?, ?, ?, ?)", result)
			conn.commit()

def getArticles():
	Articles = []
	for row in c.execute(u"Select * From Article_Directory Where Content IS NOT NULL"):
		Articles.append(Article(row))
	return Articles

def getKeywords(article):
	try:
		keywords = jieba.analyse.textrank(article.Content, topK=100, withWeight=True, allowPOS=('ns', 'n', 'vn', 'v'))
		print('Aid %d Title: %s' % (article.Aid, article.Title))
		print(','.join(map(lambda x: '(%s, %f) ' % (x[0], x[1]), keywords)))
		article.insertWordFreq(keywords)
		return keywords
	except:
		print('Failed: Aid %d Title: %s' % (article.Aid, article.Title))

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

def crawlArticle(article):
	print('Trying to fetch Aid %d, Title %s, Url %s\n' % (article.Aid, article.Title, article.Url))
	url = base_url+article.Url

	headers = {	
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.5',
		'Connection': 'keep-alive',
		'Cookie': '__utma=156441338.1484622574.1423226889.1463159306.1463161395.184; __utmz=156441338.1463062835.182.158.utmcsr=facebook.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmc=156441338; __utmb=156441338.19.10.1463161395; __utmt=1',
		'Host': 'www.ptt.cc',
		'Referer': url,
		'Cache-Control': 'max-age=0',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:45.0) Gecko/20100101 Firefox/45.0'
	}

	try:
		res = requests.get(url=url,
			headers=headers,
			verify=None)
		sleep(2)
	except:
		print('Aid %d request failed\n' % article.Aid)
		return

	try:
		dom = pq(res.content)
		meta = dom('.article-meta-value')
		update_date = datetime.now()
		user_id = meta.eq(0).text().split(' (')[0]
		user_nickname = meta.eq(0).text().split(' (')[1].replace(')', '')
		published_timestamp = datetime.strptime(meta.eq(3).text(), '%c')
		content = "".join(dom('#main-content').text().split(u'※ 發信站: 批踢踢實業坊(ptt.cc)')[0].split("\n")[1:])
		img_list = map(lambda x: urllib.quote_plus(pq(x).attr.src), dom('#main-content').find('img'))
		response_list = map(lambda x: {
			'push_tag': pq(x).find('.push-tag').text().encode('utf-8'),
			'user_id': pq(x).find('.push-userid').text().encode('utf-8'),
			'content': pq(x).find('.push-content').text().encode('utf-8'),
			'timestamp': '2016-'+pq(x).find('.push-ipdatetime').text().replace('/', '-')+':00'
			#'timestamp': datetime.strptime('2016/'+pq(x).find('.push-ipdatetime').text(), '%Y/%m/%d %H:%M')
			},dom('div.push'))
		update_result = (update_date, content, json.dumps(response_list), published_timestamp, user_id, user_nickname, json.dumps(img_list), int(article.Aid))

		#print('%s, %s, %s, %s, %s, %s' % (user_id, user_nickname, published_timestamp.strftime('%Y/%m/%d'), content, img_list, response_list))
		article.updateArticle(update_result)
	except:
		print('Aid %d parse failed\n' % article.Aid)
		return

conn = sqlite3.connect('data/ptt.db')
c = conn.cursor()
Articles = getArticles()
#Articles = getArticlesByDateRange(('2016-01-01', '2016-01-02'))
#getKeywords(Articles[1])

i=0
for article in Articles:
	i+=1;
	print('Dealing %d out of %d' % (i, len(Articles)))
	getKeywords(article)


c.close()
	


