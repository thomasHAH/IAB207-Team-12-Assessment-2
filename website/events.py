#commented

#import the necessary modules and functions from Flask and Flask-Login
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from flask import current_app
from . import db  #import the database instance from init.py
from .models import Event #import the event model
from .forms import EventForm #import the eventform form class

#creating new blueprint for event-related routes
#events is teh blueprint. init.py has access to it
events_bp = Blueprint('events', __name__)

#This is the route we are using for creating a new event
#only accessible to logged-in users because of login_required
@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    #create instance of the eventform
    form = EventForm()
    #check if form has been submitted and validated
    if form.validate_on_submit():
        filename = None #default to None in case no image is uploaded
        
        #UPLOADING IMAGE
        if form.image.data:
            #Check if the user actually selected a file in the image field
            #Secure the filename (remove special chars)
            #Removes unsafe characters
            #Can prevent traversal attacks
            filename = secure_filename(form.image.data.filename)
            #Save to static/uploads
            #Build the full path where the file will be saved
            #current_app.root_path = the Flask apps root directory
            filepath = os.path.join(current_app.root_path, 'static/uploads', filename)
            #thhen gotta save the uploaded image file to the filepath on the disk
            form.image.data.save(filepath)
        
    
        #create new event object with data from the form
        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            capacity=form.capacity.data,
            features=form.features.data,
            date=form.date.data,
            created_by=current_user.name, #link event to logged in user
            image_file=filename  #store filename in DB 
        )
        #add to sqlite database and save changes
        db.session.add(new_event)
        db.session.commit()
        #flash message
        flash('Event created successfully!', 'success')
        #redirect user to the list of events page
        return redirect(url_for('events.list_events')) 
    #if get requrest or form not valid, render the create event form
    return render_template('create_event.html', form=form)

#route for listing all events
@events_bp.route('/list')
def list_events():
    #gotta query all the events from the database, ordered by data ascending
    events = Event.query.order_by(Event.date.asc()).all()
    #render the template passing in the events
    return render_template('list_events.html', events=events)
