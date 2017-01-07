# coding=utf-8

from time import sleep
import json
import requests
import urllib
from pyquery import PyQuery as pq
import sqlite3
import sys
import datetime
import time
import re
import random
import math
import csv

base_url='https://www.ptt.cc'

class User:
	def __init__(self, data):
		(
			self.Uid,
			self.Gender,
			_,
			_,
			_,
			_,
			self.IP,
			_,
			self.Lon,
			self.Lat,
			self.City,
			self.Region
		) = data

		self.Lon = self.rand_generator(self.Lon)
		self.Lat = self.rand_generator(self.Lat)

		self.WKT = 'POINT ({0} {1})'.format('%.6f'%self.Lon, '%.6f'%self.Lat)

		self.get_random_properties()

	def rand_generator(self, target):
		f = str(target).split('.')[1]
		if f:
			while len(f) <= 6:
				f += str(random.randint(0, 9))
			f = float(f) * 0.0000001
			return math.floor(target)+round(f, 6)
		else:
			return target

	def get_random_properties(self):
		self.Age = random.randint(18, 50)
		if self.Gender == 'male':
			self.Height = random.randint(160, 185)
			self.Weight = random.randint(60, 100)
		else:
			self.Height = random.randint(150, 185)
			self.Weight = random.randint(45, 80)
		m = random.randint(1, 12)
		d = random.randint(1, 28)
		self.Birthday = datetime.date(2016-self.Age, m, d).isoformat().replace('-', '/')

	def get_export_list(self):
		return [self.Uid, self.Height, self.Weight, self.Age, self.Birthday, '%.6f'%self.Lon, '%.6f'%self.Lat, self.WKT, self.City, self.City+', '+self.Region]



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
			_,
			self.C1,
			self.C2,
			self.C3,
			self.C4,
			self.C5,
			self.C6,
			self.C7,
			self.C8,
			_,
			_,
			_,
			self.City,
			self.Region
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


def getUsers():
	Users = []
	for row in c.execute("SELECT * FROM User JOIN IP_Geolocation ON User.user_ip = IP_Geolocation.IP"):
		Users.append(User(row))
	return Users

def exportUserDetail(user, writter):
	writter.writerow(user.get_export_list())


conn = sqlite3.connect('data/ptt_category.db')
c = conn.cursor()
board, cate = ('diary', '')
Articles = getUsers()
i=0

with open('data/User_Detail_v2.csv', 'w') as f:
	writter = csv.writer(f)
	writter.writerow(['id', 'height', 'weight', 'age', 'birthday', 'longitude', 'latitude', 'wkt', 'location', 'address'])
	for article in Articles:
		i+=1;
		print('Dealing %d out of %d' % (i, len(Articles)))
		exportUserDetail(article, writter)
		
c.close()
	


