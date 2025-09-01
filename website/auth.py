
#Import necessary flask and library modules
from flask import Blueprint, flash, render_template, request, url_for, redirect, session
#Password hashing and verification (bcrypt = strong hashing algorithm)
from flask_bcrypt import generate_password_hash, check_password_hash
#Flask-login utilities to manage user session/login state
from flask_login import login_user, login_required, logout_user
#SQLAlchemy models (user table defined in models.py)
from .models import User
#The form classes that have been created in forms.py (loginform and register form)
from .forms import LoginForm, RegisterForm
#The database instance (SQLALchemy objectm defined in __init__.py)
from . import db

# Create a blueprint - make sure all BPs have unique names
#Blueprints let us split the app into logical components (auth, events, comments, etc)
#In this case auth is the bp name (used in url_for calls -> url_for('auth.login'))
#__name__ = tells Flask where this blueprint's code lives
auth_bp = Blueprint('auth', __name__)

#THIS WAS PROVIDED BY QUT------------------------------------------------------------------------------------------
# this is a hint for a login function
#this route supports both form display (GET) and form submission (POST)
@auth_bp.route('/login', methods=['GET', 'POST']) 
# view function
def login():
    #create an isntance of the loginform (from forms.py)
    login_form = LoginForm()
    
    #variable to hold any error messages
    error = None
    
    #if the form was submitted (POST) and it passes validation rules
    if login_form.validate_on_submit():
        
        #grab data entered into the form fields
        user_name = login_form.user_name.data
        password = login_form.password.data
        
        #query the database for a user with the given user name
        user = db.session.scalar(db.select(User).where(User.name==user_name))
        
        #check if user exists
        if user is None:
            error = 'Incorrect user name'
            
        #If user exists, check password hash against plain text password entered
        elif not check_password_hash(user.password, password): # takes the hash and cleartext password
            error = 'Incorrect password'
            
        #If no errors, log the user in
        if error is None:
            login_user(user) #Flask-login is going to set a session cookie so the user stays logged in
            login_user(user)  
            session['email'] = user.email  # store email in session
            #WILL NEED TO TEST IF THIS IS WORKING LATER
            #This is complicated
            #Check if the user was trying to access a protected page before login
            nextp = request.args.get('next') # this gives the url from where the login page was accessed
            print(nextp) #For debugging
            #If no redirect target or it's unsafe, send user to homepage
            if not nextp or not nextp.startswith('/'):
                return redirect(url_for('main.index')) #go to the homepage
            return redirect(nextp) #otherwise go to the page they originally wanted
        else:
             #Flash shows a small message in the UI 
            flash(error)
    #If GET request or login failed, show the login form again
    return render_template('login.html', form=login_form, heading='Login')
#---------------------------------------------------------------------------------------------------------------------


#NEW CODE ----------------------------------------------------------------------------------------------------------
@auth_bp.route('/register', methods=['GET', 'POST']) #supports form display + submission

def register():
    #Create an instance of the registerform
    register_form = RegisterForm()
    if register_form.validate_on_submit():  #if form was submitted and validated (so passed all the rules)
        # check if user already exists
        #Check if the email already exists in the database
        existing_user = User.query.filter_by(email=register_form.email.data).first()
        if existing_user:
            #flash small message to be shown in the template
            flash('Email already registered. Please log in instead.', 'danger')
            
            #redirect user to the login page instead of creating duplicate account
            return redirect(url_for('auth.login'))

        #create new user object
        #hash the password securely using bcrypt
        #decode converts hash btyes to string
        hashed_password = generate_password_hash(register_form.password.data).decode('utf-8')
        #create new user object from form data
        new_user = User(
            name=register_form.user_name.data,
            email=register_form.email.data,
            password=hashed_password #store the hashed password, NOT plaintext!
        )

        #Add the new user to the database
        db.session.add(new_user)
        db.session.commit() #commit writes the new row into sitedata.sqlite

        flash('Account created successfully! You can now log in.', 'success')
        #redirect to login page
        return redirect(url_for('auth.login'))

    #If GET request or validation failed, show the registration form again
    return render_template('register.html', form=register_form, heading='Register')



# ------------------------ LOGOUT ------------------------
@auth_bp.route('/logout')
@login_required  # only allow logged-in users to log out
def logout():
    # remove email from session so navbar updates
    session.pop('email', None)

    # log user out (Flask-Login)
    logout_user()

    flash("You have been logged out.", "info")
    return redirect(url_for('main.index'))

#------------------------------------------------------------------------------------------------------------------------