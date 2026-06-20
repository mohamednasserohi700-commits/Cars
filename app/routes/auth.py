from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timezone, timedelta
from app import db
from app.models import Admin, Employee, LoginLog
try:
    from user_agents import parse as ua_parse
    UA_AVAILABLE = True
except ImportError:
    UA_AVAILABLE = False

KSA_TZ = timezone(timedelta(hours=3))
def now_ksa():
    return datetime.now(KSA_TZ).replace(tzinfo=None)

auth_bp = Blueprint('auth', __name__)


def log_employee_login(global_id, employee_id, status):
    ua_string = request.headers.get('User-Agent', '')
    device_type = 'Desktop'
    browser = 'Unknown'
    if UA_AVAILABLE:
        ua = ua_parse(ua_string)
        device_type = 'Mobile' if ua.is_mobile else ('Tablet' if ua.is_tablet else 'Desktop')
        browser = f"{ua.browser.family} {ua.browser.version_string}"
    log = LoginLog(
        employee_id=employee_id,
        global_id=global_id,
        ip_address=request.remote_addr,
        device_type=device_type,
        browser=browser,
        status=status,
        login_time=now_ksa()
    )
    db.session.add(log)
    db.session.commit()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    return render_template('auth/login.html')


@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.check_password(password):
        login_user(admin, remember=False)
        return redirect(url_for('admin.dashboard'))
    flash('اسم المستخدم أو كلمة المرور غير صحيحة.', 'danger')
    return redirect(url_for('auth.login'))


@auth_bp.route('/employee-login', methods=['POST'])
def employee_login():
    global_id = request.form.get('global_id', '').strip()
    if not global_id.isdigit() or len(global_id) != 8:
        flash('الرقم العالمي يجب أن يتكون من 8 أرقام فقط.', 'danger')
        return redirect(url_for('auth.login'))

    # Check if employee exists in the system (registered by admin)
    employee = Employee.query.filter_by(global_id=global_id, is_active=True).first()

    if employee:
        # Known employee — use their full profile
        session['employee_id'] = employee.id
        session['employee_global_id'] = employee.global_id
        session['employee_name'] = employee.name
        session['employee_is_guest'] = False
        log_employee_login(global_id, employee.id, 'success')
    else:
        # Unknown employee — allow access as guest with just their global_id
        session['employee_id'] = None
        session['employee_global_id'] = global_id
        session['employee_name'] = global_id   # display name = their ID
        session['employee_is_guest'] = True
        log_employee_login(global_id, None, 'success')

    return redirect(url_for('employee.register'))


@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    session.clear()
    return redirect(url_for('auth.login'))
