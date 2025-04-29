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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Add MIME type configuration
    app.config['MIME_TYPES'] = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif'
    }

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

    # Create database tables
    with app.app_context():
        if not os.path.exists('instance/database.db'):
            db.create_all()
            # Create initial roles and permissions
            from .models import Role, Permission
            
            # Create permissions
            permissions = [
                Permission(name='View RFIs', description='Can view RFIs', code='view_rfis'),
                Permission(name='Create RFIs', description='Can create new RFIs', code='create_rfis'),
                Permission(name='Edit RFIs', description='Can edit existing RFIs', code='edit_rfis'),
                Permission(name='Delete RFIs', description='Can delete RFIs', code='delete_rfis'),
                Permission(name='Manage Users', description='Can manage system users', code='manage_users'),
                Permission(name='Manage Roles', description='Can manage user roles', code='manage_roles'),
                Permission(name='Manage ITPs', description='Can manage ITPs', code='manage_itps'),
                Permission(name='Manage Stakeholders', description='Can manage stakeholders', code='manage_stakeholders')
            ]
            for permission in permissions:
                db.session.add(permission)
            db.session.commit()

            # Create roles
            admin_role = Role(name='Admin', description='Full system access', color='danger')
            manager_role = Role(name='Manager', description='Can manage RFIs and ITPs', color='warning')
            inspector_role = Role(name='Inspector', description='Can create and edit RFIs', color='info')
            viewer_role = Role(name='Viewer', description='Can only view RFIs', color='secondary')

            # Add roles to session first
            db.session.add(admin_role)
            db.session.add(manager_role)
            db.session.add(inspector_role)
            db.session.add(viewer_role)
            db.session.flush()

            # Add all permissions to admin role
            admin_role.permissions = Permission.query.all()

            # Add specific permissions to manager role
            manager_permissions = ['view_rfis', 'create_rfis', 'edit_rfis', 'delete_rfis', 'manage_itps']
            manager_role.permissions = Permission.query.filter(Permission.code.in_(manager_permissions)).all()

            # Add specific permissions to inspector role
            inspector_permissions = ['view_rfis', 'create_rfis', 'edit_rfis']
            inspector_role.permissions = Permission.query.filter(Permission.code.in_(inspector_permissions)).all()

            # Add view permission to viewer role
            viewer_role.permissions = [Permission.query.filter_by(code='view_rfis').first()]

            db.session.commit()

            # Create default admin user
            admin_role = Role.query.filter_by(name='Admin').first()
            if admin_role:
                admin_user = User(
                    username='admin',
                    email='admin@example.com',
                    password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                    role_id=admin_role.id
                )
                db.session.add(admin_user)
                db.session.commit()

    return app