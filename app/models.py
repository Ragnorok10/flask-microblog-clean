#This is where we create DB TABLES


#Imports
from datetime import datetime, timezone
from typing import Optional
import redis.exceptions
import rq.exceptions
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from werkzeug.security import generate_password_hash, check_password_hash #used for password hashing
from flask_login import UserMixin #used for Flask-Login
from app import login # user to handle 
from hashlib import md5

#token generation & verification imports
from time import time
import jwt
#from app import app

#SearchMixin Imports
from app.search import add_to_index, remove_from_index, query_index

# NOTIFICATION IMPORTS
import json
from time import time

#TASK/JOB IMPORTS (REDIS/RQ)
import redis
import rq

# API IMPORTS
from flask import url_for

# API USER TOKEN AUTH IMPORTS
from datetime import timedelta
import secrets

#Creatte the model USER CLASS - this is going to create the USER TABLE
#sa & so are ALIASES to the above modules

#Followers association table: - not created using class as this is an AUXILARY table, has no other data besides foreign keys
followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
              )

#SearchMixins class
class SearchableMixin(object):
    @classmethod
    def search(cls, expression ,page, per_page): #cls = a different name for "self", used in this case as we are using classes (cls short for class)
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.session.scalars(query), total
    
    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__table__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

#PaginatedAPIMixins class - GENERIC & REUSABLE
class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = db.paginate(query, page=page, per_page=per_page,
                                error_out=False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None,
            }
        }
        return data

