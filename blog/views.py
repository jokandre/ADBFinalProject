from .api import member
from .api import diary
from .api import comment
# from .api import pair
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory, jsonify
from invalidusage import InvalidUsage
from flask.json import jsonify


app = Flask(__name__)

@app.route('/')
def index():
    if 'id' in session:
        return redirect(url_for('main'))
    else:
        return redirect(url_for('login'))

@app.route('/index', methods=['GET'])
def main():
    session_check('render_page')
    return render_template('index.html')

@app.route('/create_diary', methods=['GET'])
def create_diary():
    session_check('render_page')
    return render_template('create_diary.html')

@app.route('/friends', methods=['GET'])
def friends():
    session_check('render_page')
    return render_template('friends.html')

@app.route('/my_friends', methods=['GET'])
def my_friends():
    session_check('render_page')
    return render_template('my_friends.html')

@app.route('/search', methods=['GET'])
def search():
    session_check('render_page')
    return render_template('search.html')

@app.route('/profile', methods=['GET'])
def profile():
    session_check('render_page')
    return render_template('profile.html', me=member.get_my_info())

@app.route('/personal', methods=['GET'])
def personal():
    session_check('render_page')
    return render_template('personal.html', me=member.get_my_info())

@app.route('/browse_diary', methods=['GET'])
def browse_diary():
    session_check('render_page')
    return render_template('browse_diary.html')

@app.route('/other_profile', methods=['GET'])
def other_profile():
    session_check('render_page')
    return render_template('other_profile.html')

@app.route('/keyword', methods=['GET'])
def keyword():
    session_check('render_page')
    return render_template('keyword.html')

@app.route('/similar_diary', methods=['GET'])
def similar_diary():
    session_check('render_page')
    return render_template('similar_diary.html')

@app.route('/test_map', methods=['GET'])
def test_map():
    session_check('render_page')
    return render_template('test_map.html')

# serving static file such as js css.
@app.route('/static/<path:filename>')
def send_static(filename):
    return send_from_directory('static', filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return member.register()
    if 'id' in session:
        return redirect(url_for('main'))
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the id from the session if it's there
    session.pop('id', None)
    return redirect(url_for('login'))

@app.route('/member/<path:path>', methods=['GET', 'POST', 'DELETE'])
def member_api(path):
    print 'Request path: %s' % path
    session_check('api')
    if request.method == 'GET':
        if path == 'api/v1/me/info':
            return member.get_my_info()
        elif path == 'api/v1/profile':
            return member.get_profile()
        elif 'api/v1/friends' in path:
            # API GET: /member/api/v1/friends/me
            if path == 'api/v1/friends/me':
               return member.get_my_friends()
            # API GET: /member/api/v1/frineds/common-friends
            elif path == 'api/v1/friends/of-friends':
                return member.get_friends_of_friends()
            # API GET: /member/api/v1/friends/common-likes/users
            elif path == 'api/v1/friends/common-likes/users':
                return member.get_common_likes_users()
            # API GET: /member/pi/v1/frineds/common-likes?other_id=x
            elif path == 'api/v1/friends/common-likes':
                # params: other_id
                return member.get_common_likes()
            else:
                raise InvalidUsage("Wrong URL", 404)
        elif 'api/v1/search' in path:
            # API GET: /member/api/v1/search/nearby
            if path == 'api/v1/search/nearby':
                # params: distance_km
                return member.get_nearby_member()
            elif path == 'api/v1/search/name':
                #params : name
                return member.search_name()
            else:
                raise InvalidUsage("Wrong URL", 404)
        else:
            raise InvalidUsage("Wrong URL", 404)
    elif request.method == 'POST':
        session_check('api')
        # API TODO POST- update user info
        if path == 'api/v1/me/update-info':
            return member.update_my_info()
        elif path == 'api/v1/me/update-location':
            return member.update_location()
        elif path == 'api/v1/befriend':
            return member.create_friendship()
        else:
            raise InvalidUsage("Wrong URL", 404)
    elif request.method == 'DELETE':
        if path == 'api/v1/unfriend':
            return member.delete_friendship()
    else:
        raise InvalidUsage("Something Wrong.", 404)

@app.route('/diary/<path:path>', methods=['GET', 'POST'])
def diary_api(path):
    print 'Request path: %s' % path
    if request.method == 'GET':
        session_check('api')
        if 'api/v1/' in path:
            if 'api/v1/search/' in path:
                if path == 'api/v1/search/category':  # API GET: /diary/api/v1/search/category?category=x&timestamp=x
                    return diary.get_diary_by_category()

                elif path == 'api/v1/search/nearby':  # API GET: /diary/api/v1/search/nearby?distance_km=x
                    return diary.get_nearby_diary()

                elif path == 'api/v1/search/all':
                    return diary.search_diary()

            if path == 'api/v1/me':  # API GET: /diary/api/v1/me
                return diary.get_my_diary()

            elif path == 'api/v1/get':
                return diary.get_diary_by_did()

            elif path == 'api/v1/someone':  # API GET: /diary/api/v1/someone?id=x
                return diary.get_someone_diary()

            elif path == 'api/v1/friends':  # API GET: /diary/api/v1/friends
                return diary.get_friends_diary()
            elif path == 'api/v1/similar': #API GET: /diary/api/v1/similar
                return diary.get_similar_diary()

            else:
                raise InvalidUsage("Wrong URL", 404)
        else:
            raise InvalidUsage("Wrong URL", 404)
    elif request.method == 'POST':
        session_check('api')
        # API POST: /diary/api/v1/create
        if path == 'api/v1/create':
            return diary.create()
        else:
            raise InvalidUsage("Wrong URL", 404)
    else:
        raise InvalidUsage("Something Wrong.", 404)

@app.route('/comment/<path:path>', methods=['GET', 'POST'])
def comment_api(path):
    print 'Request path: %s' % path
    if request.method == 'GET':
        session_check('api')
        # API GET: /comment/api/v1/get
        if path == 'api/v1/get':
            return comment.get()
        else:
            raise InvalidUsage("Wrong URL", 404)
    elif request.method == 'POST':
        session_check('api')
        # API POST: /comment/api/v1/create
        if path == 'api/v1/create':
            return comment.create()
        else:
            raise InvalidUsage("Wrong URL", 404)
    else:
        raise InvalidUsage("Something Wrong.", 404)



@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    if error.get_error_type() == 'redirectToLoginPage':
        return redirect(url_for('login'))
    else:
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

def session_check(request_type):
    # request_type only will be api or render_page.
    if request_type == 'api':
        if 'id' not in session:
            raise InvalidUsage("unauthorized", 401)
    elif request_type == 'render_page':
        if 'id' not in session:
            raise InvalidUsage(None, None, None, "redirectToLoginPage")
