#commented

#import the necessary modules and functions from Flask and Flask-Login
from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from sqlalchemy import or_, func
from datetime import datetime
from flask import current_app
from . import db  #import the database instance from init.py
#adding comment import NEW
from .models import Event, Comment, Booking #import the event model
from .forms import EventForm, CommentForm, BookingForm #import the eventform form class

#NEED TO SET THIS UP
#from flask_mail import Message


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
        
        #Their code was alot more complicated I reckon (QUT). Pretty much the same thing
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
            #REMOVED TIME
            created_by=current_user.id, #link event to logged in user
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
    
    booking_form = BookingForm()  #This gave me a nightmarew

    #calculate tickets left for display
    #I reckon this is a nice touch
    #Always showing the user the amount of tickets left
    total_booked = sum(b.quantity for b in Booking.query.filter_by(event_id=event.id).all())
    tickets_left = event.capacity - total_booked
    
    #auto-update status if sold out
    #New code
    if tickets_left <= 0 and event.status.lower() == "open":
        event.status = "sold out"
        db.session.commit()
        
    #Code here for when event owners want to edit their listing and change the status
    
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
    #had to add booking_form and also tickets_left 
    
    #had to add booking_form and tickets_left because the template expects those variables
    #without them, Jinja2 throws UndefinedError since it can’t find values for the placeholders used in view_event.html
    return render_template('view_event.html', event=event, form=form,  booking_form=booking_form, comments=comments, tickets_left=tickets_left)

#NEW 07/10/25

#This route handles displaying all events on the homepage and supports search functionality.

    #Users can:
    # - View all upcoming events (future dates only).
    # - Search for events by typing a keyword (e.g., 'indoor', 'heated', etc.) that matches
    #   an event's title, description, location, or features.

    #TECHNICAL NOTE:
    #originally, this functionality was bound to the root route ('/'), which conflicted
    #with the dynamic route '/<int:event_id>' used for viewing individual events.
    #Because Flask matched '/1' (or any integer) before the generic '/', search queries
    #like '/?q=Indoor' didn’t properly reach the intended function, the request was
    #effectively ignored or misrouted.  
    
    #By explicitly defining this route as '/home', Flask now correctly handles search 
    #queries and can filter results using case-insensitive matching (ILIKE) against 
    #multiple fields.
    
@events_bp.route('/home')
def home():
    
    #we don't need a FlaskForm here because the search uses a simple GET request
    #the user's input (?q=indoor) is passed directly through the URL query string
    #flask reads it with request.args.get('q'), no backend form validation or CSRF needed.
    
    #extract the search query (?q=indoor) from the URL, or set to empty if none provided
    query = request.args.get('q', '').strip()

    #base query that orders events by ascending date (earliest first)
    base_query = Event.query.order_by(Event.date.asc())

    #If a search term exists, perform a case-insensitive search across fields that could be used
    if query:
        search = f"%{query}%" #adds wildcard matching for flexible partial matches
        events = base_query.filter(
            or_(
                Event.features.ilike(search), #match by feature (e.g., indoor etc)
                Event.title.ilike(search), #match by title like Tom's Pool
                Event.description.ilike(search), #match by description
                Event.location.ilike(search) #match by location
            )
        ).all()
        #debugging output for development, shows matched events in the terminal
        #had issues before
        print(f"[DEBUG] Searching for '{query}' → Found {len(events)} events")
        for e in events:
            print(f"Matched: {e.title} ({e.features})")
    else:
        #if no search term is provided, only show upcoming events (future dates)
        #yhis ensures users see events that haven’t occurred yet, ordered by nearest date
        events = base_query.filter(Event.date >= datetime.utcnow()).order_by(Event.date.asc()).all()
        
    #render the home.html template with the filtered or full list of events
    return render_template('home.html', events=events, search_term=query)








#NEW 03/10/25
#Allows a logged-in user to book tickets for an event,
#while enforcing important business rules:
# - Event creators cannot book their own events.
# - Bookings are only allowed if the event is open 
# - Prevents overselling by checking tickets left
# - Blocks booking if event is SOLD OUT
# - Saves a new Booking record linked to user + event.
#route to book events
@events_bp.route('/<int:event_id>/book', methods=['GET', 'POST'])
@login_required

