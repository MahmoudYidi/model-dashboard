from flask import Flask
from flask_login import LoginManager
from config import Config
from utils.auth import configure_auth

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
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