
#bunch of imports
import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import logging
db = SQLAlchemy()

#=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/
#NOTE ON FLASK APP LOCATION AND ERROR HANDLERS:
#In Flask, you can technically define app = Flask(__name__) OUTSIDE the
#create_app() function (per the tutorial's recommendation) so that global decorators 
#like @app.errorhandler can directly access it. This is not required here, since our error
#handlers are able to be INSIDE the create_app() function and are therefore
#already bound to the same Flask instance that gets returned and run.
#
#Keeping everything—app creation, configuration, blueprints, and error
#handlers—inside create_app() is generally cleaner and more maintainable.
#It avoids circular imports, ensures all components share the same app context
#and I just prefer it alot more.
#=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/=/


def create_app():
    #So we create a new Flask web application instance.
    
    app = Flask(__name__)
    
    # - loads configuration values
    # - environment variables are used where possible so sensitive data like secret keys or database URIs aren’t hard-coded 
    # - Though this isn't a big issue for our assessment
    # - ff environment variables aren’t found default values are used instead
    #Tbh this all pre much came preconfigured with the starter code
    
    #In short this line makes the app start in debug mode unless we explicitly tell it not to by 
    #setting the FLASK_DEBUG environment variable to something other than 1
    app.debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    #This setup pretty much lets us run it without some complex setup rn
    app.secret_key = os.environ.get('SECRET_KEY', 'somesecretkey')  #replace in prod
    #below sets the uri that tells the application where to find its database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///sitedata.sqlite')
    
    #Initialise extensions
    db.init_app(app)
    Bootstrap5(app)

    #flask-login helps manage user sessions (login/logout) and restricts
    #access to certain routes using @login_required <- helps with literally everything
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' #redirects
    login_manager.init_app(app)

    #Import models inside factory to avoid circular imports during import time
    from .models import User


    #tells flask-login how to load a user from the database by ID.
    # - flask stores the user_id in the session cookie
    # - on each request, it calls this function to retrieve the user object
    @login_manager.user_loader
    def load_user(user_id):
        try:
            uid = int(user_id) #ensures id is integer
        except (TypeError, ValueError):
            return None
        return db.session.scalar(db.select(User).where(User.id == uid))

    #Register blueprints /-/-/-/
    #each blueprint contains a group of related routes (views, auth, events)
    #registering them here attaches their routes to the main app
    from . import views
    app.register_blueprint(views.main_bp)

    from . import auth
    app.register_blueprint(auth.auth_bp)

    from . import events
    app.register_blueprint(events.events_bp)

    #Template context processor to inject current user info <--------------------
    #This function automatically injects variables into all templates rendered
    #by the app (so then we don’t have to manually pass like user details each time)
    #
    #flask runs this before rendering any template. if a user is logged in
    #it returns a dictionary containing their name and email allowing templates
    #to show personalised content such as the home screen with “Welcome back, <name>!”
    #
    #if no user is logged in, its gonna return none for both fields, so templates
    #can fall back to a default text
    #
    #Example:
    # {{ name }} and {{ email }} will automatically be available in any HTML
    # template, no need to pass them through render_template().
    #This is probs redundant cause we have definitely passed them through like every template lol.
    @app.context_processor
    def inject_user():
        if current_user.is_authenticated:
            return dict(name=current_user.name, email=current_user.email)
        return dict(name=None, email=None)
    
    #ERROR HANDLERS AND LOGGING SETUP
    #flask allows us to define custom error handlers to display user-friendly
    #pages instead of raw error messages. Here, both handlers are registered INSIDE the create_app() 
    #factory so that they attach to the same app instance being created and returned
    #
    # - 404 Handler: Gets triggered when user navigates to a page that doesn't 
    #                exists and returns page not found rendered through error.html
    #   
    # - Exception Handler: Catches any unhandled server errors (500 most likely)
    #                      and logs the exception details to the app’s logger. 
    #                      The user only sees a generic message.
    #
    
    #registers a function to handle 404 errors
    #basically tells flask whenever a 404 error happens anywhere in the app
    #call the function (not_found_404)to handle it.
    @app.errorhandler(404)
    #e is the error object flask passes in -> might contain like 404 not found or something
    #NOTE: We can remove e as we are not even using it??? Like we are not even using it to render the template.
    def not_found_404(e):
        #this gonna return a friendly 404 page when a route is not found for the user
        return render_template("error.html", message="Page not found"), 404

    #We are using e here tho for the logging stuff
    @app.errorhandler(Exception)
    def internal_error(e):
        #logs the full stack trace for debugging (not visible to the user)
        #and useful for us debugging all the errors!
        app.logger.error("Unhandled exception", exc_info=e)
        #this gonna show the most generic message to ever exist 
        return render_template("error.html", message="An unexpected error occurred"), 500

    #This is all logging, just to help see if there are any big messes
    #flask’s app.logger is just a standard Python logging object. 
    #.handlers are the output destinations
    if not app.logger.handlers:
        #creates a new handler that outputs logs to the console (stdout)
        handler = logging.StreamHandler()
        #sets the minimum level of logs to display. 
        #INFO means we will see important runtime messages 
        #and not just rubbish noise.
        handler.setLevel(logging.INFO)
        #attaches that handler to the Flask app’s logger so flask can 
        #print or record logs properly
        app.logger.addHandler(handler)

    return app


