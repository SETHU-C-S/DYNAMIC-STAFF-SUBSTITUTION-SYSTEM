from datetime import date
from . import db
from .models import Staff, Timetable, LeaveRequest, Substitution

def assign_substitutions():
    today = date.today().strftime('%Y-%m-%d')
    leaves = LeaveRequest.query.filter_by(status='accepted', date=today).all()

    for leave in leaves:
        dept = leave.staff.department

        # Get all staff in the same department
        all_staff = Staff.query.filter_by(department=dept).all()

        # Find staff who are busy at that hour
        busy_staff_ids = [
            t.staff_id for t in Timetable.query.filter_by(day=today_name(), hour=leave.hour)
        ]

        # Filter available staff (not busy and not the same person who is absent)
        available_staff = [
            s for s in all_staff if s.id not in busy_staff_ids and s.id != leave.staff_id
        ]

        # Sort available staff by current substitution count for fairness
        staff_load = {
            s.id: Substitution.query.filter_by(date=today, substitute_staff_id=s.id).count()
            for s in available_staff
        }

        if staff_load:
            selected_id = min(staff_load, key=staff_load.get)

            substitution = Substitution(
                absent_staff_id=leave.staff_id,
                substitute_staff_id=selected_id,
                date=today,
                hour=leave.hour,
                reason=leave.reason
            )

            db.session.add(substitution)

    db.session.commit()

def today_name():
    import datetime
    return datetime.datetime.today().strftime('%A')
