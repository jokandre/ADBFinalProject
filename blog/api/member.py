from ..models import User   # get_todays_recent_posts
from ..invalidusage import InvalidUsage
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory
import fb_API

def register():
	json_dict = request.get_json()
	if json_dict is None:
		raise InvalidUsage("Mimetype is not application/json!")
	else:
		try:
			name = json_dict['name']
			email = json_dict['email']
			gender = json_dict['gender']
			Fb_id = json_dict['id']
			access_token = json_dict['access_token']
		except (ValueError, KeyError, TypeError) as error:
			raise InvalidUsage("Missing Parameters: " + str(error))
		me = User(name, email, gender, Fb_id)
		if me.register():
			#  Not yet register before.
			me.add_fb_likes(fb_API.get_fb_likes(Fb_id, access_token))
		me.add_fb_friends(fb_API.get_fb_frends(Fb_id, access_token))
		session['Fb_id'] = Fb_id
		return redirect(url_for('main'))
