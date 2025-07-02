from flask import Flask, jsonify, request, current_app
from flask_login import LoginManager
from config import Config
from utils.auth import configure_auth
from threading import Lock
from functools import wraps
import secrets

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Your existing API key from Config
    if not app.config.get('API_SECRET_KEY'):
        raise RuntimeError("API_SECRET_KEY not configured in Config")
    
    # Thread-safe metrics storage
    app.metrics_lock = Lock()
    app.metrics = {
        'scanned': {'value': '0', 'change': '0%', 'trend': 'steady'},
        'anomaly_rate': {'value': '0%', 'change': '0%', 'trend': 'steady'},
        'top_anomaly': {'value': 'None', 'count': '0', 'trend': 'steady'},
        'yield_forecast': {'value': '0%', 'change': '0%', 'trend': 'steady'},
        'recent_anomaly': {'value': 'None', 'count': '0', 'trend': 'steady'},
        'camera_health': {'value': '0%', 'status': 'offline'}
    }

    # Initialize extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    configure_auth(login_manager)
    
    # Register blueprints
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.model import model_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(model_bp)
    
    # API security decorator
    def require_api_key(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            expected = f"Bearer {current_app.config['API_SECRET_KEY']}"
            if not auth_header or not secrets.compare_digest(auth_header, expected):
                return jsonify({"status": "unauthorized"}), 401
            return f(*args, **kwargs)
        return decorated
    
    # Metrics API endpoint
    @app.route('/api/v1/metrics', methods=['POST', 'OPTIONS'])
    @require_api_key
    def handle_metrics():
        if request.method == 'OPTIONS':
            return _build_cors_preflight()
            
        if not request.is_json:
            return jsonify({"error": "JSON content required"}), 415
            
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Empty payload"}), 400
                
            with current_app.metrics_lock:
                for metric, values in data.items():
                    if metric in current_app.metrics:
                        if isinstance(values, dict):
                            current_app.metrics[metric].update(values)
                        else:
                            current_app.metrics[metric] = values
                            
            return jsonify({
                "status": "success",
                "updated": list(data.keys())
            }), 200
            
        except Exception as e:
            current_app.logger.error(f"Metrics update failed: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    # CORS handlers
    def _build_cors_preflight():
        response = jsonify({"status": "preflight"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Authorization, Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response
    
    # Initialize Dash apps
    with app.app_context():
        from dash_apps.analytics import init_analytics_app
        from dash_apps.insights import init_insights_app
        from dash_apps.botanist_gpt import init_botanist_app
        from dash_apps.model import init_model_app
        
        init_analytics_app(app)
        init_insights_app(app)
        init_botanist_app(app)
        init_model_app(app)
    
    # Add CORS to all responses
    @app.after_request
    def add_cors_headers(response):
        if request.path.startswith('/api/'):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)