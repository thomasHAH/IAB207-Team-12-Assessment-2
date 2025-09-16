#commented

from flask import Blueprint, render_template, session
from .models import Event # Import the event model, that way pass through to the index

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Regardless of the logged in status, pass the events through to the index
    events = Event.query.order_by(Event.date.asc()).limit(5).all() # This will get the newest five events

    # Check if an email is stored in session (set in auth.py after login)
    if 'email' in session:
        #Pass the email into the template so it can display a welcome message
        return render_template('home.html', email=session['email'], name=session['name'], events=events)
    else:
        #No one logged in yet
        return render_template('home.html', events=events)
    
