from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, Stakeholder, ITP, ITPPhase
import random
import string
from werkzeug.security import generate_password_hash

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    return render_template('admin/dashboard.html')

@admin.route('/admin/users')
@login_required
def list_users():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    stakeholders = Stakeholder.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        stakeholder_id = request.form.get('stakeholder_id')

        if not username or not email or not role:
            flash('Please provide all required user details.', 'danger')
            return redirect(url_for('admin.add_user'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.add_user'))

        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_password = generate_password_hash(random_password, method='pbkdf2:sha256')

        user = User(username=username, email=email, role=role, stakeholder_id=stakeholder_id, password=hashed_password, plaintext_password=random_password)
        db.session.add(user)
        db.session.commit()

        flash(f'User added successfully. Temporary password: {random_password}', 'success')
        return redirect(url_for('admin.list_users'))

    return render_template('admin/add_user.html', stakeholders=stakeholders)

@admin.route('/admin/stakeholders')
@login_required
def list_stakeholders():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    stakeholders = Stakeholder.query.all()
    return render_template('admin/stakeholders.html', stakeholders=stakeholders)

@admin.route('/admin/add_stakeholder', methods=['GET', 'POST'])
@login_required
def add_stakeholder():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')

        if not name or not role:
            flash('Please provide all stakeholder details.', 'danger')
            return redirect(url_for('admin.add_stakeholder'))

        stakeholder = Stakeholder(name=name, role=role)
        db.session.add(stakeholder)
        db.session.commit()
        flash('Stakeholder added successfully.', 'success')
        return redirect(url_for('admin.list_stakeholders'))

    return render_template('admin/add_stakeholder.html')


@admin.route('/admin/itps')
@login_required
def list_itps():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    itps = ITP.query.all()
    return render_template('admin/itps.html', itps=itps)

# Route to list all ITP phases independently
@admin.route('/admin/itp_phases')
@login_required
def list_all_itp_phases():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    phases = ITPPhase.query.all()
    return render_template('admin/itp_phases.html', phases=phases)

@admin.route('/admin/add_itp', methods=['GET', 'POST'])
@login_required
def add_itp():
    if current_user.role != 'admin':
        return "Unauthorized", 403
    if request.method == 'POST':
        itp_number = request.form.get('itp_number')
        activity_name = request.form.get('activity_name')
        revision_number = request.form.get('revision_number')
        revision_date_str = request.form.get('revision_date')

        if not all([itp_number, activity_name, revision_number, revision_date_str]):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('admin.add_itp'))

        try:
            from datetime import datetime
            revision_date = datetime.strptime(revision_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')
            return redirect(url_for('admin.add_itp'))

        new_itp = ITP(
            itp_number=itp_number,
            activity_name=activity_name,
            revision_number=revision_number,
            revision_date=revision_date
        )
        
        db.session.add(new_itp)
        db.session.commit()
        flash('ITP created successfully.', 'success')
        return redirect(url_for('admin.list_itps'))

    return render_template('admin/add_itp.html')

@admin.route('/admin/itp/<int:itp_id>/phases')
@login_required
def list_itp_phases(itp_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    itp = ITP.query.get_or_404(itp_id)
    phases = ITPPhase.query.filter_by(itp_id=itp_id).all()
    return render_template('admin/itp_phases.html', itp=itp, phases=phases)

@admin.route('/admin/add_itp_phase/<int:itp_id>', methods=['GET', 'POST'])
@login_required
def add_itp_phase(itp_id):
    if current_user.role != 'admin':
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
    if current_user.role != 'admin':
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
    if current_user.role != 'admin':
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
    if current_user.role != 'admin':
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
    if current_user.role != 'admin':
        return "Unauthorized", 403
    stakeholder = Stakeholder.query.get_or_404(stakeholder_id)
    db.session.delete(stakeholder)
    db.session.commit()
    flash('Stakeholder deleted successfully.', 'success')
    return redirect(url_for('admin.list_stakeholders'))

# ITP deletion route
@admin.route('/admin/delete_itp/<int:itp_id>', methods=['POST'])
@login_required
def delete_itp(itp_id):
    if current_user.role != 'admin':
        return "Unauthorized", 403
    itp = ITP.query.get_or_404(itp_id)
    
    # Delete all associated phases first
    for phase in itp.phases:
        db.session.delete(phase)

    db.session.delete(itp)
    db.session.commit()
    flash('ITP deleted successfully.', 'success')
    return redirect(url_for('admin.list_itps'))