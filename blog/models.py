from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
from datetime import datetime
import os
import uuid

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

graph = Graph(url + '/db/data/', username=username, password=password)

class User:
    def __init__(self, name, email, gender, fb_id, access_token, portrait):
        self.name = name
        self.email = email
        self.gender = gender
        self.fb_id = fb_id
        self.access_token = access_token
        self.portrait = portrait

    @staticmethod
    def find(fb_id):
        user = graph.find_one('User', 'fb_id', fb_id)
        return user

    @staticmethod
    def register(name, email, gender, fb_id, access_token, portrait):
        if not User.find(fb_id):
            query = '''
            CREATE (u:User {name: {name}, email: {email}, gender: {gender}, fb_id: {fb_id}, access_token: {access_token}, portrait: {portrait}})
            RETURN ID(u)
            '''
            return graph.run(query, name=name, email=email, gender=gender, fb_id=fb_id, access_token=access_token, portrait=portrait).evaluate()
        else:
            return False

    @staticmethod
    def add_fb_likes(uid, likes):
        user = graph.node(uid)
        for like in likes:
            rel = Relationship(user, 'LIKE', Node('Likes', name=like['name'], id=like['id']), created_time=like['created_time'])
            graph.merge(rel)

    @staticmethod
    def add_fb_friends(uid, friends):
        user = graph.node(uid)
        for friend in friends:
            rel = Relationship(user, 'FRIEND', Node('User', name=friend['name'], fb_id=friend['id']))
            graph.merge(rel)

    def add_post(self, title, tags, text):
        user = self.find()
        post = Node(
            'Post',
            id=str(uuid.uuid4()),
            title=title,
            text=text,
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, 'PUBLISHED', post)
        graph.create(rel)

        tags = [x.strip() for x in tags.lower().split(',')]
        for name in set(tags):
            tag = Node('Tag', name=name)
            graph.merge(tag)

            rel = Relationship(tag, 'TAGGED', post)
            graph.create(rel)

    def like_post(self, post_id):
        user = self.find()
        post = graph.find_one('Post', 'id', post_id)
        graph.merge(Relationship(user, 'LIKED', post))

    def get_recent_posts(self):
        query = '''
        MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
        WHERE user.username = {username}
        RETURN post, COLLECT(tag.name) AS tags
        ORDER BY post.timestamp DESC LIMIT 5
        '''

        return graph.run(query, username=self.username)

    def get_similar_users(self):
        # Find three users who are most similar to the logged-in user
        # based on tags they've both blogged about.
        query = '''
        MATCH (you:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
              (they:User)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        WHERE you.username = {username} AND you <> they
        WITH they, COLLECT(DISTINCT tag.name) AS tags
        ORDER BY SIZE(tags) DESC LIMIT 3
        RETURN they.username AS similar_user, tags
        '''

        return graph.run(query, username=self.username)

    def get_commonality_of_user(self, other):
        # Find how many of the logged-in user's posts the other user
        # has liked and which tags they've both blogged about.
        query = '''
        MATCH (they:User {username: {they} })
        MATCH (you:User {username: {you} })
        OPTIONAL MATCH (they)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag:Tag),
                       (you)-[:PUBLISHED]->(:Post)<-[:TAGGED]-(tag)
        RETURN SIZE((they)-[:LIKED]->(:Post)<-[:PUBLISHED]-(you)) AS likes,
               COLLECT(DISTINCT tag.name) AS tags
        '''

        return graph.run(query, they=other.username, you=self.username).next

    @staticmethod
    def update_location(uid, lat, lon):
        query = '''
        MATCH (u) WHERE ID(u) = {which}
        SET u.wkt = {wkt}
        WITH u AS u
        CALL spatial.addNode('geom', u) YIELD node
        RETURN COUNT(node)
        '''

        return graph.run(query, which=uid, wkt=lon_lat_to_wkt(lon, lat))

    # @staticmethod
    # def get_nearby_member(uid, distance):




def get_todays_recent_posts():
    query = '''
    MATCH (user:User)-[:PUBLISHED]->(post:Post)<-[:TAGGED]-(tag:Tag)
    WHERE post.date = {today}
    RETURN user.username AS username, post, COLLECT(tag.name) AS tags
    ORDER BY post.timestamp DESC LIMIT 5
    '''

    return graph.run(query, today=date())

def timestamp():
    epoch = datetime.utcfromtimestamp(0)
    now = datetime.now()
    delta = now - epoch
    return delta.total_seconds()

def date():
    return datetime.now().strftime('%Y-%m-%d')

def lon_lat_to_wkt(lon, lat):
    return 'POINT (' + str(lon) + ' ' + str(lat) + ')'

def wkt_to_lat_long(wkt):
    lon = float(wkt[wkt.find('(')+1: wkt.find(' ', beg=wkt.find('('))])
    lat = float(wkt[wkt.find(' ', beg=wkt.find('('))+1: -1])
    return lat, lon

class Diary(object):
    """docstring for diary"""
    def __init__(self, owner_id):
        super(Diary, self).__init__()
        self.owner_id = owner_id

    @staticmethod
    def get_owner(owner_id):
        user = graph.node(self.owner_id)
        return user

    @staticmethod
    def get_all_diary(owner_id):
        query = '''
        MATCH (n:User) - [:PUBLISHED] - (D)  where ID(n)={id} RETURN D as Diary LIMIT 25
        '''
        return graph.run(query, id=owner_id)

    @staticmethod
    def add_diary(owner_id, self, title, content, latitude, longitude, category, location, address):
        user = Diary.get_owner(owner_id)
        diary = Node(
            'Diary',
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            timestamp=timestamp(),
            date=date(),
            latitude = latitude,
            longitude = longitude,
            wkt=lon_lat_to_wkt(longitude, latitude),
            category=category,
            location=location,
            address=address
        )
        rel = Relationship(user, 'PUBLISHED', diary)
        graph.create(rel)

        query = '''
        MATCH (d:Diary) WHERE d.id = {which}
        WITH d AS d
        CALL spatial.addNode('geom', d)
        RETURN count(*)
        '''

        graph.run(query, which=str(uuid.uuid4()))

        return ('', 200)
