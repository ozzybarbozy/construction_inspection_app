from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rfi.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Add MIME type configuration
    app.config['MIME_TYPES'] = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif'
    }

    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from . import auth
    app.register_blueprint(auth.auth)

    from . import admin
    app.register_blueprint(admin.admin)

    from . import routes
    app.register_blueprint(routes.main)

    # Register CLI commands
    from .cli import import_data
    app.cli.add_command(import_data)

    return app