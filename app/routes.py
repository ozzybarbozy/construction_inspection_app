from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from .models import RFI, ITP
from . import db

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    rfis = RFI.query.order_by(RFI.date_created.desc()).all()
    return render_template('index.html', rfis=rfis)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_rfi():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        submitted_by = request.form['submitted_by']

        new_rfi = RFI(
            title=title,
            description=description,
            location=location,
            submitted_by=submitted_by
        )

        db.session.add(new_rfi)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('add_rfi.html')

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
        rfi.title = request.form['title']
        rfi.description = request.form['description']
        rfi.location = request.form['location']
        rfi.submitted_by = request.form['submitted_by']

        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('edit_rfi.html', rfi=rfi)

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