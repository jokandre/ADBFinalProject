from ..models import Diary
from ..models import timestamp as get_timestamp
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

def get_friends_diary():
	id = session['id']
	timestamp = request.args.get('timestamp')
	if timestamp is None:
		timestamp = get_timestamp()
	else:
		timestamp = float(timestamp)
	db_cursor = Diary.get_friends_diary(id, timestamp)
	return jsonify(db_cursor.data())

def get_nearby_diary():
	distance_km = request.args.get('distance_km')
	if distance_km is None:
		raise InvalidUsage("Missing Parameters: distance_km")
	else:
		try:
			distance_km = float(distance_km)
			if distance_km < 0:
				raise ValueError('')
		except ValueError:
			raise InvalidUsage("latitude and longitude should be positive float!")
		db_cursor = Diary.get_nearby_diary(session['id'], distance_km)
		return jsonify(db_cursor.data())
