from flask import Blueprint, request, jsonify, render_template
import stripe
import os
from .models import Order
from . import db
import logging
from .email_utils import send_email

payment_app = Blueprint('payment', __name__, url_prefix='/payment')

# Initialize Stripe with secret key
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Set up logging
logging.basicConfig(filename='payment.log', level=logging.INFO)

@payment_app.route('/form')
def payment_form():
    stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    return render_template('payment_form.html', stripe_publishable_key=stripe_publishable_key)


def handle_successful_payment_intent(payment_intent):
    order_id = payment_intent.metadata.get('order_id')
    order = Order.query.get(order_id)
    if order:
        try:
            order.status = 'Paid'
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to update order status to 'Paid' for order {order_id}: {str(e)}")
        else:
            subject = "Order Confirmation"
            template = f"Thank you for your order {order.id}. Your payment has been received."
            send_email(order.user.email, subject, template)
            logging.info(f"Order {order_id} status updated to 'Paid' and confirmation email sent")
    else:
        logging.error(f"Order with ID {order_id} not found")

def handle_failed_payment_intent(payment_intent):
    logging.error(f"Payment intent failed: {payment_intent.id}")

event_handlers = {
    'payment_intent.succeeded': handle_successful_payment_intent,
    'payment_intent.payment_failed': handle_failed_payment_intent,
}

@payment_app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_ENDPOINT_SECRET')
        )
    except ValueError as e:
        logging.error(f"Invalid payload: {str(e)}")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        logging.error(f"Invalid signature: {str(e)}")
        return 'Invalid signature', 400

    event_type = event['type']
    handler = event_handlers.get(event_type)

    if handler:
        handler(event['data']['object'])
    else:
        logging.warning(f"No handler found for event type: {event_type}")

    return '', 200

@payment_app.route('/charge', methods=['POST'])
def charge():
    try:
        amount = int(request.form['amount'])
        currency = request.form['currency']
        description = request.form['description']
        token = request.form['stripeToken']
        order_id = int(request.form['order_id'])

        charge = stripe.Charge.create(
            amount=amount,
            currency=currency,
            description=description,
            source=token,
            metadata={'order_id': order_id}
        )

        return jsonify({'success': True, 'charge_id': charge.id})
    except stripe.error.CardError as e:
        logging.error(f"Card error occurred: {str(e)}")
        return jsonify({'success': False, 'error': "Card error"}), 400
    except stripe.error.RateLimitError as e:
        logging.error(f"Rate limit error: {str(e)}")
        return jsonify({'success': False, 'error': "Rate limit error"}), 429
    except stripe.error.InvalidRequestError as e:
        logging.error(f"Invalid request: {str(e)}")
        return jsonify({'success': False, 'error': "Invalid request"}), 400
    except stripe.error.AuthenticationError as e:
        logging.error(f"Authentication error: {str(e)}")
        return jsonify({'success': False, 'error': "Authentication error"}), 401
    except stripe.error.APIConnectionError as e:
        logging.error(f"API connection error: {str(e)}")
        return jsonify({'success': False, 'error': "API connection error"}), 502
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {str(e)}")
        return jsonify({'success': False, 'error': "Stripe error"}), 500
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return jsonify({'success': False, 'error': "Internal server error"}), 500
