from ..models import Diary   # get_todays_recent_posts
from ..invalidusage import InvalidUsage
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory
from flask.json import jsonify

def create():
	id = session['id']
	json_dict = request.get_json()
	if json_dict is None:
		raise InvalidUsage("Mimetype is not application/json!")
	else:
		try:
			title = json_dict['title']
			content = json_dict['content']
			latitude = json_dict['latitude']
			longitude = json_dict['longitude']
			location = json_dict['location']
			address = json_dict['address']
			category = json_dict['category']
			permission = json_dict['permission']
		except (ValueError, KeyError, TypeError) as error:
			raise InvalidUsage("Missing Parameters: " + str(error))
		try:
			latitude = float(latitude)
			longitude = float(longitude)
		except ValueError:
			raise InvalidUsage("latitude and longitude should be float!")
		return Diary.add_diary(id, title, content, latitude, longitude, category, location, address, permission)

def get_all_diary():
	id = session['id']
	db_cursor = Diary.get_all_diary(id)
	return jsonify(db_cursor.data())

def get_nearby_diary():
	# NOT DONE
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
