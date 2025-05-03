from app import create_app, db
from app.models import UserRole, StakeholderRole, Permission

def init_roles():
    app = create_app()
    with app.app_context():
        # Create default permissions if they don't exist
        all_permissions = [
            {'name': 'View RFIs', 'code': 'view_rfis', 'type': 'user'},
            {'name': 'Create RFIs', 'code': 'create_rfis', 'type': 'user'},
            {'name': 'Edit RFIs', 'code': 'edit_rfis', 'type': 'user'},
            {'name': 'Delete RFIs', 'code': 'delete_rfis', 'type': 'user'},
            {'name': 'Accept/Reject RFIs', 'code': 'manage_rfis', 'type': 'user'},
            {'name': 'Manage Users', 'code': 'manage_users', 'type': 'user'},
            {'name': 'Manage Roles', 'code': 'manage_roles', 'type': 'user'},
            {'name': 'Manage Permissions', 'code': 'manage_permissions', 'type': 'user'},
            {'name': 'Manage System', 'code': 'manage_system', 'type': 'user'}
        ]
        
        for perm_data in all_permissions:
            if not Permission.query.filter_by(code=perm_data['code']).first():
                permission = Permission(
                    name=perm_data['name'],
                    code=perm_data['code'],
                    description=f"Allows {perm_data['name'].lower()}"
                )
                db.session.add(permission)
        
        db.session.commit()

        # Create default user roles if they don't exist
        user_roles = [
            {
                'name': 'Engineer',
                'description': 'Engineering staff with technical responsibilities',
                'color': 'primary',
                'permissions': ['view_rfis', 'create_rfis', 'edit_rfis', 'manage_rfis']
            },
            {
                'name': 'Inspector',
                'description': 'Field inspection staff',
                'color': 'success',
                'permissions': ['view_rfis', 'create_rfis', 'edit_rfis']
            },
            {
                'name': 'Manager',
                'description': 'Project management staff',
                'color': 'warning',
                'permissions': ['view_rfis', 'create_rfis', 'edit_rfis', 'manage_users', 'manage_roles']
            },
            {
                'name': 'Admin',
                'description': 'System administrator with full access',
                'color': 'danger',
                'permissions': ['view_rfis', 'create_rfis', 'edit_rfis', 'delete_rfis', 'manage_users', 'manage_roles', 'manage_permissions', 'manage_system']
            }
        ]

        # Create user roles with permissions
        for role_data in user_roles:
            role = UserRole.query.filter_by(name=role_data['name']).first()
            if not role:
                role = UserRole(
                    name=role_data['name'],
                    description=role_data['description'],
                    color=role_data['color']
                )
                db.session.add(role)
                db.session.commit()

            # Update permissions
            role.permissions = []
            for perm_code in role_data['permissions']:
                permission = Permission.query.filter_by(code=perm_code).first()
                if permission:
                    role.permissions.append(permission)
            
            db.session.commit()

        # Create default stakeholder roles if they don't exist
        stakeholder_roles = [
            {
                'name': 'Employer',
                'description': 'Project owner or client',
                'permissions': ['view_rfis']
            },
            {
                'name': 'Engineer',
                'description': 'Engineering consultant',
                'permissions': ['view_rfis', 'create_rfis', 'edit_rfis']
            },
            {
                'name': 'Contractor',
                'description': 'Main contractor',
                'permissions': ['view_rfis', 'create_rfis']
            },
            {
                'name': 'Subcontractor',
                'description': 'Specialized contractor',
                'permissions': ['view_rfis']
            }
        ]

        # Create stakeholder roles with permissions
        for role_data in stakeholder_roles:
            role = StakeholderRole.query.filter_by(name=role_data['name']).first()
            if not role:
                role = StakeholderRole(
                    name=role_data['name'],
                    description=role_data['description']
                )
                db.session.add(role)
                db.session.commit()

            # Update permissions
            role.permissions = []
            for perm_code in role_data['permissions']:
                permission = Permission.query.filter_by(code=perm_code).first()
                if permission:
                    role.permissions.append(permission)
            
            db.session.commit()

        db.session.commit()
        print("Default roles and permissions initialized successfully!")

if __name__ == '__main__':
    init_roles() 