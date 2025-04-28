from . import db
from datetime import datetime
from flask_login import UserMixin

class RFI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    submitted_by = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    plaintext_password = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(50), nullable=False, default='viewer')
    stakeholder_id = db.Column(db.Integer, db.ForeignKey('stakeholder.id'), nullable=True)

class Stakeholder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    users = db.relationship('User', backref='stakeholder', lazy=True)


class ITP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itp_number = db.Column(db.String(50), nullable=False)  # ITP numarası
    activity_name = db.Column(db.String(255), nullable=False)  # Aktivite adı
    revision_number = db.Column(db.String(50), nullable=False)  # Revizyon numarası
    revision_date = db.Column(db.Date, nullable=False)  # Revizyon tarihi
    phases = db.relationship('ITPPhase', backref='itp', lazy=True, cascade="all, delete-orphan")
    
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