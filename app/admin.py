from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models import User, Stakeholder, ITP, ITPPhase, Role, Permission, DisciplineCode, RFISettings
import random
import string
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import current_app

admin = Blueprint('admin', __name__)

# Add these constants at the top of the file
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'app/static/uploads/logos'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    return render_template('admin/dashboard.html')

@admin.route('/admin/users')
@login_required
def list_users():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    stakeholders = Stakeholder.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role_id = request.form.get('role')
        stakeholder_id = request.form.get('stakeholder_id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        cell_phone = request.form.get('cell_phone')
        photo = request.files.get('photo')

        if not username or not email or not role_id:
            flash('Please provide all required user details.', 'danger')
            return redirect(url_for('admin.add_user'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.add_user'))

        # Handle photo upload
        photo_filename = None
        if photo and photo.filename:
            if allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                # Create uploads/photos directory if it doesn't exist
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'photos')
                os.makedirs(upload_dir, exist_ok=True)
                photo_path = os.path.join(upload_dir, filename)
                try:
                    photo.save(photo_path)
                    photo_filename = filename
                except Exception as e:
                    flash(f'Error saving photo: {str(e)}', 'danger')
                    return redirect(url_for('admin.add_user'))
            else:
                flash('Invalid file type. Allowed types: PNG, JPG, JPEG, GIF', 'danger')
                return redirect(url_for('admin.add_user'))

        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_password = generate_password_hash(random_password, method='pbkdf2:sha256')

        user = User(
            username=username,
            email=email,
            role_id=role_id,
            stakeholder_id=stakeholder_id,
            password=hashed_password,
            plaintext_password=random_password,
            name=name,
            surname=surname,
            cell_phone=cell_phone,
            photo=photo_filename
        )
        db.session.add(user)
        db.session.commit()

        flash(f'User added successfully. Temporary password: {random_password}', 'success')
        return redirect(url_for('admin.list_users'))

    return render_template('admin/add_user.html', stakeholders=stakeholders)

@admin.route('/admin/stakeholders')
@login_required
def list_stakeholders():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    stakeholders = Stakeholder.query.all()
    return render_template('admin/stakeholders.html', stakeholders=stakeholders)

@admin.route('/admin/add_stakeholder', methods=['GET', 'POST'])
@login_required
def add_stakeholder():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        logo = request.files.get('logo')

        if not name or not role:
            flash('Please provide all stakeholder details.', 'danger')
            return redirect(url_for('admin.add_stakeholder'))

        # Handle logo upload
        logo_filename = None
        if logo and logo.filename:
            if allowed_file(logo.filename):
                filename = secure_filename(logo.filename)
                # Create uploads/logos directory if it doesn't exist
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'logos')
                os.makedirs(upload_dir, exist_ok=True)
                logo_path = os.path.join(upload_dir, filename)
                try:
                    logo.save(logo_path)
                    logo_filename = filename
                except Exception as e:
                    flash(f'Error saving logo: {str(e)}', 'danger')
                    return redirect(url_for('admin.add_stakeholder'))
            else:
                flash('Invalid file type. Allowed types: PNG, JPG, JPEG, GIF', 'danger')
                return redirect(url_for('admin.add_stakeholder'))

        stakeholder = Stakeholder(name=name, role=role, logo=logo_filename)
        db.session.add(stakeholder)
        db.session.commit()
        flash('Stakeholder added successfully.', 'success')
        return redirect(url_for('admin.list_stakeholders'))

    return render_template('admin/add_stakeholder.html')

@admin.route('/admin/itps')
@login_required
def list_itps():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    itps = ITP.query.all()
    return render_template('admin/itps.html', itps=itps)

# Route to list all ITP phases independently
@admin.route('/admin/itp_phases')
@login_required
def list_all_itp_phases():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    phases = ITPPhase.query.all()
    return render_template('admin/itp_phases.html', phases=phases)

@admin.route('/admin/add_itp', methods=['GET', 'POST'])
@login_required
def add_itp():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    if request.method == 'POST':
        itp_number = request.form['itp_number']
        description = request.form['description']
        revision_number = request.form['revision_number']
        revision_date = datetime.strptime(request.form['revision_date'], '%Y-%m-%d').date()
        discipline_code = request.form['discipline_code']

        new_itp = ITP(
            itp_number=itp_number,
            description=description,
            revision_number=revision_number,
            revision_date=revision_date,
            discipline_code=discipline_code
        )
        
        db.session.add(new_itp)
        db.session.commit()
        flash('ITP added successfully.', 'success')
        return redirect(url_for('admin.list_itps'))

    disciplines = DisciplineCode.query.all()
    return render_template('admin/add_itp.html', disciplines=disciplines)

@admin.route('/admin/itp/<int:itp_id>/phases')
@login_required
def list_itp_phases(itp_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    itp = ITP.query.get_or_404(itp_id)
    phases = ITPPhase.query.filter_by(itp_id=itp_id).all()
    return render_template('admin/itp_phases.html', itp=itp, phases=phases)

@admin.route('/admin/add_itp_phase/<int:itp_id>', methods=['GET', 'POST'])
@login_required
def add_itp_phase(itp_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    itp = ITP.query.get_or_404(itp_id)
    stakeholders = Stakeholder.query.all()
    if request.method == 'POST':
        activity_name = request.form.get('activity_name')
        phase_code = request.form.get('phase_code')
        verifying_document = request.form.get('verifying_document')

        if not activity_name:
            flash('Please enter the activity name.', 'danger')
            return redirect(url_for('admin.add_itp_phase', itp_id=itp_id))

        new_phase = ITPPhase(
            itp_id=itp.id,
            activity_name=activity_name,
            phase_code=phase_code,
            verifying_document=verifying_document,
            employer=request.form.get('employer'),
            engineer=request.form.get('engineer'),
            contractor=request.form.get('contractor'),
            subcontractor=request.form.get('subcontractor'),
            third_party=request.form.get('third_party')
        )

        db.session.add(new_phase)
        db.session.commit()
        flash('Phase added successfully.', 'success')
        return redirect(url_for('admin.list_itp_phases', itp_id=itp_id))

    return render_template('admin/add_itp_phase.html', itp=itp, stakeholders=stakeholders)

@admin.route('/admin/edit_itp_phase/<int:phase_id>', methods=['GET', 'POST'])
@login_required
def edit_itp_phase(phase_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    phase = ITPPhase.query.get_or_404(phase_id)
    itp = phase.itp  # Get the associated ITP through the relationship
    
    if request.method == 'POST':
        phase.activity_name = request.form.get('activity_name')
        phase.phase_code = request.form.get('phase_code')
        phase.verifying_document = request.form.get('verifying_document')
        phase.employer = request.form.get('employer')
        phase.engineer = request.form.get('engineer')
        phase.contractor = request.form.get('contractor')
        phase.subcontractor = request.form.get('subcontractor')
        phase.third_party = request.form.get('third_party')

        db.session.commit()
        flash('Phase updated successfully.', 'success')
        return redirect(url_for('admin.list_itp_phases', itp_id=itp.id))

    return render_template('admin/edit_itp_phase.html', phase=phase, itp=itp)

@admin.route('/admin/delete_itp_phase/<int:phase_id>', methods=['POST'])
@login_required
def delete_itp_phase(phase_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    phase = ITPPhase.query.get_or_404(phase_id)
    itp_id = phase.itp_id  # Store the ITP ID before deletion
    
    db.session.delete(phase)
    db.session.commit()
    flash('Phase deleted successfully.', 'success')
    return redirect(url_for('admin.list_itp_phases', itp_id=itp_id))

# User deletion route
@admin.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.list_users'))

# Stakeholder deletion route
@admin.route('/admin/delete_stakeholder/<int:stakeholder_id>', methods=['POST'])
@login_required
def delete_stakeholder(stakeholder_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
    
    # Delete logo file if it exists
    if stakeholder.logo:
        logo_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, stakeholder.logo)
        if os.path.exists(logo_path):
            os.remove(logo_path)
    
    db.session.delete(stakeholder)
    db.session.commit()
    flash('Stakeholder deleted successfully.', 'success')
    return redirect(url_for('admin.list_stakeholders'))

# ITP deletion route
@admin.route('/admin/delete_itp/<int:id>', methods=['POST'])
@login_required
def delete_itp(id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    itp = ITP.query.get_or_404(id)
    
    # Delete all associated phases first
    for phase in itp.phases:
        db.session.delete(phase)

    db.session.delete(itp)
    db.session.commit()
    flash('ITP deleted successfully.', 'success')
    return redirect(url_for('admin.list_itps'))

@admin.route('/admin/edit_itp/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_itp(id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    itp = ITP.query.get_or_404(id)
    
    if request.method == 'POST':
        itp.itp_number = request.form['itp_number']
        itp.description = request.form['description']
        itp.revision_number = request.form['revision_number']
        itp.revision_date = datetime.strptime(request.form['revision_date'], '%Y-%m-%d').date()
        itp.discipline_code = request.form['discipline_code']
        
        db.session.commit()
        flash('ITP updated successfully.', 'success')
        return redirect(url_for('admin.list_itps'))

    disciplines = DisciplineCode.query.all()
    return render_template('admin/edit_itp.html', itp=itp, disciplines=disciplines)

@admin.route('/admin/roles')
@login_required
def manage_roles():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    roles = Role.query.all()
    permissions = Permission.query.all()
    return render_template('admin/manage_roles.html', roles=roles, permissions=permissions)

@admin.route('/admin/roles/add', methods=['POST'])
@login_required
def add_role():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    name = request.form.get('name')
    description = request.form.get('description')
    permission_ids = request.form.getlist('permissions[]')
    
    if not name:
        flash('Role name is required', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    if Role.query.filter_by(name=name).first():
        flash('Role name already exists', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    role = Role(name=name, description=description)
    db.session.add(role)
    
    # Add permissions
    for permission_id in permission_ids:
        permission = Permission.query.get(permission_id)
        if permission:
            role.permissions.append(permission)
    
    db.session.commit()
    flash('Role created successfully', 'success')
    return redirect(url_for('admin.manage_roles'))

@admin.route('/admin/roles/<int:role_id>/edit', methods=['POST'])
@login_required
def edit_role(role_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    role = Role.query.get_or_404(role_id)
    name = request.form.get('name')
    description = request.form.get('description')
    permission_ids = request.form.getlist('permissions[]')
    
    if not name:
        flash('Role name is required', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    # Check if name is already taken by another role
    existing_role = Role.query.filter_by(name=name).first()
    if existing_role and existing_role.id != role_id:
        flash('Role name already exists', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    role.name = name
    role.description = description
    
    # Update permissions
    role.permissions = []
    for permission_id in permission_ids:
        permission = Permission.query.get(permission_id)
        if permission:
            role.permissions.append(permission)
    
    db.session.commit()
    flash('Role updated successfully', 'success')
    return redirect(url_for('admin.manage_roles'))

@admin.route('/admin/roles/<int:role_id>/delete', methods=['POST'])
@login_required
def delete_role(role_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    role = Role.query.get_or_404(role_id)
    
    # Check if role is in use
    if User.query.filter_by(role_id=role_id).first():
        flash('Cannot delete role that is assigned to users', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    db.session.delete(role)
    db.session.commit()
    flash('Role deleted successfully', 'success')
    return redirect(url_for('admin.manage_roles'))

@admin.route('/admin/roles/<int:role_id>/users')
@login_required
def role_users(role_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    role = Role.query.get_or_404(role_id)
    users = User.query.filter_by(role_id=role_id).all()
    return render_template('admin/role_users.html', role=role, users=users)

@admin.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Admin user cannot be edited.', 'danger')
        return redirect(url_for('admin.list_users'))
    
    stakeholders = Stakeholder.query.all()
    roles = Role.query.all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role_id = request.form.get('role')
        stakeholder_id = request.form.get('stakeholder_id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        cell_phone = request.form.get('cell_phone')
        
        if not username or not email or not role_id:
            flash('Please provide all required user details.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Check if username is already taken by another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        user.username = username
        user.email = email
        user.role_id = role_id
        user.stakeholder_id = stakeholder_id
        user.name = name
        user.surname = surname
        user.cell_phone = cell_phone
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.list_users'))
    
    return render_template('admin/edit_user.html', user=user, stakeholders=stakeholders, roles=roles)

@admin.route('/admin/rfi_settings', methods=['GET', 'POST'])
@login_required
def rfi_settings():
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    settings = RFISettings.query.first()
    if not settings:
        settings = RFISettings(
            time_limitations_enabled=False,
            start_time=datetime.strptime('08:30', '%H:%M').time(),
            end_time=datetime.strptime('17:30', '%H:%M').time(),
            updated_by=current_user.username
        )
        db.session.add(settings)
        db.session.commit()
    
    if request.method == 'POST':
        settings.time_limitations_enabled = 'time_limitations_enabled' in request.form
        settings.start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        settings.end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        settings.updated_by = current_user.username
        settings.last_updated = datetime.utcnow()
        
        db.session.commit()
        flash('RFI time settings updated successfully.', 'success')
        return redirect(url_for('admin.rfi_settings'))
    
    return render_template('admin/rfi_settings.html', settings=settings)

@admin.route('/admin/edit_stakeholder/<int:stakeholder_id>', methods=['GET', 'POST'])
@login_required
def edit_stakeholder(stakeholder_id):
    if not current_user.role_obj or current_user.role_obj.name != 'Admin':
        return "Unauthorized", 403
    
    stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        logo = request.files.get('logo')
        
        if not name or not role:
            flash('Please provide all stakeholder details.', 'danger')
            return redirect(url_for('admin.edit_stakeholder', stakeholder_id=stakeholder_id))
        
        # Check if name is already taken by another stakeholder
        existing_stakeholder = Stakeholder.query.filter_by(name=name).first()
        if existing_stakeholder and existing_stakeholder.id != stakeholder_id:
            flash('Stakeholder name already exists.', 'danger')
            return redirect(url_for('admin.edit_stakeholder', stakeholder_id=stakeholder_id))
        
        # Handle logo upload
        if logo and logo.filename:
            if allowed_file(logo.filename):
                filename = secure_filename(logo.filename)
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'logos')
                os.makedirs(upload_dir, exist_ok=True)
                logo_path = os.path.join(upload_dir, filename)
                
                try:
                    # Save the new logo
                    logo.save(logo_path)
                    
                    # Delete old logo if it exists
                    if stakeholder.logo:
                        old_logo_path = os.path.join(upload_dir, stakeholder.logo)
                        if os.path.exists(old_logo_path):
                            os.remove(old_logo_path)
                    
                    stakeholder.logo = filename
                except Exception as e:
                    flash(f'Error handling logo: {str(e)}', 'danger')
                    return redirect(url_for('admin.edit_stakeholder', stakeholder_id=stakeholder_id))
            else:
                flash('Invalid file type. Allowed types: PNG, JPG, JPEG, GIF', 'danger')
                return redirect(url_for('admin.edit_stakeholder', stakeholder_id=stakeholder_id))
        
        stakeholder.name = name
        stakeholder.role = role
        db.session.commit()
        flash('Stakeholder updated successfully.', 'success')
        return redirect(url_for('admin.list_stakeholders'))
    
    return render_template('admin/edit_stakeholder.html', stakeholder=stakeholder)

@admin.route('/admin/logo/<filename>')
def serve_logo(filename):
    return send_from_directory(os.path.join(current_app.static_folder, 'uploads', 'logos'), filename)