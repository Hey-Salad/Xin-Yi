"""
Communication Routes
Email (SendGrid) and SMS (Twilio) integration
"""

from flask import Blueprint, jsonify, request
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

comm_bp = Blueprint('communication', __name__, url_prefix='/api/communication')

# Initialize clients
sendgrid_client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)


@comm_bp.route('/email/send', methods=['POST'])
def send_email():
    """
    Send email via SendGrid
    
    Request body:
    {
        "to": "recipient@example.com",
        "subject": "Hello",
        "html_content": "<p>Email body</p>",
        "text_content": "Email body"
    }
    """
    try:
        data = request.json
        to_email = data.get('to')
        subject = data.get('subject')
        html_content = data.get('html_content')
        text_content = data.get('text_content', '')
        
        if not to_email or not subject:
            return jsonify({'error': 'to and subject are required'}), 400
        
        message = Mail(
            from_email=os.getenv('SENDGRID_FROM_EMAIL'),
            to_emails=to_email,
            subject=subject,
            html_content=html_content or text_content
        )
        
        if text_content and html_content:
            message.plain_text_content = text_content
        
        response = sendgrid_client.send(message)
        
        return jsonify({
            'status': 'sent',
            'status_code': response.status_code,
            'message_id': response.headers.get('X-Message-Id')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@comm_bp.route('/email/template', methods=['POST'])
def send_template_email():
    """
    Send templated email via SendGrid
    
    Request body:
    {
        "to": "recipient@example.com",
        "template_id": "d-xxx",
        "dynamic_data": {"name": "John", "order_id": "12345"}
    }
    """
    try:
        data = request.json
        to_email = data.get('to')
        template_id = data.get('template_id')
        dynamic_data = data.get('dynamic_data', {})
        
        if not to_email or not template_id:
            return jsonify({'error': 'to and template_id are required'}), 400
        
        message = Mail(
            from_email=os.getenv('SENDGRID_FROM_EMAIL'),
            to_emails=to_email
        )
        message.template_id = template_id
        message.dynamic_template_data = dynamic_data
        
        response = sendgrid_client.send(message)
        
        return jsonify({
            'status': 'sent',
            'status_code': response.status_code
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@comm_bp.route('/sms/send', methods=['POST'])
def send_sms():
    """
    Send SMS via Twilio
    
    Request body:
    {
        "to": "+1234567890",
        "body": "Your verification code is 123456"
    }
    """
    try:
        data = request.json
        to_number = data.get('to')
        body = data.get('body')
        
        if not to_number or not body:
            return jsonify({'error': 'to and body are required'}), 400
        
        message = twilio_client.messages.create(
            body=body,
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=to_number
        )
        
        return jsonify({
            'status': 'sent',
            'message_sid': message.sid,
            'to': message.to,
            'status': message.status
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@comm_bp.route('/voice/call', methods=['POST'])
def make_call():
    """
    Make voice call via Twilio
    
    Request body:
    {
        "to": "+1234567890",
        "twiml_url": "https://example.com/twiml"
    }
    """
    try:
        data = request.json
        to_number = data.get('to')
        twiml_url = data.get('twiml_url')
        
        if not to_number or not twiml_url:
            return jsonify({'error': 'to and twiml_url are required'}), 400
        
        call = twilio_client.calls.create(
            url=twiml_url,
            to=to_number,
            from_=os.getenv('TWILIO_PHONE_NUMBER')
        )
        
        return jsonify({
            'status': 'initiated',
            'call_sid': call.sid,
            'to': call.to,
            'status': call.status
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@comm_bp.route('/status', methods=['GET'])
def get_status():
    """Check communication services status"""
    return jsonify({
        'sendgrid': {
            'configured': bool(os.getenv('SENDGRID_API_KEY')),
            'from_email': os.getenv('SENDGRID_FROM_EMAIL')
        },
        'twilio': {
            'configured': bool(os.getenv('TWILIO_ACCOUNT_SID')),
            'phone_number': os.getenv('TWILIO_PHONE_NUMBER'),
            'sip_domain': os.getenv('TWILIO_SIP_DOMAIN')
        }
    })
