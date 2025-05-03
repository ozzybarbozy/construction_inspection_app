from app import create_app, db
from app.models import User, UserRole, RFI
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create default roles
        admin_role = UserRole(name='Admin', description='Administrator')
        contractor_role = UserRole(name='Contractor', description='Contractor')
        viewer_role = UserRole(name='Viewer', description='Viewer')
        
        db.session.add(admin_role)
        db.session.add(contractor_role)
        db.session.add(viewer_role)
        db.session.commit()  # Commit to get the role IDs
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            role_id=admin_role.id,
            password=generate_password_hash('admin123', method='pbkdf2:sha256')
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("Database initialized with default roles and admin user")

if __name__ == '__main__':
    init_db() 