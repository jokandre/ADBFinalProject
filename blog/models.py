from py2neo import Graph, Node, Relationship
from passlib.hash import bcrypt
import psycopg2
from datetime import datetime
import os
import uuid

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')

graph = Graph(url + '/db/data/', username=username, password=password)

psqlconn = psycopg2.connect("dbname='dday' user=\'{0}\' host= 'localhost' password = \'{1}\'".format(os.environ.get("PSQL_USERNAME"), os.environ.get("PSQL_PASSWORD")))
psql = psqlconn.cursor()

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
    def get_id(fb_id):
        query = '''
        MATCH (n:User {fb_id : {fb_id}}) RETURN n.id as id
        '''
        return graph.run(query, fb_id=fb_id).evaluate()

    @staticmethod
    def register(name, email, gender, fb_id, access_token, portrait):
        user = User.find(fb_id)
        if not user:
            id = str(uuid.uuid1())
            query = '''
            CREATE (u:User {id: {id}, name: {name}, email: {email}, gender: {gender}, fb_id: {fb_id}, access_token: {access_token}, portrait: {portrait}})
            RETURN u.id
            '''
            return graph.run(query, id=id, name=name, email=email, gender=gender, fb_id=fb_id, access_token=access_token, portrait=portrait).evaluate()
        elif 'id' not in user:
            print 'Giving user an ID'
            id = str(uuid.uuid1())
            query = '''
            MATCH (u:User) WHERE u.fb_id = {fb_id}
            SET u.id= {id}, u.name= {name}, u.email= {email}, u.gender= {gender}, u.fb_id= {fb_id}, u.access_token= {access_token}, u.portrait= {portrait}
            RETURN u.id
            '''
            return graph.run(query, id=id, name=name, email=email, gender=gender, fb_id=fb_id, access_token=access_token, portrait=portrait).evaluate()
        else:
            return False

    @staticmethod
    def user_info(uid):
        user = graph.find_one('User', 'id', uid)
        return user

    @staticmethod
    def get_profile(id, other_uid):
        query = '''
        MATCH (other:User {id:{other_uid}})
        OPTIONAL MATCH (me:User {id:{id}}) - [r:FRIEND] - (other)
        WITH  other, CASE WHEN count(r) > 0 then True else False end as friendship
        RETURN friendship, {gender: other.gender, name: other.name, portrait: other.portrait, id: other.id} as owner
        '''
        return graph.run(query, id=id, other_uid=other_uid).data()

    @staticmethod
    def update_user_info(uid, name, birthday, residence, height, weight, interest):
        user = graph.find_one('User', 'id', uid)
        if user:
            query = '''
            MATCH (u:User) WHERE u.id = {id}
            SET u.name= {name}, u.birthday = {birthday},
            u.height={height}, u.weight={weight}, u.residence = {residence}, u.interest = {interest}
            RETURN u.id
            '''
            return graph.run(query, id=uid, name=name, birthday=birthday, height=height, weight=weight, residence=residence, interest=interest).evaluate()

    @staticmethod
    def search_by_name(name):
        user = graph.find_one('User', 'name', name)
        return user

    @staticmethod
    def add_fb_likes(uid, likes):
        user = graph.find_one('User', 'id', uid)
        for like in likes:
            rel = Relationship(user, 'LIKE', Node('Likes', name=like['name'], id=like['id']))
            graph.merge(rel)

    @staticmethod
    def add_fb_friends(uid, friends):
        user = graph.find_one('User', 'id', uid)
        for friend in friends:
            rel = Relationship(user, 'FRIEND', Node('User', name=friend['name'], fb_id=friend['id']))
            graph.merge(rel)

    @staticmethod
    def get_my_friends(uid):
        query = '''
        MATCH (n:User {id:{uid}}) - [r] - (u:User)
        WITH DISTINCT(u) as friends
        RETURN friends.id as id, friends.name as name, friends.gender as gender, friends.portrait as portrait, friends.nickname as nickname
        '''
        return graph.run(query, uid=uid).data()

    @staticmethod
    def get_friends_of_friends(uid):
        query = '''
        MATCH (n:User {id:{uid}}) -[r:FRIEND]- (u:User) - [r2:FRIEND] - (v)
        where NOT (n) - [:FRIEND] - (v) AND NOT (n) = (v)
        with DISTINCT v as friends_of_friends
        RETURN friends_of_friends.id as id, friends_of_friends.name as name, friends_of_friends.gender as gender, friends_of_friends.portrait as portrait, friends_of_friends.nickname as nickname
        '''
        return graph.run(query, uid=uid).data()

    @staticmethod
    def get_common_likes_users(uid):
        query = '''
        MATCH (n:User {id:{uid}}) - [:LIKE] - (k) - [:LIKE]- (v:User)
        return v.gender as gender, v.name as name, v.portrait as portrait, v.id as id, count(k) as amount_of_common_likes
        '''
        return graph.run(query, uid=uid).data()

    @staticmethod
    def get_common_likes(uid, other_uid):
        query = '''
        MATCH (n:User {id:{uid}}) - [:LIKE] - (k) - [:LIKE]- (v:User {id:{other_uid}}) return k as common_likes
        '''
        return graph.run(query, uid=uid, other_uid=other_uid).data()

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
    def create_friendship(my_id, other_uid):
        query = '''
        OPTIONAL Match (me:User {id: {my_id}})
        OPTIONAL Match (other:User {id: {other_uid}})
        WITH me, other
        WHERE me is not null and other is not null
        MERGE (me) - [:FRIEND] -> (other)
        MERGE (other) - [:FRIEND] -> (me)
        '''
        graph.run(query, my_id=my_id, other_uid=other_uid)
        return ('', 200)

    @staticmethod
    def delete_friendship(my_id, other_uid):
        query = '''
        optional Match (me:User {id:{my_id}}) - [r:FRIEND] - (other:User {id: {other_uid}})
        with r as friendship
        where friendship is not null
        delete friendship
        '''
        graph.run(query, my_id=my_id, other_uid=other_uid)
        return ('', 200)

    @staticmethod
    def update_location(uid, lat, lon):
        query = '''
        MATCH (u) WHERE u.id = {which}
        SET u.wkt = {wkt},
        u.latitude = {lat},
        u.longitude = {lon},
        WITH u AS u
        CALL spatial.addNode('member', u) YIELD node
        RETURN COUNT(node)
        '''
        return graph.run(query, which=uid, wkt=lon_lat_to_wkt(lon, lat), lat=lat, lon=lon)

    @staticmethod
    def get_nearby_member(uid, distance_km):
        user = graph.find_one('User', 'id', uid)
        query = '''
        CALL spatial.withinDistance('member',
        {latitude: {lat}, longitude: {lon}}, {distance}) YIELD node AS m
        MATCH (m) WHERE m.id <> {id} AND NOT (m:User)-[:FRIEND]-(:User{id: {id}})
        RETURN m.gender as gender, m.name as name, m.portrait as portrait, m.id as id, m.nickname as nickname
        '''
        return graph.run(query, lat=user['latitude'], lon=user['longitude'], distance=distance_km, id=uid)

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
    lon = float(wkt[wkt.find('(') + 1: wkt.find(' ', beg=wkt.find('('))])
    lat = float(wkt[wkt.find(' ', beg=wkt.find('(')) + 1: -1])
    return lat, lon

