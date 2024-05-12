# # events.py

# from flask import Blueprint, render_template, request, redirect, url_for, flash
# from .models import db, Event, User, Registration
# from sqlalchemy.exc import SQLAlchemyError
# from flask_login import login_required, current_user
# # from .dashboard import dashboard_bp

# # Create a blueprint for dashboard routes
# dashboard_bp = Blueprint('dashboard', __name__)

# # Define routes for the dashboard
# @dashboard_bp.route('/dashboard')
# @login_required
# def dashboard():
#     # Render the dashboard template
#     return render_template('dashboard.html')

# # Add routes for managing and promoting events
# @dashboard_bp.route('/events/create', methods=['GET', 'POST'])
# @login_required
# def create_event():
#     if request.method == 'POST':
#         try:
#             # Retrieve event details from the form
#             title = request.form.get('title')
#             description = request.form.get('description')
#             date = request.form.get('date')
#             time = request.form.get('time')
#             venue = request.form.get('venue')
#             # Create the event object
#             event = Event(title=title, description=description, date=date, time=time, venue=venue)
#             # Add event to the database
#             db.session.add(event)
#             db.session.commit()
#             flash('Event created successfully!', 'success')
#             # Redirect to the event details page
#             return redirect(url_for('dashboard.event_details', event_id=event.id))
#         except SQLAlchemyError as e:
#             db.session.rollback()
#             flash('An error occurred while creating the event. Please try again later.', 'error')
#             return redirect(url_for('dashboard.create_event'))
#     return render_template('create_event.html')

# @dashboard_bp.route('/events/<int:event_id>')
# @login_required
# def event_details(event_id):
#     event = Event.query.get_or_404(event_id)
#     return render_template('event_details.html', event=event)

# @dashboard_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
# @login_required
# def edit_event(event_id):
#     event = Event.query.get_or_404(event_id)
#     if request.method == 'POST':
#         try:
#             # Update event details from the form
#             event.title = request.form.get('title')
#             event.description = request.form.get('description')
#             event.date = request.form.get('date')
#             event.time = request.form.get('time')
#             event.venue = request.form.get('venue')
#             # Commit changes to the database
#             db.session.commit()
#             flash('Event updated successfully!', 'success')
#             # Redirect to the event details page
#             return redirect(url_for('dashboard.event_details', event_id=event.id))
#         except SQLAlchemyError as e:
#             db.session.rollback()
#             flash('An error occurred while updating the event. Please try again later.', 'error')
#             return redirect(url_for('dashboard.edit_event', event_id=event.id))
#     return render_template('edit_event.html', event=event)

# @dashboard_bp.route('/events/<int:event_id>/delete', methods=['POST'])
# @login_required
# def delete_event(event_id):
#     event = Event.query.get_or_404(event_id)
#     db.session.delete(event)
#     db.session.commit()
#     # Redirect to the events listing page
#     return redirect(url_for('dashboard.list_events'))

# @dashboard_bp.route('/events')
# @login_required
# def list_events():
#     events = Event.query.all()
#     return render_template('list_events.html', events=events)

# @dashboard_bp.route('/events/register/<int:event_id>', methods=['GET', 'POST'])
# @login_required
# def register_for_event(event_id):
#     event = Event.query.get_or_404(event_id)
#     if request.method == 'POST':
#         try:
#             # Check if the user already has a registration for the event
#             existing_registration = Registration.query.filter_by(event_id=event.id, user_id=current_user.id).first()
#             if existing_registration:
#                 flash('You have already registered for this event!', 'warning')
#                 return redirect(url_for('dashboard.event_details', event_id=event.id))
#             # Create a new registration for the user
#             registration = Registration(user_id=current_user.id, event_id=event.id)
#             db.session.add(registration)
#             db.session.commit()
#             flash('You have successfully registered for the event!', 'success')
#             return redirect(url_for('dashboard.event_details', event_id=event.id))
#         except SQLAlchemyError as e:
#             db.session.rollback()
#             flash('An error occurred while registering for the event. Please try again later.', 'error')
#             return redirect(url_for('dashboard.event_details', event_id=event.id))
#     return render_template('register_event.html', event=event)