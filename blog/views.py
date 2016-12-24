from .api import member
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory, jsonify

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

@app.route('/_get_facebook_login', methods=['POST'])
def get_facebook_login():
    #facebook_id = request.args.get('facebook_id', 0, type=int)
    facebook_id = request.args.get('facebook_id')
    #name = request.args.get('name', '', type=str)
    name = request.args.get('name')

    if facebook_id:
    #user = Users.query.filter_by(facebook_id=facebook_id).first()
        print('User Name: '+ name +' id: '+ facebook_id)
        print('Data: '+ str(data))
    #if not user:
    #    print('Not user yet')
      #user = Users(facebook_id,name)
      #db.session.add(user)
      #db.session.commit()
    #session['user'] = user
    return jsonify(result=1)
