from time import sleep
import json
import requests
import urllib
import re
from pyquery import PyQuery as pq
import sqlite3
import sys
from datetime import datetime

def crawlPage(page):
	print('Trying to fetch %d\n' % int(page))
	url = 'https://www.ptt.cc/bbs/%s/index%d.html' % (board, int(page))

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
		print('Page %d request failed\n' % int(page))
		return

	dom = pq(res.content)
	articles = dom('div.r-list-container div.r-ent').items()

	for article in articles:
		aid = None
		push = article.find('div.nrec').text() or '0'
		title = article.find('div.title').text()
		if(title.find(u'(本文已被刪除)')>=0):continue
		#print(title.find(u'(本文已被刪除)'))
		url = article.find('div.title a').attr('href')
		author = article.find('div.author').text()
		published_date = datetime.strptime('2016/'+article.find('div.date').text(), '%Y/%m/%d')
		category = title.split(']')[0].replace(u'[', '').replace(u'Re: ','').replace(u' ', '') if title.find(u']')>=0 else ''
		is_reply = title.find(u'Re:')>=0
		parent = None
		crawled_date = datetime.now()
		result = (
			aid, board, title, url, push, author, published_date, category, page, is_reply, parent, crawled_date
			)
		c.execute('INSERT INTO Article_Directory (Aid, Board, Title, Url, Push, Author, Publish_Date, Category, Page, Is_Reply, Parent, Crawled_Date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', result)
		#print(result)
		#print('Date: %s Category: %s Title: %s Author: %s Push: %d \n %s \n' % (published_date.strftime('%Y/%m/%d'), category, title, author, push, url) )
	conn.commit()

conn = sqlite3.connect('data/ptt.db')
board = sys.argv[3]
c = conn.cursor()
for i in range(int(sys.argv[1]), int(sys.argv[2])+1):
	crawlPage(i)
c.close()

