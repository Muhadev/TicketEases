from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# Initialize SQLAlchemy database instance
db = SQLAlchemy()

# Initialize Flask-Login login manager
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random secret key

    # Configure MySQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:muhammed@localhost/EaseTicket'

    # Suppress deprecation warning
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database with Flask application
    db.init_app(app)
    login_manager.init_app(app)

    from .auth import auth_bp  # Import the authentication blueprint
    from .dashboard import dashboard_bp  # Import the dashboard blueprint


    # Register the authentication blueprint
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(dashboard_bp)  # Register the dashboard blueprint

    # Import models here to avoid circular imports
    from .models import User, Event, Ticket, Order, Payment

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    return app
 