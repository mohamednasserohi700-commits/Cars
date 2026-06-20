from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from datetime import datetime, date
from app import db
from app.models import Employee, Bus, Station, Registration, Settings

employee_bp = Blueprint('employee', __name__)


def employee_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'employee_global_id' not in session:
            flash('يرجى تسجيل الدخول أولاً.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def get_current_employee():
    """
    Returns an Employee object if the user is registered in the system,
    or a simple namespace object (guest) if they logged in with an unknown ID.
    """
    if session.get('employee_is_guest'):
        # Build a lightweight guest object so templates don't break
        from types import SimpleNamespace
        guest = SimpleNamespace(
            id=None,
            global_id=session['employee_global_id'],
            name=session['employee_global_id'],
            department='',
            affiliate='مكتب',
            is_active=True,
        )
        return guest
    else:
        return Employee.query.get(session['employee_id'])


def check_registration_open():
    """Check if registration is currently open based on settings."""
    is_open = Settings.get('registration_open', '1')
    if is_open != '1':
        return False, 'closed'

    # Check day
    allowed_days = Settings.get('allowed_days', '0,1,2,3,4')
    today_weekday = str(datetime.now().weekday())
    if allowed_days and today_weekday not in allowed_days.split(','):
        return False, 'wrong_day'

    # Check time
    time_from = Settings.get('time_from', '00:00')
    time_to = Settings.get('time_to', '23:59')
    now_time = datetime.now().strftime('%H:%M')
    if time_from and time_to:
        if not (time_from <= now_time <= time_to):
            return False, 'wrong_time'

    return True, 'open'


@employee_bp.route('/register', methods=['GET', 'POST'])
@employee_required
def register():
    is_open, reason = check_registration_open()
    if not is_open:
        contact_phone = Settings.get('contact_phone', '0500000000')
        return render_template('employee/closed.html', reason=reason, contact_phone=contact_phone)

    employee = get_current_employee()
    buses = Bus.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        bus_id = request.form.get('bus_id')
        station_id = request.form.get('station_id')
        shift = request.form.get('shift')
        phone = request.form.get('phone', '').strip()
        pickup_time = request.form.get('pickup_time', '').strip()
        travel_date_str = request.form.get('travel_date')
        affiliate = request.form.get('affiliate', employee.affiliate)
        employee_name = request.form.get('employee_name', '').strip()

        # Validate
        if not all([bus_id, station_id, shift, phone, pickup_time, travel_date_str, employee_name]):
            flash('يرجى تعبئة جميع الحقول المطلوبة.', 'danger')
            return render_template('employee/register.html', employee=employee, buses=buses)

        try:
            travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('تاريخ غير صحيح.', 'danger')
            return render_template('employee/register.html', employee=employee, buses=buses)

        # Check duplicate — for guests use global_id; for known employees use employee_id
        global_id = session['employee_global_id']
        if employee.id:
            existing = Registration.query.filter_by(
                employee_id=employee.id,
                travel_date=travel_date
            ).first()
        else:
            # Guest: check by global_id stored in registration
            existing = Registration.query.filter_by(
                guest_global_id=global_id,
                travel_date=travel_date
            ).first()

        if existing:
            flash('لقد قمت بالتسجيل مسبقاً لهذا اليوم.', 'warning')
            return render_template('employee/register.html', employee=employee, buses=buses)

        # Check bus availability
        bus = Bus.query.get(bus_id)
        if not bus:
            flash('الخط غير موجود.', 'danger')
            return render_template('employee/register.html', employee=employee, buses=buses)

        used_bus = bus
        used_station_id = station_id
        is_backup = False

        if bus.is_full():
            if bus.backup_bus and not bus.backup_bus.is_full():
                is_backup = True
                used_bus = bus.backup_bus
                backup_station = used_bus.stations.first()
                used_station_id = backup_station.id if backup_station else station_id
            else:
                flash('عذراً، الخط ممتلئ ولا يوجد خط بديل متاح.', 'danger')
                return render_template('employee/register.html', employee=employee, buses=buses)

        # Auto-create employee record if not exists (first-time registration)
        if not employee.id:
            new_emp = Employee(
                global_id=global_id,
                name=employee_name,
                department='',
                affiliate=affiliate,
                is_active=True
            )
            db.session.add(new_emp)
            db.session.flush()  # get the new id without committing
            employee_id_to_use = new_emp.id
            # Update session so next visit recognizes them
            session['employee_id'] = new_emp.id
            session['employee_name'] = employee_name
            session['employee_is_guest'] = False
        else:
            employee_id_to_use = employee.id

        reg = Registration(
            employee_id=employee_id_to_use,
            guest_global_id=global_id,
            employee_name=employee_name,
            bus_id=used_bus.id,
            station_id=used_station_id,
            shift=shift,
            phone=phone,
            pickup_time=pickup_time,
            travel_date=travel_date,
            affiliate=affiliate
        )
        db.session.add(reg)
        db.session.commit()

        return render_template('employee/success.html',
                               employee=employee,
                               bus=used_bus,
                               registration=reg,
                               is_backup=is_backup,
                               original_bus=bus)

    return render_template('employee/register.html', employee=employee, buses=buses)


@employee_bp.route('/stations/<int:bus_id>')
@employee_required
def get_stations(bus_id):
    from flask import jsonify
    stations = Station.query.filter_by(bus_id=bus_id).order_by(Station.order).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in stations])
