from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize SQLAlchemy database instance
db = SQLAlchemy()

# Initialize Flask-Login login manager
login_manager = LoginManager()

# Initialize Flask-Migrate
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a random secret key

    # Configure MySQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://muhadev:muhammed@localhost/eventsdbs'

    # Suppress deprecation warning
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database with Flask application
    db.init_app(app)
    login_manager.init_app(app)

    # Initialize Flask-Migrate with the Flask application and database
    migrate.init_app(app, db)

    from .auth import auth_bp  # Import the authentication blueprint
    from .dashboard import dashboard_bp  # Import the dashboard blueprint
    from .routes import home_bp


    # Register the authentication blueprint
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')  # Register the dashboard blueprint
    # Register the home page Blueprint
    app.register_blueprint(home_bp)


    # Import models here to avoid circular imports
    from .models import User, Event, Ticket, Order, Payment

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'


    return app
 