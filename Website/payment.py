from flask import Blueprint, request, jsonify
import stripe
import os
from .models import Ticket, TicketType, Order
from . import db, mail
import logging
from .email_utils import send_email

payment_app = Blueprint('payment', __name__, url_prefix='/payment')

# Set up logging
logging.basicConfig(filename='payment.log', level=logging.INFO)

def handle_successful_payment_intent(payment_intent):
    order_id = payment_intent.metadata.get('order_id')
    order = Order.query.get(order_id)
    if order:
        try:
            with db.session.begin_nested():
                order.status = 'Paid'
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update order status to 'Paid' for order {order_id}: {str(e)}")
            # Send notification to administrators
            # Notify administrators via email, SMS, or Slack
        else:
            # Send order confirmation email to the user
            subject = "Order Confirmation"
            template = f"Thank you for your order {order.id}. Your payment has been received."
            send_email(order.user.email, subject, template)
            logging.info(f"Order {order_id} status updated to 'Paid' and confirmation email sent")
    else:
        logging.error(f"Order with ID {order_id} not found")

def handle_failed_payment_intent(payment_intent):
    logging.error(f"Payment intent failed: {payment_intent.id}")
    # Send notification to administrators
    # Notify administrators via email, SMS, or Slack

def handle_refunded_charge(charge):
    logging.info(f"Charge refunded: {charge.id}")

def handle_dispute_created(dispute):
    logging.info(f"Dispute created: {dispute.id}")

def handle_new_subscription(subscription):
    logging.info(f"New subscription created: {subscription.id}")

def handle_subscription_updated(subscription):
    logging.info(f"Subscription updated: {subscription.id}")

def handle_subscription_canceled(subscription):
    logging.info(f"Subscription canceled: {subscription.id}")

def handle_new_invoice(invoice):
    logging.info(f"New invoice created: {invoice.id}")

def handle_successful_invoice_payment(invoice):
    logging.info(f"Invoice payment succeeded: {invoice.id}")

def handle_failed_invoice_payment(invoice):
    logging.error(f"Invoice payment failed: {invoice.id}")
    # Send notification to administrators
    # Notify administrators via email, SMS, or Slack

# Route for processing payments
@payment_app.route('/charge', methods=['POST'])
def charge():
    try:
        # Get payment information from request and validate
        amount = int(request.form['amount'])
        currency = request.form['currency']
        description = request.form['description']
        token = request.form['stripeToken']
        order_id = int(request.form['order_id'])

        # Create charge using Stripe API
        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            description=description,
            source=token,
        )

        # Return success response
        return jsonify({'success': True, 'charge_id': charge.id})
    except stripe.error.StripeError as e:
        # Handle Stripe errors
        error_message = str(e)
        logging.error(f"Stripe error occurred during payment processing: {error_message}")
        return jsonify({'success': False, 'error': error_message}), 400
    except Exception as e:
        # Handle other errors
        error_message = str(e)
        logging.error(f"An unexpected error occurred during payment processing: {error_message}")
        return jsonify({'success': False, 'error': error_message}), 500

# Define a dictionary to map event types to handler functions
event_handlers = {
    'payment_intent.succeeded': handle_successful_payment_intent,
    'payment_intent.payment_failed': handle_failed_payment_intent,
    'charge.refunded': handle_refunded_charge,
    'charge.dispute.created': handle_dispute_created,
    'customer.subscription.created': handle_new_subscription,
    'customer.subscription.updated': handle_subscription_updated,
    'customer.subscription.deleted': handle_subscription_canceled,
    'invoice.created': handle_new_invoice,
    'invoice.payment_succeeded': handle_successful_invoice_payment,
    'invoice.payment_failed': handle_failed_invoice_payment
}

# Route for handling webhook events
@payment_app.route('/webhook', methods=['POST'])    
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_ENDPOINT_SECRET')
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Get event type
    event_type = event['type']

    # Get handler function for the event type
    handler = event_handlers.get(event_type)

    if handler:
        # Call the handler function with the event data
        handler(event['data']['object'])
    else:
        # No handler found for the event type
        logging.warning(f"No handler found for event type: {event_type}")

    return '', 200
