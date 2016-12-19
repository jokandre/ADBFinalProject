from ..models import User   # get_todays_recent_posts
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory

def register():
	json_dict = request.get_json()
	name = json_dict['name']
	email = json_dict['email']
	gender = json_dict['gender']
	Fb_id = json_dict['id']
	print json_dict['name']
	# username = request.form['username']
	if not User(name, email, gender, Fb_id).register():
		session['name'] = name
		return redirect(url_for('main'))
		flash('A user with that username already exists.')
	else:
		session['name'] = name
		flash('Logged in.')
		return redirect(url_for('main'))
