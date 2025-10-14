#commented

# import flask - from 'package' import 'Class'
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import current_user


db = SQLAlchemy()

# This has been moved outside the create app function allowing the error handling to access it
app = Flask(__name__)  # this is the name of the module/package that is calling this app


# create a function that creates a web application
# a web server will run this web application
def create_app():
    # Should be set to false in a production environment
    app.debug = True
    app.secret_key = 'somesecretkey'
    # set the app configuration data 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'
    # initialise db with flask app
    db.init_app(app)

    Bootstrap5(app)
    
    # initialise the login manager
    login_manager = LoginManager()
    
    # set the name of the login function that lets user login
    # in our case it is auth.login (blueprintname.viewfunction name)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # create a user loader function takes userid and returns User
    # Importing inside the create_app function avoids circular references
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
      #This function tells Flask-Login how to find a user in the database.
      #When someone is logged in, Flask-Login stores their user ID in a cookie.
      #On the next page load, Flask-Login uses this function:
      # - Takes the ID from the cookie
      # - Looks up the User in the database
      # - Returns the User so we can use current_user
      return db.session.scalar(db.select(User).where(User.id==user_id))

    #Register here means attaching a blueprint to the flask app
    from . import views
    app.register_blueprint(views.main_bp)

    from . import auth
    app.register_blueprint(auth.auth_bp)
    
    #Importing the whole events.py module from the current package
    #This will load everything define inside events.py including the blueprint
    #and route functions
    from . import events
    #Registering the events blueprints with the flask app
    #this attaches all routes defined under events_bp like /create, /list to tha main app
    app.register_blueprint(events.events_bp)
    
    
    #Fix issue of personalising the home screen
    @app.context_processor
    def inject_user():
      if current_user.is_authenticated:
          return dict(name=current_user.name, email=current_user.email)
      return dict(name=None, email=None)
    return app


# This will handle rendering the error.html page
#This will only occur when any error happens by switching the 404 to the Exceptino
@app.errorhandler(Exception) 
# inbuilt function which takes error as parameter 
def not_found(e): 
  return render_template("error.html")