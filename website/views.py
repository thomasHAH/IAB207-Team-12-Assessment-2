from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Instead of returning plain text, render the home.html page
    return render_template('home.html')
    