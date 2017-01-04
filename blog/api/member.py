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
		print(uid)
		if uid:
			#  Not yet register before.
			User.add_fb_likes(uid, fb_graph_api.get_fb_likes(fb_id, access_token))
			User.add_fb_friends(uid, fb_graph_api.get_fb_frends(fb_id, access_token))
		session['id'] = uid
		return ('', 200)
		# return redirect(url_for('main'))

def update_location():
	json_dict = request.get_json()
	if json_dict is None:
		raise InvalidUsage("Mimetype is not application/json!")
	else:
		try:
			latitude = json_dict['latitude']
			longitude = json_dict['longitude']
			# latitude = 60
			# longitude = 23
			result = User.update_location(session['id'], latitude, longitude)
		except (ValueError, KeyError, TypeError) as error:
			raise InvalidUsage("Missing Parameters: " + str(error))
	return (str(result), 200)

def get_nearby_member():
	json_dict = request.get_json()
	if json_dict is None:
		raise InvalidUsage("Mimetype is not application/json!")
	else:
		try:
			result = User.get_nearby_member(session['id'], distance)
	return (str(result), 200)