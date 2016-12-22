from .api import member
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')

# serving static file such as js css.
@app.route('/static/<path:filename>')
def send_static(filename):
    return send_from_directory('static', filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return member.register()
    return render_template('login.html')


@app.route('/index', methods=['GET'])
def main():
    return render_template('index.html')
