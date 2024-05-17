# dashboard.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Event, User, Registration, TicketType
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import FlushError
from flask_login import login_required, current_user
from flask import jsonify  # Import jsonify for returning JSON responses
import logging

# Configure logging
logging.basicConfig(filename='dashboard.log', level=logging.INFO)
# Initialize logger
logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@dashboard_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        try:
            # Retrieve event details from the form
            title = request.form.get('title')
            description = request.form.get('description')
            date = request.form.get('date')
            time = request.form.get('time')
            venue = request.form.get('venue')
            # Create the event object
            event = Event(title=title, description=description, date=date, time=time, venue=venue)
            # Add event to the database
            db.session.add(event)
            db.session.commit()
            flash('Event created successfully!', 'success')
            # Redirect to the event details page
            return jsonify({'event_id': event.id})
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while creating the event. Please try again later.', 'error')
            return redirect(url_for('dashboard.create_event'))
    return render_template('create_event.html')

@dashboard_bp.route('/events/<int:event_id>/details')
@login_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_details.html', event=event)

# Route for the success page
@dashboard_bp.route('/success')
@login_required
def success():
    return render_template('success.html')

@dashboard_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        try:
            # Update event details from the form
            event.title = request.form.get('title')
            event.description = request.form.get('description')
            event.date = request.form.get('date')
            event.time = request.form.get('time')
            event.venue = request.form.get('venue')
            # Commit changes to the database
            db.session.commit()
            # Redirect to the success page
            return redirect(url_for('dashboard.success'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while updating the event. Please try again later.', 'error')
            return redirect(url_for('dashboard.edit_event', event_id=event.id))
    return render_template('edit_event.html', event=event)

@dashboard_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
        logger.info(f"Event with ID {event_id} deleted successfully.")
    except (IntegrityError, FlushError) as e:
        db.session.rollback()
        flash('An error occurred while deleting the event. Please try again later.', 'error')
        logger.error(f"Error deleting event with ID {event_id}: {str(e)}")
    return redirect(url_for('dashboard.list_events'))

@dashboard_bp.route('/events/list')
@login_required
def list_events():
    events = Event.query.all()
    return render_template('list_events.html', events=events)

@dashboard_bp.route('/events/register/<int:event_id>', methods=['GET', 'POST'])
@login_required
def register_for_event(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        try:
            # Check if the user already has a registration for the event
            existing_registration = Registration.query.filter_by(event_id=event.id, user_id=current_user.id).first()
            if existing_registration:
                flash('You have already registered for this event!', 'warning')
                return redirect(url_for('dashboard.event_details', event_id=event.id))
            # Create a new registration for the user
            registration = Registration(user_id=current_user.id, event_id=event.id)
            db.session.add(registration)
            db.session.commit()
            flash('You have successfully registered for the event!', 'success')
            return redirect(url_for('dashboard.event_details', event_id=event.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while registering for the event. Please try again later.', 'error')
            return redirect(url_for('dashboard.event_details', event_id=event.id))
    return render_template('register_event.html', event=event)


@dashboard_bp.route('/events/<int:event_id>/tickets', methods=['GET', 'POST'])
@login_required
def manage_tickets(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            seating_arrangement = request.form.get('seating_arrangement')
            ticket_type = TicketType(
                event_id=event.id,
                name=name,
                description=description,
                price=price,
                seating_arrangement=seating_arrangement
            )
            db.session.add(ticket_type)
            db.session.commit()
            flash('Ticket type created successfully!', 'success')
            return redirect(url_for('dashboard.success', event_id=event.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while creating the ticket type. Please try again later.', 'error')
            return redirect(url_for('dashboard.manage_tickets', event_id=event.id))
    ticket_types = TicketType.query.filter_by(event_id=event.id).all()
    return render_template('manage_tickets.html', event=event, ticket_types=ticket_types)

@dashboard_bp.route('/events/<int:event_id>/tickets/<int:ticket_type_id>/delete', methods=['POST'])
@login_required
def delete_ticket_type(event_id, ticket_type_id):
    ticket_type = TicketType.query.get_or_404(ticket_type_id)
    try:
        db.session.delete(ticket_type)
        db.session.commit()
        flash('Ticket type deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while deleting the ticket type. Please try again later.', 'error')
    return redirect(url_for('dashboard.manage_tickets', event_id=event_id))
