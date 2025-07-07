from . import db

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    department = db.Column(db.String(50))
    timetable = db.relationship('Timetable', backref='staff', lazy=True)
    leaves = db.relationship('LeaveRequest', backref='staff', lazy=True)
    substitutions = db.relationship('Substitution', foreign_keys='Substitution.substitute_staff_id', backref='substitute_staff', lazy=True)

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    day = db.Column(db.String(20))
    hour = db.Column(db.Integer)
    subject = db.Column(db.String(100))

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    date = db.Column(db.String(20))
    hour = db.Column(db.Integer)
    reason = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')

class Substitution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    absent_staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    substitute_staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    date = db.Column(db.String(20))
    hour = db.Column(db.Integer)
    reason = db.Column(db.String(255))
    absent_staff = db.relationship('Staff', foreign_keys=[absent_staff_id])
