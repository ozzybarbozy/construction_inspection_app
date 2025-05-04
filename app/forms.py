from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from datetime import datetime, timedelta

class RFIForm(FlaskForm):
    remarks = TextAreaField('Remarks', validators=[
        Optional(),
        Length(max=1000, message='Remarks cannot exceed 1000 characters')
    ])
    
    priority = SelectField('Priority', choices=[
        ('', '-- Select Priority --'),
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent')
    ], validators=[
        DataRequired(message='Please select a priority level')
    ])
    
    itp = SelectField('ITP', coerce=lambda x: int(x) if x else None, validators=[
        DataRequired(message='Please select an ITP')
    ])
    
    itp_phase = SelectField('ITP Phase', coerce=lambda x: int(x) if x else None, validators=[
        DataRequired(message='Please select an ITP phase')
    ])
    
    assigned_to = SelectField('Assigned To', coerce=lambda x: int(x) if x else None, validators=[
        DataRequired(message='Please select an assignee')
    ])
    
    building_code = SelectField('Building Code', validators=[
        DataRequired(message='Please select a building code')
    ])
    
    discipline_code = SelectField('Discipline Code', validators=[
        DataRequired(message='Please select a discipline code')
    ])
    
    drawing_number = SelectField('Drawing Number', validators=[
        DataRequired(message='Please select a drawing number')
    ])
    
    inspection_date = DateField('Inspection Date', format='%Y-%m-%d', validators=[
        DataRequired(message='Please select an inspection date')
    ], default=lambda: datetime.now().date() + timedelta(days=1))
    
    inspection_time = SelectField('Inspection Time', choices=[
        ('', '-- Select Time --'),
        *[(f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}') 
          for hour in range(9, 18) 
          for minute in [0, 30]]
    ], validators=[
        DataRequired(message='Please select an inspection time')
    ])
    
    def validate_inspection_date(self, field):
        if field.data < datetime.now().date():
            raise ValidationError('Inspection date cannot be in the past') 