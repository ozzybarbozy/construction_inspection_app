from . import db
from datetime import datetime
from flask_login import UserMixin

# Association table for role-permission many-to-many relationship
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    color = db.Column(db.String(20), default='primary')  # For UI styling
    permissions = db.relationship('Permission', secondary=role_permissions, backref='roles')
    users = db.relationship('User', backref='role_obj', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    code = db.Column(db.String(50), unique=True, nullable=False)  # For programmatic checks

    def __repr__(self):
        return f'<Permission {self.name}>'

class RFI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rfi_number = db.Column(db.String(50), unique=True, nullable=False)  # New column for RFI number
    title = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    submitted_by = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    last_action_date = db.Column(db.DateTime, default=datetime.utcnow)  # Track last action date
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Closed, Accepted, Rejected, Cancelled
    priority = db.Column(db.String(20), default='Normal')  # Low, Normal, High, Urgent
    itp_id = db.Column(db.Integer, db.ForeignKey('itp.id'), nullable=True)
    itp_phase_id = db.Column(db.Integer, db.ForeignKey('itp_phase.id'), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    building_code = db.Column(db.String(50), nullable=False)
    discipline_code = db.Column(db.String(10), nullable=False)
    drawing_number = db.Column(db.String(50), nullable=False)
    inspection_date = db.Column(db.Date, nullable=True)
    inspection_time = db.Column(db.Time, nullable=True)
    
    # Relationships
    itp = db.relationship('ITP', backref='rfis')
    itp_phase = db.relationship('ITPPhase', backref='rfis')
    assigned_to = db.relationship('User', backref='assigned_rfis')

    @staticmethod
    def generate_rfi_number(discipline_code, building_code):
        # Get the last RFI number for this discipline and building combination
        last_rfi = RFI.query.filter(
            RFI.discipline_code == discipline_code,
            RFI.building_code == building_code
        ).order_by(RFI.id.desc()).first()
        
        # Extract the sequential number from the last RFI or start from 0001
        if last_rfi and last_rfi.rfi_number:
            last_number = int(last_rfi.rfi_number.split('-')[-1])
            next_number = last_number + 1
        else:
            next_number = 1
            
        # Format the number with leading zeros
        sequential_number = f"{next_number:04d}"
        
        # Generate the full RFI number
        return f"KLN-SPP2-RFI-{discipline_code}-{building_code}-{sequential_number}"

    def is_closed(self):
        return self.status in ['Closed', 'Accepted', 'Rejected', 'Cancelled']

    def can_be_accepted_rejected_by(self, user):
        # Admin can accept/reject any RFI
        if (user.role_obj and user.role_obj.name == 'Admin') or \
           (user.stakeholder and user.stakeholder.role == 'Admin'):
            return not self.is_closed()
        
        # Engineers can only accept/reject RFIs assigned to them
        return ((user.role_obj and user.role_obj.name == 'Engineer') or 
                (user.stakeholder and user.stakeholder.role == 'Engineer')) and \
                self.assigned_to_id == user.id and \
                not self.is_closed()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    plaintext_password = db.Column(db.String(100), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    stakeholder_id = db.Column(db.Integer, db.ForeignKey('stakeholder.id'), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    surname = db.Column(db.String(100), nullable=True)
    cell_phone = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.String(255), nullable=True)  # Path to the photo file

    def has_permission(self, permission_code):
        if not self.role_obj:
            return False
        return any(permission.code == permission_code for permission in self.role_obj.permissions)

class Stakeholder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    logo = db.Column(db.String(255), nullable=True)  # Path to the logo file
    users = db.relationship('User', backref='stakeholder', lazy=True)

class ITP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itp_number = db.Column(db.String(50), nullable=False)  # ITP numarası
    description = db.Column(db.String(255), nullable=False)  # ITP açıklaması
    revision_number = db.Column(db.String(50), nullable=False)  # Revizyon numarası
    revision_date = db.Column(db.Date, nullable=False)  # Revizyon tarihi
    discipline_code = db.Column(db.String(10), db.ForeignKey('discipline_code.code'), nullable=False)  # New field for discipline code
    phases = db.relationship('ITPPhase', backref='itp', lazy=True, cascade="all, delete-orphan")
    
    # Relationship
    discipline = db.relationship('DisciplineCode', backref='itps')
    
    def __repr__(self):
        return f"<ITP {self.itp_number}>"

class ITPPhase(db.Model):
    __tablename__ = "itp_phase"
    id = db.Column(db.Integer, primary_key=True)
    phase_code = db.Column(db.String(50), nullable=True)
    activity_name = db.Column(db.String(255), nullable=False)
    verifying_document = db.Column(db.String(255), nullable=True)
    employer = db.Column(db.String(2), nullable=True)
    engineer = db.Column(db.String(2), nullable=True)
    contractor = db.Column(db.String(2), nullable=True)
    subcontractor = db.Column(db.String(2), nullable=True)
    third_party = db.Column(db.String(2), nullable=True)
    itp_id = db.Column(db.Integer, db.ForeignKey('itp.id'), nullable=False)

class Drawing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drawing_number = db.Column(db.String(50), unique=True, nullable=False)
    building_code = db.Column(db.String(10), db.ForeignKey('building.code'), nullable=False)
    discipline_code = db.Column(db.String(10), nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    revision_number = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    building = db.relationship('Building', backref='drawings')

    def __repr__(self):
        return f'<Drawing {self.drawing_number}>'

class Building(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Building {self.code}>'

class DisciplineCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DisciplineCode {self.code}>'

class RFISettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_limitations_enabled = db.Column(db.Boolean, default=False)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(50), nullable=False)