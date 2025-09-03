from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Event
from .forms import EventForm

events_bp = Blueprint('events', __name__)

@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        new_event = Event(
            title=form.title.data,
            description=form.description.data,
            capacity=form.capacity.data,
            features=form.features.data,
            date=form.date.data,
            created_by=current_user.id
        )
        db.session.add(new_event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.list_events'))  # redirect to event list after creation
    return render_template('create_event.html', form=form)

@events_bp.route('/list')
def list_events():
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template('list_events.html', events=events)
