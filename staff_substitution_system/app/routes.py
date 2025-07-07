from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, Staff, Timetable, LeaveRequest, Substitution
from datetime import date
from .substitution_scheduler import assign_substitutions


app = Blueprint('main_app', __name__)

HOD_USERNAME = "hod"
HOD_PASSWORD = "admin123"

@app.route('/')
def index():
    return render_template('choose_role.html')

@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if role == 'hod':
            if email == HOD_USERNAME and password == HOD_PASSWORD:
                session['user'] = 'hod'
                return redirect(url_for('main_app.hod_dashboard'))
            else:
                flash('Invalid HOD credentials')

        elif role == 'staff':
            staff = Staff.query.filter_by(email=email).first()
            if staff and check_password_hash(staff.password, password):
                session['user'] = staff.id
                return redirect(url_for('main_app.staff_dashboard'))
            else:
                flash('Invalid Staff credentials')

        return redirect(url_for('main_app.login', role=role))

    return render_template('login.html', role=role)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main_app.index'))

# ------------------ HOD ROUTES ------------------
@app.route('/hod/dashboard')
def hod_dashboard():
    if session.get('user') != 'hod': return redirect('/')
    staff_list = Staff.query.all()
    leaves = LeaveRequest.query.filter_by(status='pending').all()
    return render_template('hod_dashboard.html', staff=staff_list, leaves=leaves)

@app.route('/hod/add_staff', methods=['POST'])
def add_staff():
    if session.get('user') != 'hod': return redirect('/')
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    dept = request.form['department']

    if Staff.query.filter_by(email=email).first():
        flash('Email already exists')
        return redirect(url_for('main_app.hod_dashboard'))

    hashed_password = generate_password_hash(password)
    new_staff = Staff(name=name, email=email, password=hashed_password, department=dept)
    db.session.add(new_staff)
    db.session.commit()
    flash('Staff added successfully')
    return redirect(url_for('main_app.hod_dashboard'))

@app.route('/hod/approve_leave/<int:leave_id>/<action>')
def approve_leave(leave_id, action):
    if session.get('user') != 'hod': return redirect('/')
    leave = LeaveRequest.query.get_or_404(leave_id)
    leave.status = 'accepted' if action == 'accept' else 'rejected'
    db.session.commit()
    flash(f'Leave {action}ed successfully')
    return redirect(url_for('main_app.hod_dashboard'))

@app.route('/hod/add_timetable', methods=['GET', 'POST'])
def add_timetable():
    if session.get('user') != 'hod': return redirect('/')
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        day = request.form['day']
        hour = int(request.form['hour'])
        subject = request.form['subject']

        # Prevent duplicate hour entries for same staff and day
        exists = Timetable.query.filter_by(staff_id=staff_id, day=day, hour=hour).first()
        if exists:
            flash('Timetable entry already exists for this hour')
        else:
            new_entry = Timetable(staff_id=staff_id, day=day, hour=hour, subject=subject)
            db.session.add(new_entry)
            db.session.commit()
            flash('Timetable entry added')
        return redirect(url_for('main_app.hod_dashboard'))
    staff_list = Staff.query.all()
    return render_template('add_timetable.html', staff=staff_list)

@app.route('/hod/substitutions')
def view_substitutions():
    if session.get('user') != 'hod': return redirect('/')
    subs = Substitution.query.all()
    return render_template('substitutions.html', substitutions=subs)

# ------------------ STAFF ROUTES ------------------
@app.route('/staff/dashboard')
def staff_dashboard():
    staff_id = session.get('user')
    if not isinstance(staff_id, int): return redirect('/')
    timetable = Timetable.query.filter_by(staff_id=staff_id).all()
    subs = Substitution.query.filter_by(substitute_staff_id=staff_id).all()
    return render_template('staff_dashboard.html', timetable=timetable, substitutions=subs)

@app.route('/staff/apply_leave', methods=['GET', 'POST'])
def apply_leave():
    staff_id = session.get('user')
    if not isinstance(staff_id, int): return redirect('/')
    if request.method == 'POST':
        date_val = request.form['date']
        hour = int(request.form['hour'])
        reason = request.form['reason']
        exists = LeaveRequest.query.filter_by(staff_id=staff_id, date=date_val, hour=hour).first()
        if exists:
            flash('Already applied leave for this hour')
        else:
            leave = LeaveRequest(staff_id=staff_id, date=date_val, hour=hour, reason=reason)
            db.session.add(leave)
            db.session.commit()
            flash('Leave request submitted')
        return redirect(url_for('main_app.staff_dashboard'))
    return render_template('apply_leave.html')
@app.route('/hod/generate_substitutions')
def generate_substitutions():
    if session.get('user') != 'hod': return redirect('/')
    assign_substitutions()
    flash("Substitution duties assigned successfully.")
    return redirect(url_for('main_app.hod_dashboard'))

