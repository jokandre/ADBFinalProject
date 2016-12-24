import facebook
import requests
from ..invalidusage import InvalidUsage

def get_fb_frends(Fb_id, ACCESS_TOKEN):
	graph = facebook.GraphAPI(ACCESS_TOKEN)
	try:
		friends = graph.get_connections("me", "friends")
	except facebook.GraphAPIError as e:
		raise InvalidUsage(str(e))
	all_friends = []
	# Wrap this block in a while loop so we can keep paginating requests until
	# finished.
	while(True):
		try:
			for friend in friends['data']:
				all_friends.append(friend)
			# Attempt to make a request to the next page of data, if it exists.
			friends = requests.get(friends['paging']['next']).json()
		except KeyError:
			# When there are no more pages (['paging']['next']), break from the
			# loop and end the script.
			break
	return all_friends

def get_fb_likes(Fb_id, ACCESS_TOKEN):
	graph = facebook.GraphAPI(ACCESS_TOKEN)
	try:
		likes = graph.get_connections("me", "likes")
	except facebook.GraphAPIError as e:
		raise InvalidUsage(str(e))
	all_likes = []
	# Wrap this block in a while loop so we can keep paginating requests until
	# finished.
	while(True):
		try:
			for like in likes['data']:
				all_likes.append(like)
			# Attempt to make a request to the next page of data, if it exists.
			likes = requests.get(likes['paging']['next']).json()
		except KeyError:
			# When there are no more pages (['paging']['next']), break from the
			# loop and end the script.
			break
	return all_likes
