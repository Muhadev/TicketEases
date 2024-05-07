# dashboard.py

from flask import Blueprint, render_template

# Create a blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

# Define routes for the dashboard
@dashboard_bp.route('/dashboard')
def dashboard():
    # Render the dashboard template
    return render_template('dashboard.html')