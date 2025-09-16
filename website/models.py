#Need comments here

from . import db
from datetime import datetime, time
from flask_login import UserMixin

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)

# Event Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.Text, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), nullable=False)
    features = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow().date())
    time = db.Column(db.Time, default=lambda: datetime.utcnow().time())
    
    #NEW: store image filename/path
    image_file = db.Column(db.String(255), nullable=True, default='default.jpg')

# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))

# Order Model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

