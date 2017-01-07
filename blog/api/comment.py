from ..models import Comment
from ..models import timestamp as get_timestamp
from ..models import check_permission as check_permission
from ..invalidusage import InvalidUsage
from flask import Flask, request, session, redirect, url_for, render_template, flash, send_from_directory
from flask.json import jsonify

def create():
	id=session['id']
	json_dict = request.get_json()
	if json_dict is None:
		raise InvalidUsage("Mimetype is not application/json!")
	else:
		try:
			content = json_dict['content']
			did = json_dict['did']
		except (ValueError, KeyError, TypeError) as error:
			raise InvalidUsage("Missing Parameters: " + str(error))
		if not check_permission(id, did):
			raise InvalidUsage("unauthorized", 401)
		else:
			return Comment.create(id,did,content)

def get():
	did = request.args.get('did')
	if did is None:
		raise InvalidUsage("Missing Parameters: did")
	elif not check_permission(session['id'], did):
		raise InvalidUsage("unauthorized", 401)
	else:
		db_cursor = Comment.get(did)
		return jsonify(db_cursor.data())