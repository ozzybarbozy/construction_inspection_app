from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, send_file
from flask_login import login_required, current_user
from app import db
from app.models import User, Stakeholder, ITP, ITPPhase, UserRole, Permission, DisciplineCode, RFISettings, StakeholderRole, Drawing, Building
from app.decorators import admin_required
import random
import string
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask import current_app
from io import BytesIO

admin = Blueprint('admin', __name__)

# Add these constants at the top of the file
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'app/static/uploads/logos'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get counts for dashboard
    total_users = User.query.count()
    total_roles = UserRole.query.count()
    total_permissions = Permission.query.count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_roles=total_roles,
                         total_permissions=total_permissions)

@admin.route('/admin/users')
@login_required
def list_users():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    stakeholders = Stakeholder.query.all()
    roles = UserRole.query.all()
    disciplines = DisciplineCode.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role_id = request.form.get('role')
        stakeholder_id = request.form.get('stakeholder_id')
        discipline_code = request.form.get('discipline_code')
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
            user_role_id=role_id,
            stakeholder_id=stakeholder_id,
            discipline_code=discipline_code,
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

    return render_template('admin/add_user.html', 
                         stakeholders=stakeholders, 
                         roles=roles,
                         disciplines=disciplines)

@admin.route('/admin/stakeholders')
@login_required
def list_stakeholders():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    stakeholders = Stakeholder.query.all()
    return render_template('admin/stakeholders.html', stakeholders=stakeholders)

@admin.route('/admin/add_stakeholder', methods=['GET', 'POST'])
@login_required
def add_stakeholder():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    if request.method == 'POST':
        name = request.form.get('name')
        role_name = request.form.get('role')
        logo = request.files.get('logo')

        if not name or not role_name:
            flash('Please provide all stakeholder details.', 'danger')
            return redirect(url_for('admin.add_stakeholder'))

        # Get the stakeholder role
        stakeholder_role = StakeholderRole.query.filter_by(name=role_name).first()
        if not stakeholder_role:
            flash('Invalid stakeholder role.', 'danger')
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

        stakeholder = Stakeholder(
            name=name,
            stakeholder_role_id=stakeholder_role.id,
            logo=logo_filename
        )
        db.session.add(stakeholder)
        db.session.commit()
        flash('Stakeholder added successfully.', 'success')
        return redirect(url_for('admin.list_stakeholders'))

    return render_template('admin/add_stakeholder.html')

@admin.route('/admin/itps')
@login_required
def list_itps():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    itps = ITP.query.all()
    return render_template('admin/itps.html', itps=itps)

# Route to list all ITP phases independently
@admin.route('/admin/itp_phases')
@login_required
def list_all_itp_phases():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    phases = ITPPhase.query.all()
    return render_template('admin/itp_phases.html', phases=phases)

@admin.route('/admin/add_itp', methods=['GET', 'POST'])
@login_required
def add_itp():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
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
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    itp = ITP.query.get_or_404(itp_id)
    phases = ITPPhase.query.filter_by(itp_id=itp_id).all()
    return render_template('admin/itp_phases.html', itp=itp, phases=phases)

@admin.route('/admin/add_itp_phase/<int:itp_id>', methods=['GET', 'POST'])
@login_required
def add_itp_phase(itp_id):
    if not current_user.user_role or current_user.user_role.name != 'Admin':
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
    if not current_user.user_role or current_user.user_role.name != 'Admin':
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
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    
    phase = ITPPhase.query.get_or_404(phase_id)
    itp_id = phase.itp_id  # Store the ITP ID before deletion
    
    db.session.delete(phase)
    db.session.commit()
    flash('Phase deleted successfully.', 'success')
    return redirect(url_for('admin.list_itp_phases', itp_id=itp_id))

