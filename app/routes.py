from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from .models import RFI, ITP, ITPPhase, User, Drawing, Building, DisciplineCode, RFISettings
from . import db
from datetime import datetime, timedelta
from .forms import RFIForm

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    # Check for RFIs that need to be cancelled
    today = datetime.now().date()
    rfis_to_cancel = RFI.query.filter(
        RFI.status == 'Open',
        RFI.inspection_date < today,
        RFI.assigned_to_id.isnot(None)
    ).all()
    
    for rfi in rfis_to_cancel:
        rfi.status = 'Cancelled'
        rfi.last_action_date = datetime.utcnow()
    
    if rfis_to_cancel:
        db.session.commit()
    
    rfis = RFI.query.order_by(RFI.date_created.desc()).all()
    return render_template('index.html', rfis=rfis)

@main.route('/rfi/add', methods=['GET', 'POST'])
@login_required
def add_rfi():
    form = RFIForm()
    
    # Get choices for form fields
    form.itp.choices = [('', '-- Select ITP --')] + [(itp.id, f"{itp.itp_number} - {itp.description}") for itp in ITP.query.all()]
    form.itp_phase.choices = [('', '-- Select Phase --')]
    form.assigned_to.choices = [('', '-- Not Assigned --')] + [(user.id, f"{user.name or 'No Name'} {user.surname or ''} ({user.username})") for user in User.query.all()]
    
    # Get building codes and discipline codes
    buildings = Building.query.join(Drawing).distinct().all()
    form.building_code.choices = [('', '-- Select Building Code --')] + [(building.code, f"{building.code} - {building.name}") for building in buildings]
    
    # Initialize empty choices for discipline and drawing
    form.discipline_code.choices = [('', '-- Select Discipline Code --')]
    form.drawing_number.choices = [('', '-- Select Drawing Number --')]
    
    # Get building-discipline-drawing mapping
    building_disciplines = {}
    building_discipline_drawings = {}
    
    for building in buildings:
        # Get disciplines for this building
        disciplines = db.session.query(Drawing.discipline_code).filter_by(building_code=building.code).distinct().all()
        building_disciplines[building.code] = []
        
        # Get full discipline information for each code
        for discipline_code in disciplines:
            discipline = DisciplineCode.query.filter_by(code=discipline_code[0]).first()
            if discipline:
                building_disciplines[building.code].append({
                    'code': discipline.code,
                    'name': discipline.name
                })
                # Add to form choices if not already present
                if (discipline.code, f"{discipline.code} - {discipline.name}") not in form.discipline_code.choices:
                    form.discipline_code.choices.append((discipline.code, f"{discipline.code} - {discipline.name}"))
        
        # Get drawings for each discipline in this building
        for discipline in building_disciplines[building.code]:
            drawings = Drawing.query.filter_by(
                building_code=building.code,
                discipline_code=discipline['code']
            ).all()
            
            if building.code not in building_discipline_drawings:
                building_discipline_drawings[building.code] = {}
            
            building_discipline_drawings[building.code][discipline['code']] = [
                {
                    'id': drawing.id,
                    'drawing_number': drawing.drawing_number,
                    'sequence_number': drawing.sequence_number,
                    'revision_number': drawing.revision_number
                }
                for drawing in drawings
            ]
            # Add to form choices if not already present
            for drawing in drawings:
                choice = (drawing.drawing_number, f"{drawing.drawing_number} (Rev. {drawing.revision_number})")
                if choice not in form.drawing_number.choices:
                    form.drawing_number.choices.append(choice)
    
    # Get phases for ITP selection
    phases = ITPPhase.query.all()
    phases_data = [
        {
            'id': phase.id,
            'phase_code': phase.phase_code,
            'activity_name': phase.activity_name,
            'itp_id': phase.itp_id
        }
        for phase in phases
    ]
    
    # Add all phases to form choices
    for phase in phases:
        choice = (phase.id, f"{phase.phase_code} - {phase.activity_name}")
        if choice not in form.itp_phase.choices:
            form.itp_phase.choices.append(choice)
    
    if form.validate_on_submit():
        try:
            # Check if user is an Admin or Contractor
            is_admin = current_user.user_role and current_user.user_role.name == 'Admin'
            is_contractor = current_user.stakeholder and current_user.stakeholder.role == 'Contractor'
            
            if not (is_admin or is_contractor):
                flash('Only Admins and Contractors can submit RFIs.', 'error')
                return redirect(url_for('main.index'))
            
            # Debug print form data
            print("Form data:", form.data)
            
            # Generate RFI number
            rfi_number = RFI.generate_rfi_number(
                form.discipline_code.data,
                form.building_code.data
            )
            
            # Convert inspection_time string to time object
            inspection_time = datetime.strptime(form.inspection_time.data, '%H:%M').time()
            
            # Create RFI object
            rfi = RFI(
                rfi_number=rfi_number,
                remarks=form.remarks.data,
                submitted_by=current_user.username,
                status='Open',
                priority=form.priority.data,
                itp_id=form.itp.data if form.itp.data else None,
                itp_phase_id=form.itp_phase.data if form.itp_phase.data else None,
                assigned_to_id=form.assigned_to.data if form.assigned_to.data else None,
                building_code=form.building_code.data,
                discipline_code=form.discipline_code.data,
                drawing_number=form.drawing_number.data,
                inspection_date=form.inspection_date.data,
                inspection_time=inspection_time
            )
            
            # Debug print RFI object
            print("RFI object:", rfi.__dict__)
            
            # Add to session and commit
            db.session.add(rfi)
            db.session.commit()
            
            flash('RFI has been created successfully.', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            print("Error creating RFI:", str(e))
            flash(f'Error creating RFI: {str(e)}', 'error')
            return redirect(url_for('main.add_rfi'))
    else:
        # Debug print form errors
        print("Form errors:", form.errors)
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return render_template('add_rfi.html', 
                         title='Add RFI', 
                         form=form,
                         buildings=buildings,
                         users=User.query.all(),
                         itps=ITP.query.all(),
                         phases=phases_data,
                         building_disciplines=building_disciplines,
                         building_discipline_drawings=building_discipline_drawings,
                         now=datetime.now(),
                         timedelta=timedelta)

@main.route('/delete/<int:id>')
@login_required
def delete_rfi(id):
    rfi = RFI.query.get_or_404(id)
    db.session.delete(rfi)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_rfi(id):
    rfi = RFI.query.get_or_404(id)
    
    if request.method == 'POST':
        # Check if time limitations are enabled
        settings = RFISettings.query.first()
        if settings and settings.time_limitations_enabled:
            now = datetime.now()
            current_time = now.time()
            if current_time < settings.start_time or current_time > settings.end_time:
                flash(f'RFIs can only be submitted between {settings.start_time.strftime("%H:%M")} and {settings.end_time.strftime("%H:%M")}.', 'error')
                return redirect(url_for('main.edit_rfi', id=id))

        rfi.remarks = request.form['remarks']
        rfi.submitted_by = request.form['submitted_by']
        rfi.priority = request.form['priority']
        rfi.itp_id = request.form.get('itp_id')
        rfi.itp_phase_id = request.form.get('itp_phase_id')
        rfi.assigned_to_id = request.form.get('assigned_to_id')
        rfi.building_code = request.form['building_code']
        rfi.discipline_code = request.form['discipline_code']
        rfi.drawing_number = request.form['drawing_number']
        rfi.inspection_date = datetime.strptime(request.form['inspection_date'], '%Y-%m-%d').date()
        rfi.inspection_time = datetime.strptime(request.form['inspection_time'], '%H:%M').time()

        db.session.commit()
        flash('RFI updated successfully!', 'success')
        return redirect(url_for('main.index'))

    # Get all ITPs and users for the form
    itps = ITP.query.all()
    users = User.query.all()
    phases = ITPPhase.query.all()
    
    # Get unique building codes from existing drawings
    buildings = Building.query.join(Drawing).distinct().all()
    
    # Get building-discipline-drawing mapping
    building_disciplines = {}
    building_discipline_drawings = {}
    
    for building in buildings:
        # Get disciplines for this building
        disciplines = db.session.query(Drawing.discipline_code).filter_by(building_code=building.code).distinct().all()
        building_disciplines[building.code] = []
        
        # Get full discipline information for each code
        for discipline_code in disciplines:
            discipline = DisciplineCode.query.filter_by(code=discipline_code[0]).first()
            if discipline:
                building_disciplines[building.code].append({
                    'code': discipline.code,
                    'name': discipline.name
                })
        
        # Get drawings for each discipline in this building
        for discipline in building_disciplines[building.code]:
            drawings = Drawing.query.filter_by(
                building_code=building.code,
                discipline_code=discipline['code']
            ).all()
            
            if building.code not in building_discipline_drawings:
                building_discipline_drawings[building.code] = {}
            
            building_discipline_drawings[building.code][discipline['code']] = [
                {
                    'id': drawing.id,
                    'drawing_number': drawing.drawing_number,
                    'sequence_number': drawing.sequence_number,
                    'revision_number': drawing.revision_number
                }
                for drawing in drawings
            ]
    
    # Convert phases to JSON-serializable format
    phases_data = [
        {
            'id': phase.id,
            'phase_code': phase.phase_code,
            'activity_name': phase.activity_name,
            'itp_id': phase.itp_id
        }
        for phase in phases
    ]
    
    return render_template('edit_rfi.html', 
                         rfi=rfi,
                         itps=itps, 
                         users=users,
                         phases=phases_data,
                         buildings=buildings,
                         building_disciplines=building_disciplines,
                         building_discipline_drawings=building_discipline_drawings)

# ITP Routes

@main.route('/add_itp', methods=['GET', 'POST'])
@login_required
def add_itp():
    if request.method == 'POST':
        itp_number = request.form['itp_number']
        activity_name = request.form['activity_name']
        revision_number = request.form['revision_number']
        revision_date = request.form['revision_date']

        new_itp = ITP(
            itp_number=itp_number,
            activity_name=activity_name,
            revision_number=revision_number,
            revision_date=revision_date
        )
        
        db.session.add(new_itp)
        db.session.commit()
        return redirect(url_for('main.list_itps'))

    return render_template('admin/add_itp.html')

@main.route('/list_itps')
@login_required
def list_itps():
    itps = ITP.query.all()
    return render_template('admin/list_itps.html', itps=itps)

@main.route('/delete_itp/<int:id>', methods=['GET'])
@login_required
def delete_itp(id):
    itp = ITP.query.get_or_404(id)
    db.session.delete(itp)
    db.session.commit()
    return redirect(url_for('main.list_itps'))

@main.route('/drawings', methods=['GET', 'POST'])
@login_required
def drawings():
    if request.method == 'POST':
        building_code = request.form.get('building_code')
        discipline_code = request.form.get('discipline_code')
        sequence_number = request.form.get('sequence_number')
        revision_number = request.form.get('revision_number')

        # Generate drawing number
        drawing_number = f"PRO-SPP2-DWG-{discipline_code}-{building_code}-{sequence_number}_{revision_number}"

        # Check if drawing number already exists
        existing_drawing = Drawing.query.filter_by(drawing_number=drawing_number).first()
        if existing_drawing:
            flash('Drawing number already exists!', 'danger')
            return redirect(url_for('main.drawings'))

        # Create new drawing
        drawing = Drawing(
            drawing_number=drawing_number,
            building_code=building_code,
            discipline_code=discipline_code,
            sequence_number=sequence_number,
            revision_number=revision_number
        )

        try:
            db.session.add(drawing)
            db.session.commit()
            flash('Drawing created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating drawing: {str(e)}', 'danger')

        return redirect(url_for('main.drawings'))

    # Get all drawings
    drawings = Drawing.query.all()
    buildings = Building.query.all()
    
    return render_template('drawings.html', 
                         drawings=drawings,
                         buildings=buildings,
                         discipline_codes=DisciplineCode.query.all())

@main.route('/rfi/<int:id>/accept', methods=['POST'])
@login_required
def accept_rfi(id):
    rfi = RFI.query.get_or_404(id)
    
    if not rfi.can_be_accepted_rejected_by(current_user):
        flash('You are not authorized to accept this RFI.', 'danger')
        return redirect(url_for('main.index'))
    
    rfi.status = 'Accepted'
    rfi.last_action_date = datetime.utcnow()
    db.session.commit()
    
    flash('RFI has been accepted.', 'success')
    return redirect(url_for('main.index'))

@main.route('/rfi/<int:id>/reject', methods=['POST'])
@login_required
def reject_rfi(id):
    rfi = RFI.query.get_or_404(id)
    
    if not rfi.can_be_accepted_rejected_by(current_user):
        flash('You are not authorized to reject this RFI.', 'danger')
        return redirect(url_for('main.index'))
    
    rfi.status = 'Rejected'
    rfi.last_action_date = datetime.utcnow()
    db.session.commit()
    
    flash('RFI has been rejected.', 'success')
    return redirect(url_for('main.index'))

@main.route('/api/discipline_codes/<building_code>')
@login_required
def get_discipline_codes(building_code):
    disciplines = db.session.query(Drawing.discipline_code).filter_by(building_code=building_code).distinct().all()
    return jsonify([{'code': d[0]} for d in disciplines])

@main.route('/api/drawings/<building_code>/<discipline_code>')
@login_required
def get_drawings(building_code, discipline_code):
    drawings = Drawing.query.filter_by(
        building_code=building_code,
        discipline_code=discipline_code
    ).all()
    return jsonify([{
        'drawing_number': d.drawing_number,
        'revision_number': d.revision_number
    } for d in drawings])

@main.route('/api/rfi/<int:id>')
@login_required
def get_rfi(id):
    rfi = RFI.query.get_or_404(id)
    return jsonify({
        'id': rfi.id,
        'rfi_number': rfi.rfi_number,
        'status': rfi.status,
        'priority': rfi.priority,
        'submitted_by': rfi.submitted_by,
        'date_created': rfi.date_created.isoformat(),
        'building_code': rfi.building_code,
        'discipline_code': rfi.discipline_code,
        'drawing_number': rfi.drawing_number,
        'inspection_date': rfi.inspection_date.strftime('%Y-%m-%d') if rfi.inspection_date else None,
        'inspection_time': rfi.inspection_time.strftime('%H:%M') if rfi.inspection_time else None,
        'remarks': rfi.remarks,
        'itp': {
            'itp_number': rfi.itp.itp_number,
            'description': rfi.itp.description
        } if rfi.itp else None,
        'itp_phase': {
            'phase_code': rfi.itp_phase.phase_code,
            'activity_name': rfi.itp_phase.activity_name
        } if rfi.itp_phase else None,
        'assigned_to': {
            'id': rfi.assigned_to.id,
            'name': rfi.assigned_to.name,
            'surname': rfi.assigned_to.surname,
            'username': rfi.assigned_to.username,
            'photo': rfi.assigned_to.photo
        } if rfi.assigned_to else None,
        'can_be_accepted_rejected_by': rfi.can_be_accepted_rejected_by(current_user)
    })