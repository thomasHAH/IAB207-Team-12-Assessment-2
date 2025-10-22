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

from .models import Event, Comment, Booking
from .forms import EventForm, CommentForm, BookingForm, CancelForm

events_bp = Blueprint('events', __name__)

@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            # consider prepending a UUID or timestamp to avoid collisions
            filepath = os.path.join(current_app.root_path, 'static/uploads', filename)
            form.image.data.save(filepath)

        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            status='Open',
            cost=form.cost.data,
            capacity=form.capacity.data,
            features=form.features.data,
            date=datetime.combine(form.date.data, datetime.min.time()) if form.date.data else None,
            created_by=current_user.id,
            image_file=filename
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.list_events'))
    else:
        print(form.errors)
    return render_template('create_event.html', form=form)


@events_bp.route('/list')
def list_events():
    # Only show events whose date is today or in the future
    events = (
        Event.query
        .filter(Event.date >= datetime.now())  # exclude past events
        .order_by(Event.date.asc())            # sort upcoming events by soonest first
        .all()
    )
    return render_template('list_events.html', events=events)

@events_bp.route('/<int:event_id>', methods=['GET', 'POST'])
def view_event(event_id):
    event = Event.query.get_or_404(event_id)

    comment_form = CommentForm()
    booking_form = BookingForm()
    cancel_form = CancelForm()

    # Handle Cancel Event submission
    if cancel_form.validate_on_submit() and cancel_form.cancel_button.data:
        event.status = "Cancelled"
        if hasattr(Event, 'is_cancelled') or hasattr(event, 'is_cancelled'):
            try:
                event.is_cancelled = True
            except Exception:
                current_app.logger.debug("Could not set event.is_cancelled; continuing with status only.")
        db.session.commit()
        return redirect(url_for('events.view_event', event_id=event.id))

    total_booked = db.session.scalar(
        db.select(func.coalesce(func.sum(Booking.quantity), 0)).where(Booking.event_id == event.id)
    ) or 0
    tickets_left = event.capacity - total_booked

    now = datetime.utcnow()

    if hasattr(event, 'is_cancelled'):
        is_cancelled_flag = bool(getattr(event, 'is_cancelled', False))
    else:
        is_cancelled_flag = str(getattr(event, 'status', '')).lower() == 'cancelled'

    if is_cancelled_flag:
        event.status = "Cancelled"
    elif event.date and event.date < now:
        event.status = "Closed"
    elif tickets_left <= 0:
        event.status = "Sold Out"
    else:
        event.status = "Open"

    db.session.commit()

    if comment_form.validate_on_submit() and comment_form.submit.data:
        if current_user.is_authenticated:
            new_comment = Comment(
                text=comment_form.text.data,
                user_id=current_user.id,
                event_id=event.id
            )
            db.session.add(new_comment)
            db.session.commit()
            flash("Your comment has been posted!", "success")
            return redirect(url_for('events.view_event', event_id=event.id))
        else:
            flash("You must be logged in to comment.", "danger")
            return redirect(url_for('auth.login'))

    comments = Comment.query.filter_by(event_id=event.id).order_by(Comment.date_created.desc()).all()

    return render_template(
        'view_event.html',
        event=event,
        comment_form=comment_form,
        booking_form=booking_form,
        cancel_form=cancel_form,
        comments=comments,
        tickets_left=tickets_left
    )

@events_bp.route('/home')
def home():
    query = request.args.get('q', '').strip()
    base_query = Event.query.order_by(Event.date.asc())

    if query:
        search = f"%{query}%"
        events = base_query.filter(
            or_(
                Event.features.ilike(search),
                Event.title.ilike(search),
                Event.description.ilike(search),
                Event.location.ilike(search)
            )
        ).all()
        print(f"[DEBUG] Searching for '{query}' → Found {len(events)} events")
        for e in events:
            print(f"Matched: {e.title} ({e.features})")
    else:
        # Show upcoming events; relies on Event.date being a datetime
        events = base_query.filter(Event.date >= datetime.utcnow()).order_by(Event.date.asc()).all()

    return render_template('home.html', events=events, search_term=query)

@events_bp.route('/<int:event_id>/book', methods=['GET', 'POST'])
@login_required
def book_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = BookingForm()

    if event.created_by == current_user.id:
        flash("You created this event, so you can't book tickets for it.", "warning")
        return redirect(url_for('events.view_event', event_id=event.id))

    if event.status.lower() != "open":
        flash(f"This event is currently {event.status} and cannot be booked.", "danger")
        return redirect(url_for('events.view_event', event_id=event.id))

    total_booked = db.session.scalar(
        db.select(func.coalesce(func.sum(Booking.quantity), 0)).where(Booking.event_id == event.id)
    ) or 0
    tickets_left = event.capacity - total_booked

    if tickets_left <= 0:
        flash("This event is SOLD OUT. No more tickets available.", "danger")
        return redirect(url_for('events.view_event', event_id=event.id))

    if form.validate_on_submit():
        qty = form.quantity.data
        if qty > tickets_left:
            flash(f"Not enough tickets available. Only {tickets_left} left.", "danger")
            return redirect(url_for('events.view_event', event_id=event.id))

        total_price = event.cost * qty if event.cost else 0.0
        new_booking = Booking(
            user_id=current_user.id,
            event_id=event.id,
            quantity=qty,
            price=total_price
        )
        db.session.add(new_booking)
        db.session.commit()

        flash(f"Booking successful! Order ID: {new_booking.id}", "success")


        return render_template(
            "event_booked.html",
            event=event,
            booking=new_booking,
            user=current_user,
            tickets_left=tickets_left - qty
        )

    return render_template('book_event.html', event=event, form=form)

@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.created_by != current_user.id:
        flash("You are not authorised to edit this event.", "danger")
        return redirect(url_for('events.view_event', event_id=event.id))

    form = EventForm()
    cancel_form = CancelForm()  

    if request.method == 'GET':
        form.title.data = event.title
        form.description.data = event.description
        form.location.data = event.location
        form.cost.data = event.cost
        form.capacity.data = event.capacity
        form.features.data = event.features
        form.date.data = event.date.date() if event.date else None

    if form.validate_on_submit():
        filename = event.image_file
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            filepath = os.path.join(current_app.root_path, 'static/uploads', filename)
            form.image.data.save(filepath)

        event.title = form.title.data
        event.description = form.description.data
        event.location = form.location.data
        event.cost = form.cost.data
        event.capacity = form.capacity.data
        event.features = form.features.data
        event.date = datetime.combine(form.date.data, datetime.min.time()) if form.date.data else None
        event.image_file = filename

        db.session.commit()

        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.view_event', event_id=event.id))

    return render_template('edit_event.html', form=form, cancel_form=cancel_form, editing=True, event=event)

@events_bp.route('/my_bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.date.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)

@events_bp.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')

@events_bp.route('/contact')
def contact():
    return render_template('contact.html')

@events_bp.route('/TnC')
def TnC():
    return render_template('TnC.html')