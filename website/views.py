#commented

from flask import Blueprint, render_template, session

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Check if an email is stored in session (set in auth.py after login)
    if 'email' in session:
        #Pass the email into the template so it can display a welcome message
        return render_template('home.html', email=session['email'])
    else:
        #No one logged in yet
        return render_template('home.html')
