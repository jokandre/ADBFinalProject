from ..models import User   # get_todays_recent_posts
from ..invalidusage import InvalidUsage
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory
from jobs import fb_graph_api
from flask.json import jsonify


def register():
	json_dict = request.get_json()
	if json_dict is None:
		raise InvalidUsage("Mimetype is not application/json!")
	else:
		try:
			name = json_dict['name']
			email = json_dict['email']
			gender = json_dict['gender']
			fb_id = json_dict['id']
			access_token = json_dict['access_token']
			portrait = json_dict['portrait']
		except (ValueError, KeyError, TypeError) as error:
			raise InvalidUsage("Missing Parameters: " + str(error))
		uid = User.register(name, email, gender, fb_id, access_token, portrait)
		if uid:
			#  Not yet register before.
			User.add_fb_likes(uid, fb_graph_api.get_fb_likes(fb_id, access_token))
			User.add_fb_friends(uid, fb_graph_api.get_fb_frends(fb_id, access_token))
		else:
			uid = User.get_id(fb_id)
		session['id'] = uid
		return ('', 200)

def get_my_friends():
	id = session['id']
	friends = User.get_my_friends(id)
	return jsonify(friends)

def get_common_friends():
	id = session['id']
	common_friends = User.get_common_friends(id)
	return jsonify(common_friends)

def get_common_likes_users():
	id = session['id']
	common_likes = User.get_common_likes_users(id)
	return jsonify(common_likes)

def get_common_likes():
	id = session['id']
	other_id = request.args.get('other_id')
	common_likes = User.get_common_likes(id, other_id)
	return jsonify(common_likes)

def update_location():
	json_dict = request.get_json()
	if json_dict is None:
		raise InvalidUsage("Mimetype is not application/json!")
	else:
		try:
			latitude = json_dict['latitude']
			longitude = json_dict['longitude']
		except (ValueError, KeyError, TypeError) as error:
			raise InvalidUsage("Missing Parameters: " + str(error))
		try:
			latitude = float(latitude)
			longitude = float(longitude)
		except ValueError:
			raise InvalidUsage("latitude and longitude should be float!")
		result = User.update_location(session['id'], latitude, longitude)
		return (str(result), 200)

def get_nearby_member():
	json_dict = request.get_json()
	if json_dict is None:
		raise InvalidUsage("Mimetype is not application/json!")
	else:
		try:
			distance_km = json_dict['distance_km']
			# distance_km = 1
		except (ValueError, KeyError, TypeError) as error:
			raise InvalidUsage("Missing Parameters: " + str(error))
		try:
			distance_km = float(distance_km)
		except ValueError:
			raise InvalidUsage("latitude and longitude should be positive float!")
		db_cursor = User.get_nearby_member(session['id'], distance_km)
		return jsonify(db_cursor.data())
