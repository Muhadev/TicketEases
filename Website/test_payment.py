import unittest
from unittest.mock import patch
from flask import Flask
from payment import payment_app, charge, webhook, event_handlers

class PaymentIntegrationTest(unittest.TestCase):

    def setUp(self):
        # Create a test Flask app and configure it for testing
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(payment_app)

        # Create a test client for making requests
        self.client = self.app.test_client()

    @patch('payment.stripe')
    def test_successful_payment_processing(self, mock_stripe):
        # Mock the Charge.create method to simulate successful payment processing
        mock_stripe.Charge.create.return_value.id = 'ch_123'
        
        # Simulate a request with valid payment information
        response = self.client.post('/payment/charge', json={
            'amount': 1000,
            'currency': 'usd',
            'description': 'Test Payment',
            'stripeToken': 'tok_123',
            'order_id': 123
        })
        
        # Assert that the response indicates success and contains a charge_id
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['charge_id'], 'ch_123')

    @patch('payment.stripe.Webhook.construct_event')
    def test_successful_webhook_handling(self, mock_construct_event):
        # Mock the Webhook.construct_event method to simulate a successful event handling
        mock_construct_event.return_value = {'type': 'payment_intent.succeeded', 'data': {'object': {}}}
        
        # Simulate a request with a valid webhook payload
        response = self.client.post('/payment/webhook', data='valid_payload', headers={'Stripe-Signature': 'signature'})
        
        # Assert that the response status code is 200 (success)
        self.assertEqual(response.status_code, 200)

    def test_event_handlers(self):
        # Simulate event data for different event types
        successful_payment_intent_event = {'type': 'payment_intent.succeeded', 'data': {'object': {}}}
        failed_payment_intent_event = {'type': 'payment_intent.payment_failed', 'data': {'object': {}}}
        
        # Test successful payment intent event handling
        self.assertIsNone(event_handlers['payment_intent.succeeded'](successful_payment_intent_event['data']['object']))
        
        # Test failed payment intent event handling
        self.assertIsNone(event_handlers['payment_intent.payment_failed'](failed_payment_intent_event['data']['object']))

if __name__ == '__main__':
    unittest.main()
