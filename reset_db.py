import os
from app import create_app, db
from app.models import UserRole, Permission, User
from werkzeug.security import generate_password_hash

def reset_database():
    app = create_app()
    with app.app_context():
        # Remove existing database
        if os.path.exists('instance/rfi.db'):
            os.remove('instance/rfi.db')
        
        # Create new database
        db.create_all()
        
        # Create default roles and permissions
        admin_role = UserRole(name='Admin', description='Administrator with full access')
        contractor_role = UserRole(name='Contractor', description='Contractor role')
        viewer_role = UserRole(name='Viewer', description='Read-only access')
        
        db.session.add_all([admin_role, contractor_role, viewer_role])
        db.session.commit()
        
        # Create default admin user
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            user_role_id=admin_role.id
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("Database reset and initialized successfully!")

if __name__ == '__main__':
    reset_database() 