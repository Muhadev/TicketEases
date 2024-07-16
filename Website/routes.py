from flask import Blueprint, render_template

# Create a Blueprint for home page routes
home_bp = Blueprint('home', __name__)

# Define the home page route
@home_bp.route('/')
def home():
    return render_template('home.html')