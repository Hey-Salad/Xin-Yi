"""
HeySalad Platform Backend
Extensible Flask application with modular routes

This is the main backend for all HeySalad services:
- Xin Yi (WMS/Food Inventory)
- AI Chat & Image Generation
- Payment Processing (Stripe)
- Communication (Email/SMS)
- Future services...
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure CORS for multiple origins
CORS(app, 
     origins=[
         "https://xinyi.heysalad.app",
         "https://heysalad.app",
         "https://*.heysalad.app",
         "https://vscode.heysalad.app",
         "http://localhost:2125",
         "http://localhost:*",
         "http://127.0.0.1:*"
     ],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Import and register blueprints
from routes.wms_routes import wms_bp
from routes.ai_routes import ai_bp
from routes.payment_routes import payment_bp
from routes.communication_routes import comm_bp
from routes.document_routes import document_bp

app.register_blueprint(wms_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(comm_bp)
app.register_blueprint(document_bp)


# Add explicit OPTIONS handler for CORS preflight
@app.before_request
def handle_preflight():
    """Handle CORS preflight OPTIONS requests"""
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        # Allow cross-origin requests from xinyi.heysalad.app
        origin = request.headers.get('Origin')
        if origin:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response


@app.route('/', methods=['GET'])
def index():
    """Platform API root"""
    return jsonify({
        'name': 'HeySalad Platform API',
        'version': '1.0.0',
        'services': {
            'wms': {
                'name': 'Xin Yi - Warehouse Management',
                'prefix': '/api/wms',
                'description': 'Food inventory management with FEFO logic'
            },
            'documents': {
                'name': 'WMS Document Generation',
                'prefix': '/api/documents',
                'description': 'Generate warehouse documents (PO receipts, pick lists, reports, etc.)'
            },
            'ai': {
                'name': 'AI Services',
                'prefix': '/api/ai',
                'description': 'Multi-provider AI chat and image generation'
            },
            'payment': {
                'name': 'Payment Processing',
                'prefix': '/api/payment',
                'description': 'Stripe payment and subscription management'
            },
            'communication': {
                'name': 'Communication Services',
                'prefix': '/api/communication',
                'description': 'Email (SendGrid) and SMS (Twilio)'
            }
        },
        'endpoints': {
            'health': '/health',
            'status': '/status'
        }
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'environment': os.getenv('FLASK_ENV', 'production')
    })


@app.route('/status', methods=['GET'])
def status():
    """Service status check"""
    services = {
        'database': {
            'supabase': bool(os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'))
        },
        'ai_providers': {
            'openai': bool(os.getenv('OPENAI_API_KEY')),
            'anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
            'gemini': bool(os.getenv('GEMINI_API_KEY')),
            'deepseek': bool(os.getenv('DEEPSEEK_API_KEY')),
            'huggingface': bool(os.getenv('HUGGINGFACE_API_KEY')),
            'cloudflare': bool(os.getenv('CLOUDFLARE_API_KEY'))
        },
        'payment': {
            'stripe': bool(os.getenv('STRIPE_SECRET_KEY'))
        },
        'communication': {
            'sendgrid': bool(os.getenv('SENDGRID_API_KEY')),
            'twilio': bool(os.getenv('TWILIO_ACCOUNT_SID'))
        }
    }
    
    return jsonify({
        'status': 'operational',
        'services': services
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Please check the API documentation at /'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong. Please try again later.'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('BACKEND_PORT', 2124))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("=" * 60)
    print("🚀 HeySalad Platform Backend Starting...")
    print("=" * 60)
    print(f"📍 Port: {port}")
    print(f"🔧 Debug: {debug}")
    print(f"🌍 Environment: {os.getenv('FLASK_ENV', 'production')}")
    print("=" * 60)
    print("\n📦 Available Services:")
    print("  • WMS (Xin Yi): /api/wms/*")
    print("  • Documents: /api/documents/*")
    print("  • AI Services: /api/ai/*")
    print("  • Payments: /api/payment/*")
    print("  • Communication: /api/communication/*")
    print("\n🔗 Endpoints:")
    print(f"  • API Root: http://localhost:{port}/")
    print(f"  • Health: http://localhost:{port}/health")
    print(f"  • Status: http://localhost:{port}/status")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