# User deletion route
@admin.route('/admin/delete_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    if not current_user.user_role or current_user.user_role.name != 'Admin':
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
    if not current_user.user_role or current_user.user_role.name != 'Admin':
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
    if not current_user.user_role or current_user.user_role.name != 'Admin':
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
    if not current_user.user_role or current_user.user_role.name != 'Admin':
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
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    roles = UserRole.query.all()
    permissions = Permission.query.all()
    return render_template('admin/manage_roles.html', roles=roles, permissions=permissions)

@admin.route('/admin/roles/add', methods=['GET', 'POST'])
@login_required
def add_role():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    
    name = request.form.get('name')
    description = request.form.get('description')
    color = request.form.get('color', '#007bff')  # Default to Bootstrap primary color
    permission_ids = request.form.getlist('permissions[]')
    
    if not name:
        flash('Role name is required', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    if UserRole.query.filter_by(name=name).first():
        flash('Role name already exists', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    role = UserRole(name=name, description=description, color=color)
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
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    
    try:
        role = UserRole.query.get_or_404(role_id)
        name = request.form.get('name')
        description = request.form.get('description')
        color = request.form.get('color', '#007bff')  # Default to Bootstrap primary color
        
        if not name:
            flash('Role name is required', 'danger')
            return redirect(url_for('admin.manage_roles'))
        
        # Check if name is already taken by another role
        existing_role = UserRole.query.filter_by(name=name).first()
        if existing_role and existing_role.id != role_id:
            flash(f'Role name "{name}" is already in use by another role', 'danger')
            return redirect(url_for('admin.manage_roles'))
        
        role.name = name
        role.description = description
        role.color = color
        
        db.session.commit()
        flash('Role updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating role: {str(e)}', 'danger')
    
    return redirect(url_for('admin.manage_roles'))

@admin.route('/admin/roles/<int:role_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_role(role_id):
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    
    role = UserRole.query.get_or_404(role_id)
    
    # Check if role is in use
    if User.query.filter_by(user_role_id=role_id).first():
        flash('Cannot delete role that is assigned to users', 'danger')
        return redirect(url_for('admin.manage_roles'))
    
    db.session.delete(role)
    db.session.commit()
    flash('Role deleted successfully', 'success')
    return redirect(url_for('admin.manage_roles'))

@admin.route('/admin/roles/<int:role_id>/users')
@login_required
def role_users(role_id):
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    
    role = UserRole.query.get_or_404(role_id)
    users = User.query.filter_by(user_role_id=role_id).all()
    return render_template('admin/role_users.html', role=role, users=users)

@admin.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    
    user = User.query.get_or_404(user_id)
    roles = UserRole.query.all()
    stakeholders = Stakeholder.query.all()
    disciplines = DisciplineCode.query.all()  # Get all disciplines
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.user_role_id = request.form.get('role')
        user.stakeholder_id = request.form.get('stakeholder_id')
        user.discipline_code = request.form.get('discipline_code')  # Update discipline code
        user.name = request.form.get('name')
        user.surname = request.form.get('surname')
        user.cell_phone = request.form.get('cell_phone')
        
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.list_users'))
    
    return render_template('admin/edit_user.html', 
                         user=user, 
                         roles=roles, 
                         stakeholders=stakeholders,
                         disciplines=disciplines)  # Pass disciplines to template

@admin.route('/admin/rfi_settings', methods=['GET', 'POST'])
@login_required
def rfi_settings():
    if not current_user.user_role or current_user.user_role.name != 'Admin':
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
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    
    stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        role_name = request.form.get('role')
        logo = request.files.get('logo')
        
        if not name or not role_name:
            flash('Please provide all stakeholder details.', 'danger')
            return redirect(url_for('admin.edit_stakeholder', stakeholder_id=stakeholder_id))
        
        # Get the stakeholder role
        stakeholder_role = StakeholderRole.query.filter_by(name=role_name).first()
        if not stakeholder_role:
            flash('Invalid stakeholder role.', 'danger')
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
        stakeholder.stakeholder_role_id = stakeholder_role.id
        db.session.commit()
        flash('Stakeholder updated successfully.', 'success')
        return redirect(url_for('admin.list_stakeholders'))
    
    return render_template('admin/edit_stakeholder.html', stakeholder=stakeholder)

@admin.route('/admin/logo/<filename>')
def serve_logo(filename):
    return send_from_directory(os.path.join(current_app.static_folder, 'uploads', 'logos'), filename)

@admin.route('/admin/permissions')
@login_required
def manage_permissions():
    if not current_user.has_permission('manage_permissions'):
        return "Unauthorized", 403
    
    # Get system-critical permissions
    system_permissions = Permission.query.filter(
        Permission.code.in_(['manage_system', 'manage_permissions', 'manage_roles', 'manage_users'])
    ).all()
    
    # Get manageable permissions (all permissions except system ones)
    manageable_permissions = Permission.query.filter(
        ~Permission.code.in_(['manage_system', 'manage_permissions', 'manage_roles', 'manage_users'])
    ).all()
    
    return render_template('admin/manage_permissions.html', 
                         system_permissions=system_permissions,
                         manageable_permissions=manageable_permissions)

@admin.route('/admin/permissions/add', methods=['POST'])
@login_required
def add_permission():
    if not current_user.has_permission('manage_permissions'):
        return "Unauthorized", 403
    
    name = request.form.get('name')
    code = request.form.get('code')
    description = request.form.get('description')
    
    if not name or not code:
        flash('Name and code are required', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    # Check if code is already taken
    if Permission.query.filter_by(code=code).first():
        flash('Permission code already exists', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    permission = Permission(name=name, code=code, description=description)
    db.session.add(permission)
    db.session.commit()
    
    flash('Permission created successfully', 'success')
    return redirect(url_for('admin.manage_permissions'))

@admin.route('/admin/permissions/<int:permission_id>/edit', methods=['POST'])
@login_required
def edit_permission(permission_id):
    if not current_user.has_permission('manage_permissions'):
        return "Unauthorized", 403
    
    permission = Permission.query.get_or_404(permission_id)
    
    # Check if this is a system permission
    if permission.code in ['manage_system', 'manage_permissions', 'manage_roles', 'manage_users']:
        flash('Cannot edit system permissions', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    name = request.form.get('name')
    code = request.form.get('code')
    description = request.form.get('description')
    
    if not name or not code:
        flash('Name and code are required', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    # Check if code is already taken by another permission
    existing_permission = Permission.query.filter_by(code=code).first()
    if existing_permission and existing_permission.id != permission_id:
        flash('Permission code already exists', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    permission.name = name
    permission.code = code
    permission.description = description
    db.session.commit()
    
    flash('Permission updated successfully', 'success')
    return redirect(url_for('admin.manage_permissions'))

@admin.route('/admin/permissions/<int:permission_id>/delete', methods=['POST'])
@login_required
def delete_permission(permission_id):
    if not current_user.has_permission('manage_permissions'):
        return "Unauthorized", 403
    
    permission = Permission.query.get_or_404(permission_id)
    
    # Check if this is a system permission
    if permission.code in ['manage_system', 'manage_permissions', 'manage_roles', 'manage_users']:
        flash('Cannot delete system permissions', 'danger')
        return redirect(url_for('admin.manage_permissions'))
    
    db.session.delete(permission)
    db.session.commit()
    
    flash('Permission deleted successfully', 'success')
    return redirect(url_for('admin.manage_permissions'))

@admin.route('/admin/roles/<int:role_id>/permissions', methods=['GET', 'POST'])
@login_required
def manage_role_permissions(role_id):
    if not current_user.user_role or current_user.user_role.name != 'Admin':
        return "Unauthorized", 403
    
    role = UserRole.query.get_or_404(role_id)
    
    if request.method == 'POST':
        try:
            permission_ids = request.form.getlist('permissions[]')
            
            # Update permissions
            role.permissions = []
            for permission_id in permission_ids:
                permission = Permission.query.get(permission_id)
                if permission:
                    role.permissions.append(permission)
            
            db.session.commit()
            flash('Role permissions updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating role permissions: {str(e)}', 'danger')
        
        return redirect(url_for('admin.manage_role_permissions', role_id=role_id))
    
    # Get all permissions grouped by type
    system_permissions = Permission.query.filter(
        Permission.code.in_(['manage_system', 'manage_permissions', 'manage_roles', 'manage_users'])
    ).all()
    
    regular_permissions = Permission.query.filter(
        ~Permission.code.in_(['manage_system', 'manage_permissions', 'manage_roles', 'manage_users'])
    ).all()
    
    return render_template('admin/manage_role_permissions.html',
                         role=role,
                         system_permissions=system_permissions,
                         regular_permissions=regular_permissions)

@admin.route('/drawings')
@login_required
@admin_required
def drawings_redirect():
    return redirect(url_for('admin.list_drawings'))

@admin.route('/admin/drawings')
@login_required
@admin_required
def list_drawings():
    # Get filter parameters
    building_code = request.args.get('building')
    discipline_code = request.args.get('discipline')
    
    # Base query
    query = Drawing.query
    
    # Apply filters if provided
    if building_code:
        query = query.filter(Drawing.building_code == building_code)
    if discipline_code:
        query = query.filter(Drawing.discipline_code == discipline_code)
    
    # Get filtered drawings
    drawings = query.all()
    
    # Get total count
    total_count = len(drawings)
    
    # Get unique building codes with counts from existing drawings
    buildings = db.session.query(
        Building.code,
        Building.name,
        db.func.count(Drawing.id).label('drawing_count')
    ).join(
        Drawing,
        Building.code == Drawing.building_code
    ).group_by(
        Building.code,
        Building.name
    ).order_by(Building.code).all()
    
    # Get unique discipline codes with counts from existing drawings
    disciplines = db.session.query(
        DisciplineCode.code,
        DisciplineCode.name,
        db.func.count(Drawing.id).label('drawing_count')
    ).join(
        Drawing,
        DisciplineCode.code == Drawing.discipline_code
    ).group_by(
        DisciplineCode.code,
        DisciplineCode.name
    ).order_by(DisciplineCode.code).all()
    
    return render_template('admin/drawings.html',
                         drawings=drawings,
                         total_count=total_count,
                         buildings=buildings,
                         disciplines=disciplines,
                         selected_building=building_code,
                         selected_discipline=discipline_code)

@admin.route('/admin/upload_drawings', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_drawings():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('admin.upload_drawings'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('admin.upload_drawings'))
        
        try:
            import pandas as pd
            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file, header=0)
            else:
                flash('Please upload an Excel (.xlsx) file', 'error')
                return redirect(url_for('admin.upload_drawings'))
            
            # Expected columns in order
            expected_columns = [
                'Building Code',
                'Discipline Code',
                'Sequence Number',
                'Revision Number',
                'Drawing Title',
                'Issue Date'
            ]
            
            # Check if all required columns exist
            missing_columns = [col for col in expected_columns if col not in df.columns]
            if missing_columns:
                flash(f'Missing required columns: {", ".join(missing_columns)}', 'error')
                return redirect(url_for('admin.upload_drawings'))
            
            # Process each row
            success_count = 0
            error_count = 0
            error_messages = []
            
            for index, row in df.iterrows():
                try:
                    building_code = str(row['Building Code']).strip()
                    discipline_code = str(row['Discipline Code']).strip()
                    sequence_number = int(row['Sequence Number'])
                    revision_number = str(row['Revision Number']).strip()
                    drawing_title = str(row['Drawing Title']).strip() if pd.notna(row['Drawing Title']) else None
                    
                    # Handle issue date
                    issue_date = None
                    if pd.notna(row['Issue Date']):
                        try:
                            from datetime import datetime
                            # Convert to string first in case it's a datetime object
                            date_str = str(row['Issue Date'])
                            # Try to parse the date string
                            issue_date = datetime.strptime(date_str.split()[0], '%Y-%m-%d').date()
                        except ValueError:
                            error_messages.append(f"Row {index + 1}: Invalid date format '{date_str}'. Expected format: YYYY-MM-DD")
                            error_count += 1
                            continue
                    
                    # Validate required fields
                    if not all([building_code, discipline_code, sequence_number, revision_number]):
                        error_messages.append(f"Row {index + 1}: Missing required fields")
                        error_count += 1
                        continue
                    
                    # Create new drawing
                    drawing = Drawing(
                        building_code=building_code,
                        discipline_code=discipline_code,
                        sequence_number=sequence_number,
                        revision_number=revision_number,
                        drawing_title=drawing_title,
                        issue_date=issue_date
                    )
                    db.session.add(drawing)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    error_messages.append(f"Row {index + 1}: {str(e)}")
            
            if error_count > 0:
                flash(f'Successfully imported {success_count} drawings. {error_count} errors occurred:', 'warning')
                for msg in error_messages:
                    flash(msg, 'error')
            else:
                flash(f'Successfully imported {success_count} drawings.', 'success')
            
            db.session.commit()
            return redirect(url_for('admin.list_drawings'))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(url_for('admin.upload_drawings'))
    
    return render_template('admin/upload_drawings.html')

@admin.route('/admin/download_drawing_template')
@login_required
@admin_required
def download_drawing_template():
    try:
        import pandas as pd
        import xlsxwriter
        
        # Create a sample DataFrame with the required fields
        data = {
            'Building Code': ['ES04', 'ES05'],
            'Discipline Code': ['CV', 'AR'],
            'Sequence Number': [100, 1],
            'Revision Number': ['01', '02'],
            'Drawing Title': ['Foundation Grading Plan', 'Architectural Drawings'],
            'Issue Date': ['2024-12-03', '2024-12-09']
        }
        
        df = pd.DataFrame(data)
        
        # Create Excel writer
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Drawings')
        
        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Drawings']
        
        # Set column widths
        worksheet.set_column('A:F', 15)
        
        # Add header formatting
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # Apply header formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Close the Pandas Excel writer
        writer.close()
        
        # Create response
        output.seek(0)
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='drawing_template.xlsx'
        )
        
    except Exception as e:
        flash(f'Error generating template: {str(e)}', 'error')
        return redirect(url_for('admin.upload_drawings'))

@admin.route('/admin/add_drawing', methods=['GET', 'POST'])
@login_required
@admin_required
def add_drawing():
    if request.method == 'POST':
        drawing_number = request.form.get('drawing_number')
        building_code = request.form.get('building_code')
        discipline_code = request.form.get('discipline_code')
        sequence_number = request.form.get('sequence_number')
        revision_number = request.form.get('revision_number')

        drawing = Drawing(
            drawing_number=drawing_number,
            building_code=building_code,
            discipline_code=discipline_code,
            sequence_number=sequence_number,
            revision_number=revision_number
        )
        db.session.add(drawing)
        db.session.commit()
        flash('Drawing added successfully.', 'success')
        return redirect(url_for('admin.list_drawings'))

    buildings = Building.query.all()
    disciplines = DisciplineCode.query.all()
    return render_template('admin/add_drawing.html', buildings=buildings, disciplines=disciplines)

@admin.route('/admin/edit_drawing/<int:drawing_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_drawing(drawing_id):
    drawing = Drawing.query.get_or_404(drawing_id)
    
    if request.method == 'POST':
        drawing.drawing_number = request.form.get('drawing_number')
        drawing.building_code = request.form.get('building_code')
        drawing.discipline_code = request.form.get('discipline_code')
        drawing.sequence_number = request.form.get('sequence_number')
        drawing.revision_number = request.form.get('revision_number')
        
        db.session.commit()
        flash('Drawing updated successfully.', 'success')
        return redirect(url_for('admin.list_drawings'))
    
    buildings = Building.query.all()
    disciplines = DisciplineCode.query.all()
    return render_template('admin/edit_drawing.html', drawing=drawing, buildings=buildings, disciplines=disciplines)

@admin.route('/admin/delete_drawing/<int:drawing_id>', methods=['POST'])
@login_required
@admin_required
def delete_drawing(drawing_id):
    drawing = Drawing.query.get_or_404(drawing_id)
    db.session.delete(drawing)
    db.session.commit()
    flash('Drawing deleted successfully.', 'success')
    return redirect(url_for('admin.list_drawings'))

@admin.route('/admin/stakeholder_roles/<int:role_id>/permissions', methods=['GET', 'POST'])
@login_required
def manage_stakeholder_role_permissions(role_id):
    if not current_user.has_permission('manage_permissions'):
        return "Unauthorized", 403
    
    role = StakeholderRole.query.get_or_404(role_id)
    
    if request.method == 'POST':
        try:
            permission_ids = request.form.getlist('permissions[]')
            
            # Update permissions
            role.permissions = []
            for permission_id in permission_ids:
                permission = Permission.query.get(permission_id)
                if permission:
                    role.permissions.append(permission)
            
            db.session.commit()
            flash('Stakeholder role permissions updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating stakeholder role permissions: {str(e)}', 'danger')
        
        return redirect(url_for('admin.manage_stakeholder_role_permissions', role_id=role_id))
    
    # Get all permissions grouped by type
    system_permissions = Permission.query.filter(
        Permission.code.in_(['manage_system', 'manage_permissions', 'manage_roles', 'manage_users'])
    ).all()
    
    regular_permissions = Permission.query.filter(
        ~Permission.code.in_(['manage_system', 'manage_permissions', 'manage_roles', 'manage_users'])
    ).all()
    
    return render_template('admin/manage_stakeholder_role_permissions.html',
                         role=role,
                         system_permissions=system_permissions,
                         regular_permissions=regular_permissions)