#Look up the event by ID, or show 404 if not found
def book_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = BookingForm()

    #prevent event creator from booking their own event
    if event.created_by == current_user.id:
        flash("You created this event, so you can't book tickets for it.", "warning")
        return redirect(url_for('events.view_event', event_id=event.id))

    #prevent booking if event is inactive/closed/cancelled
    #just not equal to open - this may cause an issue in the future! :0
    if event.status.lower() != "open":
        flash(f"This event is {event.status}, so bookings are not allowed.", "danger")
        return redirect(url_for('events.view_event', event_id=event.id))

    #always calculate tickets left before using it
    total_booked = sum(b.quantity for b in Booking.query.filter_by(event_id=event.id).all())
    #simples
    tickets_left = event.capacity - total_booked

    #prevent booking if sold out
    #less than or equal to 0
    if tickets_left <= 0:
        flash("This event is SOLD OUT. No more tickets available.", "danger")
        return redirect(url_for('events.view_event', event_id=event.id))
    
    #Handle form submission (POST request)
    #User does what they are told =
    if form.validate_on_submit():
        #quantity
        qty = form.quantity.data

        #Check against capacity again just in case
        #basically need to make sure we are not over-selling
        if qty > tickets_left:
            flash(f"Not enough tickets available. Only {tickets_left} left.", "danger")
            return redirect(url_for('events.view_event', event_id=event.id))

        #passed all checks: create booking
        #we then create a new booking record
        total_price = event.cost * qty if event.cost else 0.0
        new_booking = Booking(
            user_id=current_user.id, #link booking to current user
            event_id=event.id,       #link booking to this event
            quantity=qty,            #number of tickets booked
            price=total_price        #total price is quantity times cost
        )
        #add it to database
        db.session.add(new_booking)
        db.session.commit()

        #confirmation flash message
        flash(f"Booking successful! Order ID: {new_booking.id}", "success")

        #show confirmation page with updated tickets left
        #So we send the user to the success page essentially
        return render_template(
            "event_booked.html",             #The confirmation page template
            event=event,                     #pass the event details to show what was booked
            booking=new_booking,             #pass the booking object so we can display order ID, qty
            user=current_user,               #pass the logged-in user to personalise the confirmation
            tickets_left=tickets_left - qty  #update after booking
        )

    #If GET request (or form invalid), show booking form page
    return render_template('book_event.html', event=event, form=form)

#should make sure we email the user their booking details or something like that.

#NEW CODE 04/10/25
#Allows the event owner (and only the owner) to edit an existing event.
# The form is pre-filled with the current event details and updates are saved
# to the database once submitted
    
#OWNER-ONLY: Edit an existing event
@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):

    #We get the event by its ID or return a 404 error if not found
    event = Event.query.get_or_404(event_id)

    #Security check, we want to make sure only the event creator can edit their event
    if event.created_by != current_user.id:
        flash("You are not authorised to edit this event.", "danger")
        return redirect(url_for('events.view_event', event_id=event.id))

    #create the form instance for editing
    form = EventForm()

    #if this is a GET request (first time loading), pre-fill the form fields
    #with the event’s current data
    #this is gonna help the user see the existing values when editing
    if request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.location.data = event.location
        form.cost.data = event.cost
        form.capacity.data = event.capacity
        form.features.data = event.features
        form.status.data = event.status
        #Extract the date portion
        form.date.data = event.date.date() if event.date else None

    #when form is submitted and valid, update the event details
    if form.validate_on_submit():
        # Keep the old image unless a new one is uploaded
        filename = event.image_file
        if form.image.data:
            #secure the uploaded filename and save it to the uploads folder
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(current_app.root_path, 'static/uploads', filename)
            form.image.data.save(filepath)

        #We will now update event details from the form inputs
        event.title = form.title.data
        event.description = form.description.data
        event.location = form.location.data
        event.cost = form.cost.data
        event.capacity = form.capacity.data
        event.features = form.features.data
        event.status = form.status.data
        event.date = form.date.data
        event.image_file = filename

        #and now gotta save the new changes to the database
        db.session.commit()

        #flash a confirmation message and redirect to the event details page
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.view_event', event_id=event.id))

    #If not submitted or invalid, render the edit form page
    #editing=true helps the template display the correct heading and button text
    #render edit_event.html
    return render_template('edit_event.html', form=form, editing=True, event=event)

#NEW NEW CODE 04/10/25
#Show all bookings for the currently logged-in user

#Displays all bookings made by the currently logged-in user.
#Each booking includes event details, quantity, total cost, and booking date.
@events_bp.route('/my_bookings')
@login_required
def my_bookings():
    
    #query all bookings that belong to the current user
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.date.desc()).all()

    #render the template and pass bookings
    return render_template('my_bookings.html', bookings=bookings)
