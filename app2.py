from flask import Flask, jsonify, request
from flask_login import LoginManager
from config import Config
from utils.auth import configure_auth
from threading import Lock


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Global metrics storage with thread lock
    app.metrics_lock = Lock()
    app.metrics = {
        'scanned': {'value': '1,248', 'change': '+12%', 'trend': 'up'},
        'anomaly_rate': {'value': '3.2%', 'change': '-0.5%', 'trend': 'down'},
        'top_anomaly': {'value': 'Split', 'count': '28', 'trend': 'steady'},
        'yield_forecast': {'value': '96.5%', 'change': '+1.2%', 'trend': 'up'},
        'recent_anomaly': {'value': 'Crack', 'count': '9', 'trend': 'up'},
        'camera_health': {'value': '92%', 'status': 'good'}
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
    
    # Add API endpoint for metrics updates
    @app.route('/api/update_metrics', methods=['POST'])
    def update_metrics():
        try:
            data = request.json
            with app.metrics_lock:
                for key in data:
                    if key in app.metrics:
                        app.metrics[key].update(data[key])
            return jsonify({"status": "success"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400
    
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
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)