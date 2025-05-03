from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Optional
from datetime import datetime, timedelta

class RFIForm(FlaskForm):
    remarks = TextAreaField('Remarks', validators=[Optional()])
    priority = SelectField('Priority', choices=[
        ('', '-- Select Priority --'),
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent')
    ], validators=[DataRequired()])
    itp = SelectField('ITP', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    itp_phase = SelectField('ITP Phase', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    assigned_to = SelectField('Assigned To', coerce=lambda x: int(x) if x else None, validators=[DataRequired()])
    building_code = SelectField('Building Code', validators=[DataRequired()])
    discipline_code = SelectField('Discipline Code', validators=[DataRequired()])
    drawing_number = SelectField('Drawing Number', validators=[DataRequired()])
    inspection_date = DateField('Inspection Date', format='%Y-%m-%d', validators=[DataRequired()], default=lambda: datetime.now().date() + timedelta(days=1))
    inspection_time = SelectField('Inspection Time', choices=[
        ('', '-- Select Time --'),
        *[(f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}') 
          for hour in range(9, 18) 
          for minute in [0, 30]]
    ], validators=[DataRequired()]) 