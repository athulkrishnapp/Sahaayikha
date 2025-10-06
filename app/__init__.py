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

    # Create database tables and default settings
    with app.app_context():
        db.create_all()

        # --- ADDED THIS SECTION TO POPULATE DEFAULT SETTINGS ---
        from app.models import SystemSetting
        # Check if settings already exist
        if not SystemSetting.query.first():
            # Create default settings
            default_expiry = SystemSetting(key='ITEM_EXPIRY_DAYS', value='30')
            maintenance_mode = SystemSetting(key='MAINTENANCE_MODE', value='false')
            db.session.add(default_expiry)
            db.session.add(maintenance_mode)
            db.session.commit()

    return app