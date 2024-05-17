# from flask import Blueprint, render_template, request, redirect, url_for, flash
# from .models import db, Event, User, Registration
# from sqlalchemy.exc import SQLAlchemyError, IntegrityError
# from sqlalchemy.orm.exc import FlushError
# from flask_login import login_required, current_user
# from flask import jsonify  # Import jsonify for returning JSON responses

# @dashboard_bp.route('/events/<int:event_id>/tickets', methods=['GET', 'POST'])
# @login_required
# def manage_tickets(event_id):
#     event = Event.query.get_or_404(event_id)
#     if request.method == 'POST':
#         try:
#             name = request.form.get('name')
#             description = request.form.get('description')
#             price = float(request.form.get('price'))
#             seating_arrangement = request.form.get('seating_arrangement')
#             ticket_type = TicketType(
#                 event_id=event.id,
#                 name=name,
#                 description=description,
#                 price=price,
#                 seating_arrangement=seating_arrangement
#             )
#             db.session.add(ticket_type)
#             db.session.commit()
#             flash('Ticket type created successfully!', 'success')
#             return redirect(url_for('dashboard.manage_tickets', event_id=event.id))
#         except SQLAlchemyError as e:
#             db.session.rollback()
#             flash('An error occurred while creating the ticket type. Please try again later.', 'error')
#             return redirect(url_for('dashboard.manage_tickets', event_id=event.id))
#     ticket_types = TicketType.query.filter_by(event_id=event.id).all()
#     return render_template('manage_tickets.html', event=event, ticket_types=ticket_types)

# @dashboard_bp.route('/events/<int:event_id>/tickets/<int:ticket_type_id>/delete', methods=['POST'])
# @login_required
# def delete_ticket_type(event_id, ticket_type_id):
#     ticket_type = TicketType.query.get_or_404(ticket_type_id)
#     try:
#         db.session.delete(ticket_type)
#         db.session.commit()
#         flash('Ticket type deleted successfully!', 'success')
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         flash('An error occurred while deleting the ticket type. Please try again later.', 'error')
#     return redirect(url_for('dashboard.manage_tickets', event_id=event_id))
