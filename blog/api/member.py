from ..models import User   # get_todays_recent_posts
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory

def register():
    username = request.form['username']
    # For postgreSQL
    if not User(username).register():
        flash('A user with that username already exists.')
    else:
        session['username'] = username
        flash('Logged in.')
        return redirect(url_for('index'))