#USERS Table
class User(PaginatedAPIMixin, UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), 
                                                index=True,unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped['Posts'] = so.relationship(
        back_populates='author')
    
    #this is different, since the mapped table is created differently (sa.table - Followers)
    following: so.WriteOnlyMapped['User'] = so.relationship(
            secondary=followers, primaryjoin=(followers.c.follower_id == id),
            secondaryjoin=(followers.c.followed_id == id),
            back_populates='followers')
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')
    
    
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    
    #Message related columns
    last_message_read_time: so.Mapped[Optional[datetime]]
    messages_sent: so.WriteOnlyMapped['Message'] = so.relationship(
        foreign_keys='Message.sender_id', back_populates='author')
    messages_recieved: so.WriteOnlyMapped['Message'] = so.relationship(
        foreign_keys='Message.recipient_id', back_populates='recipient')
    
    #API TOKEN auth related columns
    token: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(32), index=True, unique=True)
    token_expiration: so.Mapped[Optional[datetime]]
    
    #Notification related columns
    notifications: so.WriteOnlyMapped['Notification'] = so.relationship(
        back_populates='user'
    )

    #Task related column
    tasks: so.WriteOnlyMapped['Task'] = so.relationship(
        back_populates='user')


    def __repr__(self):
        return '<user {}'.format(self.username)
    
    #Create passwords & hashing them
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    #Follow/Unfollow methods
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

            #Purpose: Adds a follow link (User A follows User B).
            #Check: It first checks if the user is already being followed to avoid duplicates.

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

            #Purpose: Removes the follow link (User A stops following User B).
            #Check: Only removes the user if they’re actually being followed.

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None
    
            #Purpose: Checks if the current user is already following another user.
            #How: Runs a query to see if the target user is in the .following list.
            #Returns: True if the user is being followed, False if not.
    
    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)
        
    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)
    
        #Purpose: Get the number of followers (followers_count) and followings (following_count).
        #How:
            #It builds a query using count() to count the rows in the relationship.
            #The .subquery() is required because we're counting inside another query.
    
    #DB QUERY - to get posts by other users that our user follows
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User) 
        return (
            sa.select(Posts)
            .join(Posts.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True) #OUTER JOIN
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id
            ))
            .group_by(Posts)
            .order_by(Posts.timestamp.desc())
        )
        
    #Token generation & verification methods
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms='HS256')['reset_password']
        except:
            return
        return db.session.get(User, id)
    
    #Message related methods
    def unread_message_count(self): #this function will count how many messages are unread since this will use the LAST_MESSAGE_READ_TIME field to see if any new messages have been recieved since that timestamp
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        query = sa.select(Message).where(Message.recipient == self,
                                         Message.timestamp > last_read_time)
        return db.session.scalar(sa.select(sa.func.count()).select_from(
            query.subquery()))
    
    #Notification related helper method
    def add_notification(self, name, data):
        db.session.execute(self.notifications.delete().where(
            Notification.name == name))
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n
    
    #TASK/JOB related helper functions - REDIS/RQ
    def launch_task(self, name, description, *args, **kwargs):
        rq_job = current_app.task_queue.enqueue(f'app.tasks.{name}', self.id,
                                                *args, **kwargs)
        task = Task(id=rq_job.get_id(), name=name, description=description,
                    user=self)
        db.session.add(task)
        return task

    def get_tasks_in_progress(self):
        query = self.tasks.select().where(Task.complete == False)
        return db.session.scalars(query)

    def get_task_in_progress(self, name):
        query = self.tasks.select().where(Task.name == name,
                                          Task.complete == False)
        return db.session.scalar(query)
    
    #API related helper function
    def posts_count(self): # helper method used in the TO_DICT HELPER METHOD below
        query = sa.select(sa.func.count()).select_from(
            self.posts.select().subquery())
        return db.session.scalar(query)

    def to_dict(self, include_email=False): #converts a user object to a Python representation
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.replace(
                tzinfo=timezone.utc).isoformat() if self.last_seen else None,
            'about_me': self.about_me,
            'post_count': self.posts_count(),
            'follower_count': self.followers_count(),
            'following_count': self.following_count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'following': url_for('api.get_following', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def from_dict(self, data, new_user=False): # the client passes a user representation in a request and the server needs to parse it and convert it to a User object.
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    #API USER TOKEN AUTH helper methods
    def get_token(self, expires_in=3600):
        now = datetime.now(timezone.utc)
        if self.token and self.token_expiration.replace(
                tzinfo=timezone.utc) > now + timedelta(seconds=60):
            return self.token
        self.token = secrets.token_hex(16)
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.now(timezone.utc) - timedelta(
            seconds=1)

    @staticmethod
    def check_token(token):
        user = db.session.scalar(sa.select(User).where(User.token == token))
        if user is None or user.token_expiration.replace(
                tzinfo=timezone.utc) < datetime.now(timezone.utc):
            return None
        return user

#Loading USER_LOADER function
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

#Posts table
class Posts(SearchableMixin, db.Model):
    __searchable__ = ['body']
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    
    author: so.Mapped[User] = so.relationship(back_populates='posts')

    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    def __repr__(self):
        return '<Post {}'.format(self.body)
    
#MESSAGES TABLE
class Message(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    sender_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                                 index=True)
    recipient_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                                    index=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    
    #these columns are the REVERSE RELATIONSHIPS for the BACK_POPULATES argumments in the USERS table
    author: so.Mapped[User] = so.relationship(
        foreign_keys='Message.sender_id',
        back_populates='messages_sent')
    recipient: so.Mapped[User] = so.relationship(
        foreign_keys='Message.recipient_id',
        back_populates='messages_recieved')
    
    def __repr__(self):
        return '<Message {}>'.format(self.body)

#data types:
#str - varchar in sql

#NOTIFICATIONS CLASS (TABLE)
class Notification(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),
                                               index=True)
    timestamp: so.Mapped[float] = so.mapped_column(index=True, default=time)
    payload_json: so.Mapped[str] = so.mapped_column(sa.Text)

    user: so.Mapped[User] = so.relationship(back_populates='notifications')

    def get_data(self):
        return json.loads(str(self.payload_json))
    
#TASK CLASS (TABLE) - will store task/jobs for users as jobs don't retain data long-terms (REDIS/RQ)
class Task(db.Model):
    id: so.Mapped[str] = so.mapped_column(sa.String(36), primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(128))
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id))
    complete: so.Mapped[bool] = so.mapped_column(default=False)

    user: so.Mapped[User] = so.relationship(back_populates='tasks')

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100