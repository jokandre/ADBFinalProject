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
    def __init__(self, name, email, gender, Fb_id, access_token, head_photo):
        self.name = name
        self.email = email
        self.gender = gender
        self.Fb_id = Fb_id
        self.access_token = access_token
        self.head_photo = head_photo

    def find(self):
        user = graph.find_one('User', 'Fb_id', self.Fb_id)
        return user

    def find_id(self):
        query = '''
        MATCH (user:User)
        WHERE user.Fb_id = {Fb_id}
        RETURN ID(user) as id
        '''
        return graph.run(query, Fb_id=self.Fb_id)

    def register(self):
        if not self.find():
            user = Node('User', name=self.name, email=self.email, gender=self.gender, Fb_id=self.Fb_id, access_token=self.access_token, head_photo=self.head_photo)
            graph.create(user)
            return True
        else:
            return False

    def add_fb_likes(self, likes):
        user = self.find()
        for like in likes:
            rel = Relationship(user, 'LIKE', Node('Likes', name=like['name'], id=like['id']), created_time=like['created_time'])
            graph.merge(rel)

    def add_fb_friends(self, friends):
        user = self.find()
        for friend in friends:
            rel = Relationship(user, 'FRIEND', Node('User', name=friend['name'], id=friend['id']))
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

class Diary(object):
    """docstring for diary"""
    def __init__(self, owner_id):
        super(Diary, self).__init__()
        self.owner_id = owner_id

    def get_owner(self):
        user = graph.node(self.owner_id)
        return user

    def get_all_diary(self):
        query = '''
        MATCH (n:User) - [:PUBLISHED] - (D)  where ID(n)={id} RETURN D as Diary LIMIT 25
        '''
        return graph.run(query, id=self.owner_id)

    def add_diary(self, title, content, latitude, longitude, category, location, address):
        user = self.get_owner()
        diary = Node(
            'Diary',
            id=str(uuid.uuid4()),
            title=title,
            content=content,
            timestamp=timestamp(),
            date=date(),
            lat=latitude,
            lon=longitude,
            category=category,
            location=location,
            address=address
        )
        rel = Relationship(user, 'PUBLISHED', diary)
        graph.create(rel)
        return ('', 200)