def check_permission(uid, did):
    diary = graph.find_one('Diary', 'id', did)
    if diary['permission'] == 'public':
        return True
    else:
        query = '''
        MATCH (u:User)-[:PUBLISHED]-(d:Diary {id:{did}})
        RETURN u.id
        '''
        owner_id = graph.run(query, did=did).evaluate()
        if uid == owner_id:
            return True
        elif diary['permission'] == 'private':
            return False
        else:
            query = '''
            MATCH (u:User {id:{uid}})-[:FRIEND]-(:User {id: {owner_id}})
            RETURN u.id
            '''
            id = graph.run(query, uid=uid, owner_id=owner_id).evaluate()
            if id == uid:
                return True
            else:
                return False

class Diary:
    """docstring for diary"""
    def __init__(self, owner_id):
        super(Diary, self).__init__()
        self.owner_id = owner_id

    @staticmethod
    def get_owner(owner_id):
        user = graph.find_one('User', 'id', owner_id)
        return user

    @staticmethod
    def get_my_diary(owner_id):
        query = '''
        MATCH (n:User) - [:PUBLISHED] - (D)
        where n.id={id}
        RETURN D as Diary
        ORDER BY Diary.timestamp DESC
        '''
        return graph.run(query, id=owner_id)

    @staticmethod
    def get_someone_diary(id, someone_id):
        is_friend_query = '''
        MATCH (n:User {id:{id}})
        OPTIONAL MATCH (n) - [friend:FRIEND] - (u:User {id:{someone_id}})
        RETURN CASE WHEN count(friend) > 0 THEN TRUE
        ELSE False
        END
        '''
        is_friend = graph.run(is_friend_query, id=id, someone_id=someone_id).evaluate()
        if is_friend:
            friend_diary_query = '''
            MATCH (owner:User {id:{someone_id}}) - [:PUBLISHED] - (diary:Diary)
            WHERE diary.permission <> 'private'
            RETURN diary, {gender: owner.gender, name: owner.name, portrait: owner.portrait, id: owner.id} as owner
            ORDER BY diary.timestamp DESC
            '''
            return graph.run(friend_diary_query, someone_id=someone_id).data()
        else:
            public_diary_query = '''
            MATCH (owner:User {id:{someone_id}}) - [:PUBLISHED] - (diary:Diary)
            WHERE diary.permission = 'public'
            RETURN diary, {gender: owner.gender, name: owner.name, portrait: owner.portrait, id: owner.id} as owner
            ORDER BY diary.timestamp DESC
            '''
            return graph.run(public_diary_query, someone_id=someone_id).data()

    @staticmethod
    def get_friends_diary(uid, timestamp):
        query = '''
        MATCH (:User {id:{uid}})- [:FRIEND] - (friend:User) - [:PUBLISHED]->(diary:Diary)
        WHERE diary.timestamp < {timestamp} and diary.permission <> 'private'
        RETURN diary, {gender: friend.gender, name: friend.name, portrait: friend.portrait, id: friend.id} as friend
        ORDER BY diary.timestamp DESC LIMIT 20
        '''
        return graph.run(query, uid=uid, timestamp=timestamp).data()

    @staticmethod
    def get_diary_by_category(category, timestamp):
        query = '''
        MATCH (diary:Diary)
        WHERE diary.permission = 'public' and diary.category = {category} and diary.timestamp < {timestamp}
        RETURN diary
        ORDER BY diary.timestamp DESC LIMIT 20
        '''
        return graph.run(query, category=category, timestamp=timestamp).data()

    @staticmethod
    def add_diary(owner_id, title, content, latitude, longitude, category, location, address, permission):
        user = Diary.get_owner(owner_id)
        uuid_diary = str(uuid.uuid1())
        diary = Node(
            'Diary',
            id=uuid_diary,
            title=title,
            content=content,
            timestamp=timestamp(),
            date=date(),
            latitude=latitude,
            longitude=longitude,
            wkt=lon_lat_to_wkt(longitude, latitude),
            category=category,
            location=location,
            address=address,
            permission=permission
        )
        rel = Relationship(user, 'PUBLISHED', diary)
        graph.create(rel)

        query = '''
        MATCH (d:Diary) WHERE d.id = {which}
        CALL spatial.addNode('diary', d) YIELD node
        RETURN count(node)
        '''

        result = str(graph.run(query, which=uuid_diary).evaluate())
        if result != '1':
            print "spatial addNode error!" + result

        return ('', 200)

    @staticmethod
    def get_nearby_diary(uid, distance_km):
        user = graph.find_one('User', 'id', uid)
        query = '''
        CALL spatial.withinDistance('diary',
        {latitude: {lat}, longitude: {lon}}, {distance}) YIELD node AS d
        MATCH (d)
        WHERE NOT (d:Diary)-[:PUBLISHED]-(:User{id: {id}})
        AND NOT (d:Diary)-[:PUBLISHED]-(:User)-[:FRIEND]-(:User{id: {id}})
        AND (d.permission = "public")
        RETURN d.id AS id, d.title AS title, d.content AS content, d.timestamp AS timestamp, d.date AS date, d.category AS category, d.location AS location, d.latitude AS latitude,
        d.longitude AS longitude
        '''
        # TODO what to return?
        return graph.run(query, lat=user['latitude'], lon=user['longitude'], distance=distance_km, id=uid)

    @staticmethod
    def check_permission(id, did):
        query = '''
        MATCH (d:Diary {id:{did}})-[:PUBLISHED]-(u:User)
        RETURN d.permission AS permission, u.id AS uid
        '''
        result = graph.run(query, did=did).data()
        print result
        return True

    @staticmethod
    def get_diary_by_did(did):
        query = '''
        MATCH (p:User)-[:PUBLISHED]-(diary:Diary {id:{did}})
        RETURN {gender: p.gender, name: p.name, portrait: p.portrait, id: p.id} as owner,
        {id: diary.id, title: diary.title, content: diary.content, timestamp: diary.timestamp, date: diary.date, category: diary.category,
        location: diary.location, latitude: diary.latitude, longitude:diary.longitude} as diary
        '''
        return graph.run(query, did=did)

    @staticmethod
    def get_similar_diary(uid, did):
        query = """
        SELECT * from diary_vectors 
        WHERE did != \'{0}\' ORDER BY 
            (SELECT vector FROM diary_vectors 
            WHERE did=\'{0}\') 
        <-> vector asc limit 100
        """.format(did)
        psql.execute(query)
        candidates_tmp = psql.fetchall()
        candidates = []
        target = []
        for i in candidates_tmp:
            candidates.append(i[0])
        query = '''
        MATCH (p:User)-[:PUBLISHED]-(diary:Diary) WHERE diary.id IN ''' + str(ids) + '''
        AND NOT (diary:Diary)-[:PUBLISHED]-(:User{id: {id}})
        AND NOT (diary:Diary)-[:PUBLISHED]-(:User)-[:FRIEND]-(:User{id: {id}})
        AND (diary.permission = "public")
        RETURN {gender: p.gender, name: p.name, portrait: p.portrait, id: p.id} as owner,
        {id: diary.id, title: diary.title, content: diary.content, timestamp: diary.timestamp, date: diary.date, category: diary.category,
        location: diary.location, latitude: diary.latitude, longitude:diary.longitude} as diary limit 10
        '''

        return graph.run(query, id = uid)




class Comment:
    @staticmethod
    def get(did):
        query = '''
        MATCH (diary:Diary {id:{did}})-[:HAS]-(comment:Comment)-[:COMMENTED]-(u:User)
        RETURN comment, {gender: u.gender, name: u.name, portrait: u.portrait, id: u.id} as commentator
        '''
        return graph.run(query, did=did)

    @staticmethod
    def create(uid, did, content):
        user = graph.find_one('User', 'id', uid)
        diary = graph.find_one('Diary', 'id', did)
        uuid_comment = str(uuid.uuid1())
        comment = Node(
            'Comment',
            id=uuid_comment,
            content=content,
            timestamp=timestamp(),
            date=date()
        )
        rel = Relationship(user, 'COMMENTED', comment)
        rel2 = Relationship(diary, 'HAS', comment)
        graph.create(rel)
        graph.create(rel2)
        return ('', 200)
