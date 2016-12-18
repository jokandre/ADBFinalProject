from .models import User   # get_todays_recent_posts
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')

# serving static file such as js css.
@app.route('/static/<path:filename>')
def send_static(filename):
    return send_from_directory('static', filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']

        # For postgreSQL
        if not User(username).register():
            flash('A user with that username already exists.')
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/index.html', methods=['GET'])
def main():
    return render_template('index.html')
