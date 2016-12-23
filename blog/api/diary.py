from ..models import Diary   # get_todays_recent_posts
from ..invalidusage import InvalidUsage
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory
from flask.json import jsonify

def create():
	json_dict = request.get_json()
	if json_dict is None:
		raise InvalidUsage("Mimetype is not application/json!")
	else:
		try:
			id = json_dict['id']
			title = json_dict['title']
			content = json_dict['content']
			latitude = json_dict['latitude']
			longitude = json_dict['longitude']
			category = json_dict['category']
		except (ValueError, KeyError, TypeError) as error:
			print error
			raise InvalidUsage("Missing Parameters!")

		if (id and title and content and latitude and longitude and category) is None:
			raise InvalidUsage("Missing Parameters!")
		else:
			try:
				id = int(id)
				latitude = int(latitude)
				longitude = int(longitude)
			except ValueError:
				raise InvalidUsage("id, latitude, longitude should be int!")
			diary = Diary(id)
			return diary.add_diary(title, content, latitude, longitude, category)

def get_all_diary():
	id = request.args.get('id')
	if id is None:
		raise InvalidUsage("Missing Parameters!")
	else:
		try:
			id = int(id)
		except ValueError:
			raise InvalidUsage("id should be int!")
		diary = Diary(id)
		db_cursor = diary.get_all_diary()
		return jsonify(db_cursor.data())
