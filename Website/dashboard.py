from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import db, Event, TicketType, Ticket, Order, Payment
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_required, current_user
import logging
from .forms import EventForm
from .token_utils import generate_confirmation_token  # Add this import statement

# Configure logging
logging.basicConfig(filename='dashboard.log', level=logging.INFO)
logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    if not current_user.confirmed:
        token = generate_confirmation_token(current_user.email)  # Generate confirmation token
        return redirect(url_for("auth.confirm_email", token=token))  # Pass the token as a parameter
    return render_template('dashboard.html')


@dashboard_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()  # Instantiate your EventForm

    if form.validate_on_submit():  # Server-side validation using Flask-WTF
        title = form.title.data
        description = form.description.data
        date = form.date.data
        time = form.time.data
        venue = form.venue.data

        try:
            # Redirect to the payment page with event details
            amount = 1000  # Amount in cents (set your own logic to determine amount)
            currency = 'usd'
            return redirect(url_for('payment.charge', amount=amount, currency=currency, description=description, event_name=title, event_date=date, venue=venue))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error preparing event creation: {str(e)}')
            flash('An error occurred while preparing the event creation. Please try again later.', 'error')

    return render_template('create_event.html', form=form)


@dashboard_bp.route('/events/<int:event_id>/details')
@login_required
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_details.html', event=event)

@dashboard_bp.route('/success')
@login_required
def success():
    return render_template('success.html')

@dashboard_bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)  # Pass the event object to prepopulate the form
    
    if form.validate_on_submit():
        form.populate_obj(event)  # Update the event object with form data
        try:
            db.session.commit()
            logger.info(f'Event updated: {event.title}')
            flash('Event updated successfully!', 'success')
            return redirect(url_for('dashboard.success'))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating event: {str(e)}')
            flash('An error occurred while updating the event. Please try again later.', 'error')

    return render_template('edit_event.html', event=event, form=form)

@dashboard_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event)
        db.session.commit()
        logger.info(f'Event deleted: {event.title}')
        flash('Event deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f'Error deleting event: {str(e)}')
        flash('An error occurred while deleting the event. Please try again later.', 'error')
    return redirect(url_for('dashboard.list_events'))

@dashboard_bp.route('/events/list')
@login_required
def list_events():
    events = Event.query.all()
    return render_template('list_events.html', events=events)

@dashboard_bp.route('/events/book/form', methods=['GET'])
@login_required
def book_ticket_form():
    events = Event.query.all()
    ticket_types = TicketType.query.all()
    return render_template('book_tickets.html', events=events, ticket_types=ticket_types)

@dashboard_bp.route('/events/book', methods=['POST'])
@login_required
def book_tickets():
    event_id = request.form.get('event')
    ticket_type_id = request.form.get('ticket_type')
    quantity = int(request.form.get('quantity'))

    try:
        ticket_type = TicketType.query.get(ticket_type_id)
        if ticket_type.available_tickets < quantity:
            return jsonify({'error': 'Not enough tickets available!'}), 400

        amount = quantity * ticket_type.price  # Total amount in cents
        currency = 'usd'
        description = f'Booking {quantity} tickets for {ticket_type.name}'

        # Redirect to the payment page with booking details
        return redirect(url_for('payment.charge', amount=amount, currency=currency, description=description, event_id=event_id, ticket_type_id=ticket_type_id, quantity=quantity))
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error preparing ticket booking: {str(e)}')
        return jsonify({'error': 'An error occurred while preparing ticket booking. Please try again later.'}), 500

@dashboard_bp.route('/booking/confirmation/<int:booking_id>')
@login_required
def booking_confirmation(booking_id):
    ticket = Ticket.query.get_or_404(booking_id)
    quantity = Ticket.query.filter_by(user_id=current_user.id, event_id=ticket.event_id).count()
    return render_template('booking_confirmation.html', ticket=ticket, quantity=quantity)

@dashboard_bp.route('/ticket_types/<int:event_id>')
@login_required
def list_ticket_types(event_id):
    ticket_types = TicketType.query.filter_by(event_id=event_id).all()
    return jsonify([{
        'id': ticket_type.id,
        'name': ticket_type.name,
        'description': ticket_type.description,
        'price': ticket_type.price,
        'available_tickets': ticket_type.available_tickets
    } for ticket_type in ticket_types])

@dashboard_bp.route('/events/<int:event_id>/tickets', methods=['GET', 'POST'])
@login_required
def manage_tickets(event_id):
    event = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        seating_arrangement = request.form.get('seating_arrangement')
        available_tickets = int(request.form.get('available_tickets'))

        if not name or not price or available_tickets < 0:
            flash('Name, Price, and available tickets are required.', 'error')
            return redirect(url_for('dashboard.manage_tickets', event_id=event.id))

        try:
            ticket_type = TicketType(
                event_id=event.id,
                name=name,
                description=description,
                price=price,
                seating_arrangement=seating_arrangement,
                available_tickets=available_tickets
            )
            db.session.add(ticket_type)
            db.session.commit()
            logger.info(f'Ticket type created for event {event.id}')
            flash('Ticket type created successfully!', 'success')
            return redirect(url_for('dashboard.success', event_id=event.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f'Error creating ticket type: {str(e)}')
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
        logger.info(f'Ticket type deleted: {ticket_type.name}')
        flash('Ticket type deleted successfully!', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f'Error deleting ticket type: {str(e)}')
        flash('An error occurred while deleting the ticket type. Please try again later.', 'error')
    return redirect(url_for('dashboard.manage_tickets', event_id=event_id))
