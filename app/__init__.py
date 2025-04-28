from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'verysecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rfi.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    from .auth import auth
    app.register_blueprint(auth)

    from .admin import admin
    app.register_blueprint(admin)

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User  # importu fonksiyon içine aldık
    return User.query.get(int(user_id))