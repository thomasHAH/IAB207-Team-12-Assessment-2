#Commented

from . import db
from datetime import datetime, time
from flask_login import UserMixin

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    
    #A user can have many bookings
    bookings = db.relationship('Booking', backref='user', lazy=True)

    #NEW
    #Relationship: a user can have many comments
    #This creates a one-to-many relationship:
    # - One user can have many comments.
    # - The 'backref' makes it so each Comment automatically gets an 'author' attribute
    #   (so we can do comment.author to get the User who wrote it).
    # - lazy=True means comments are loaded only when accessed (not upfront)
    
    #users can "review" many events, and events can be "reviewed" by many
    #users but the link happens through the Comment model rather than being a
    #direct many-to-many.
    comments = db.relationship('Comment', backref='author', lazy=True)
    
# Event Model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.Text, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), nullable=False)
    features = db.Column(db.Text, default='regular')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    #relationship so we can access the creator directly as an object
    creator = db.relationship('User', backref='events_created', lazy=True)
    
    #Before it executed immediately when the model is loaded, not each time a new row is created
    date = db.Column(db.DateTime, default=datetime.utcnow)  
    #removed time, not really needed
    
    #NEW: store image filename/path
    image_file = db.Column(db.String(255), nullable=True, default='default.jpg')
    
    #An event can have many bookings
    bookings = db.relationship('Booking', backref='event', lazy=True)
    
    #NEW
    #Relationship: an event can have many comments
    #Another one-to-many relationship:
    # - One event can have many comments.
    # - The 'backref' makes it so each Comment automatically gets an 'event' attribute
    #(so we can do comment.event to get the Event it belongs to)
    # - lazy=True means only loaded when used.
    comments = db.relationship('Comment', backref='event', lazy=True)

# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    #Foreign keys
    #These are the foreign keys that lead back to the user and event tables.
    # - user_id links each comment to the user who created it.
    # - event_id links each comment to the event it belongs to
    #together, they let us know who wrote what comment on which event
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    
    #Example of how the foreign key + relationship works in practice:
    #If we set the foreign key manually:
    #comment.user_id = 5
    # -> SQLAlchemy understands this means the comment belongs to the User with id=5.
    #Because of backref='author' in the relationship, we can also do:
    #comment.author
    # -> This automatically gives us the actual User object (not just the id).

    #Same logic applies for events:
    #comment.event_id = 3
    # -> Links the comment to the Event with id=3,
    #and with backref='event', comment.event will return that Event object.

#This is new
# Order Model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

#Booking model utilised for tickets to the event
#Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Primary key for the table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # User foriegn key
    event_id = db.Column(db.Integer, db.ForeignKey('event.id')) # Event foreign key
    price = db.Column(db.Float, default=0.0) # NOTE this is set to a float as there could be cents in the price
    date = db.Column(db.DateTime, default=datetime.utcnow) # NOTE this is just storing when the booking was made
    quantity = db.Column(db.Integer, default=1) # NOTE this is stored as integer as there shouldn't ever be hald a event ticket

    #NEW RELATIONSHIP
    
    #This creates a direct relationship between the Booking and Event models.
    #It allows us to access the event linked to a booking easily: for example:
    # - booking.event.title -> gets the title of the event for that booking
    # - booking.event.date -> gets the event date
    #
    #The 'backref' part adds a reverse reference so we can also do:
    # - event.bookings -> gets a list of all bookings for that event
    #
    #This relationship is required for the "My Bookings" page to display
    #event details (title, date, description, etc.) for each booking record.
    #event = db.relationship('Event', backref='bookings')
    
    
    
    #New
    # Added this just to check the simple task of the list
    # Explained why I decided to set the table columns next to each of the keys