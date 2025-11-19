"""
Payment Processing Routes
Stripe integration for HeySalad platform
"""

from flask import Blueprint, jsonify, request
import os
import stripe

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


@payment_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """
    Create a Stripe payment intent
    
    Request body:
    {
        "amount": 1000,  # Amount in cents
        "currency": "usd",
        "customer_email": "customer@example.com",
        "metadata": {}
    }
    """
    try:
        data = request.json
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        
        if not amount:
            return jsonify({'error': 'Amount is required'}), 400
        
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            receipt_email=data.get('customer_email'),
            metadata=data.get('metadata', {}),
            automatic_payment_methods={'enabled': True}
        )
        
        return jsonify({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        })
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/create-subscription', methods=['POST'])
def create_subscription():
    """
    Create a Stripe subscription
    
    Request body:
    {
        "customer_id": "cus_xxx",
        "price_id": "price_xxx",
        "trial_days": 14
    }
    """
    try:
        data = request.json
        customer_id = data.get('customer_id')
        price_id = data.get('price_id')
        
        if not customer_id or not price_id:
            return jsonify({'error': 'customer_id and price_id are required'}), 400
        
        subscription_params = {
            'customer': customer_id,
            'items': [{'price': price_id}]
        }
        
        if data.get('trial_days'):
            subscription_params['trial_period_days'] = data['trial_days']
        
        subscription = stripe.Subscription.create(**subscription_params)
        
        return jsonify({
            'subscription_id': subscription.id,
            'status': subscription.status,
            'current_period_end': subscription.current_period_end
        })
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle different event types
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Handle successful payment
        print(f"Payment succeeded: {payment_intent['id']}")
        
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # Handle failed payment
        print(f"Payment failed: {payment_intent['id']}")
        
    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        # Handle new subscription
        print(f"Subscription created: {subscription['id']}")
        
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        # Handle cancelled subscription
        print(f"Subscription cancelled: {subscription['id']}")
    
    return jsonify({'status': 'success'})


@payment_bp.route('/config', methods=['GET'])
def get_config():
    """Get Stripe public configuration"""
    return jsonify({
        'publishable_key': os.getenv('STRIPE_PUBLIC_KEY')
    })
