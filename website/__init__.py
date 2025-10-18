import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import logging

db = SQLAlchemy()

def create_app():
    # Instantiate the app inside the factory (recommended)
    app = Flask(__name__)

    # Configuration (recommend moving to environment/config file for production)
    app.debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.secret_key = os.environ.get('SECRET_KEY', 'somesecretkey')  # replace in prod
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///sitedata.sqlite')
    # Optional: limit upload size
    app.config.setdefault('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16 MB

    # Initialize extensions
    db.init_app(app)
    Bootstrap5(app)

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Import models inside factory to avoid circular imports during import time
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # Flask-Login may pass user_id as a string; ensure proper type handling
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            return None
        return db.session.scalar(db.select(User).where(User.id == uid))

    # Register blueprints
    from . import views
    app.register_blueprint(views.main_bp)

    from . import auth
    app.register_blueprint(auth.auth_bp)

    from . import events
    app.register_blueprint(events.events_bp)

    # Template context processor to inject current user info
    @app.context_processor
    def inject_user():
        if current_user.is_authenticated:
            return dict(name=current_user.name, email=current_user.email)
        return dict(name=None, email=None)

    # Error handlers: keep them inside factory so they are registered on the app instance
    @app.errorhandler(404)
    def not_found_404(e):
        return render_template("error.html", message="Page not found"), 404

    @app.errorhandler(Exception)
    def internal_error(e):
        # Log the exception for diagnostics (do not expose internal details to users)
        app.logger.error("Unhandled exception", exc_info=e)
        return render_template("error.html", message="An unexpected error occurred"), 500

    # Optional: configure logging if not already configured
    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)

    return app