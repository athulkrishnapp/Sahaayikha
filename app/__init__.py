from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login settings
    login_manager.login_view = 'main.user_login'  # must match your route name
    login_manager.login_message_category = 'info'

    # Import and register blueprint
    from app.routes import main
    app.register_blueprint(main)

    # Create database tables if not exist (development use)
    with app.app_context():
        db.create_all()

    return app
