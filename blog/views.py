from .api import member
from .api import diary
from invalidusage import InvalidUsage
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory
from flask.json import jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/index', methods=['GET'])
def main():
    return render_template('index.html')

# serving static file such as js css.
@app.route('/static/<path:filename>')
def send_static(filename):
    return send_from_directory('static', filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return member.register()
    return render_template('login.html')

@app.route('/diary/<path:path>', methods=['GET', 'POST'])
def diary_API(path):
    print 'You want path: %s' % path
    if request.method == 'GET':
        # API GET: /diary/api/v1/get?id=x
        if path == 'api/v1/get':
           return diary.get_all_diary()
    elif request.method == 'POST':
        # API POST: /diary/api/v1/create
        if path == 'api/v1/create':
            return diary.create()
    else:
        return 'Something Wrong!'

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
