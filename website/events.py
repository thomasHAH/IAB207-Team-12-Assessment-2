#commented

#import the necessary modules and functions from Flask and Flask-Login
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from flask import current_app
from . import db  #import the database instance from init.py
#adding comment import NEW
from .models import Event, Comment #import the event model
from .forms import EventForm, CommentForm #import the eventform form class

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
            location=form.location.data,
            status=form.status.data,
            cost=form.cost.data,
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
    else:
        #Check if the form submitted if not then throw error
        print(form.errors)
    #if get requrest or form not valid, render the create event form
    return render_template('create_event.html', form=form)

#route for listing all events
@events_bp.route('/list')
def list_events():
    #gotta query all the events from the database, ordered by data ascending
    events = Event.query.order_by(Event.date.asc()).all()
    #render the template passing in the events
    return render_template('list_events.html', events=events)


#NEW IMPLEMENTED CODE------------------------------------------------

#This route handles viewing a single event page.
#The <int:event_id> part in the URL makes it dynamic, so if a user visits /events/3,
#Flask passes event_id=3 into the function.
#When links are created with url_for('events.view_event', event_id=event.id),
#Flask replaces <int:event_id> with the actual event's ID from the database.
#The function then uses that ID to look up the specific event and display its details.

#This is the route to view a single event page (both get to view and then POST to submit a comment) 
    #User clicks event link -> URL /events/3 -> Flask passes event_id=3 -> Database query fetches 
    #event #3 -> Render template with that event.
@events_bp.route('/<int:event_id>', methods=['GET', 'POST'])
def view_event(event_id):
    #We look up the event by its ID, or show a 404 error if not found
    event = Event.query.get_or_404(event_id)
    
    #Create a new instance of the CommentForm so the user can submit comments
    #grabs this from the forms.py
    form = CommentForm()

    #Handle comment submission when the form is posted
    if form.validate_on_submit():
        #Ensure only logged-in users can comment
        if current_user.is_authenticated:  #only logged in users can comment
            new_comment = Comment(
                text=form.text.data,
                user_id=current_user.id, #link comment to the current user
                event_id=event.id        #link comment to the current event
            )
            #add the new comment to the database and save
            db.session.add(new_comment)
            db.session.commit()
            
            #show success message and redirect (PRG pattern)
            #should tweak these flash messages a lil to make sure they don't break the styling
            flash("Your comment has been posted!", "success")
            return redirect(url_for('events.view_event', event_id=event.id))
        else:
            #If the user is not logged in, show an error and redirect to login page
            flash("You must be logged in to comment.", "danger")
            return redirect(url_for('auth.login'))

    #For get requests or if the form is invalid, fetch existing comments for this event
    #Ordered newest-first by date_created
    comments = Comment.query.filter_by(event_id=event.id).order_by(Comment.date_created.desc()).all()
    
    #render the event detail page with event info, comment form, and existing comments
    return render_template('view_event.html', event=event, form=form, comments=comments)


# This route handles the sorting of the features on the index page
# It will pass the feature into the url that will be read and sorted 
# This is the home route and it will get all the events that are stored
@events_bp.route('/')
def home():
    # First five most recent events
    recent_events = Event.query.order_by(Event.date.desc()).limit(5).all()
    
    # Handle getting the drop down filter
    feature = request.args.get("feature")

    # Check if the feature exists in the url
    if feature:
        # From the event data filter by the feature for and return all that match
        events = Event.query.filter_by(features=feature).order_by(Event.date.asc()).all()
    else:
        # If there is no feature just get all the events
        events = Event.query.order_by(Event.date.asc()).all()
        pass

    # Return the recent events and the events data which is all the events and return just a selected event which can be used to show with the home template
    return render_template('home.html', recent_events=recent_events, selected_feature=feature, events=events)