from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    global_id = db.Column(db.String(8), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    affiliate = db.Column(db.String(20), default='مكتب')  # مكتب / CFI
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    registrations = db.relationship('Registration', backref='employee', lazy='dynamic')
    login_logs = db.relationship('LoginLog', backref='employee', lazy='dynamic')

    def __repr__(self):
        return f'<Employee {self.global_id} - {self.name}>'


class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    primary_buses = db.relationship('Bus', foreign_keys='Bus.driver_id', backref='primary_driver', lazy='dynamic')
    backup_buses = db.relationship('Bus', foreign_keys='Bus.backup_driver_id', backref='backup_driver', lazy='dynamic')

    def __repr__(self):
        return f'<Driver {self.name}>'


class Bus(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    total_seats = db.Column(db.Integer, default=50)
    is_active = db.Column(db.Boolean, default=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    backup_driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    backup_bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    stations = db.relationship('Station', backref='bus', lazy='dynamic', cascade='all, delete-orphan')
    registrations = db.relationship('Registration', backref='bus', lazy='dynamic')
    backup_bus = db.relationship('Bus', remote_side='Bus.id', backref='primary_buses', foreign_keys=[backup_bus_id])

    def get_today_registrations_count(self):
        today = datetime.now().date()
        return self.registrations.filter(
            db.func.date(Registration.registration_date) == today
        ).count()

    def get_remaining_seats(self):
        return max(0, self.total_seats - self.get_today_registrations_count())

    def is_full(self):
        return self.get_remaining_seats() <= 0

    def __repr__(self):
        return f'<Bus {self.name}>'


class Station(db.Model):
    __tablename__ = 'stations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    registrations = db.relationship('Registration', backref='station', lazy='dynamic')

    def __repr__(self):
        return f'<Station {self.name}>'


class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    # employee_id is nullable — guests (unregistered employees) will have None here
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    # guest_global_id stores the ID for employees not in the Employee table
    guest_global_id = db.Column(db.String(8), nullable=True, index=True)
    # employee_name stores the name entered at registration time (for guests or known employees)
    employee_name = db.Column(db.String(100), nullable=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('stations.id'), nullable=False)
    shift = db.Column(db.String(20), nullable=False)  # وردية أولى/ثانية/ثالثة
    phone = db.Column(db.String(20), nullable=False)
    pickup_time = db.Column(db.String(10), nullable=True)  # وقت الركوب من المحطة (HH:MM) يدخله الموظف بنفسه
    travel_date = db.Column(db.Date, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.now)
    affiliate = db.Column(db.String(20))

    @property
    def display_global_id(self):
        if self.guest_global_id:
            return self.guest_global_id
        if self.employee:
            return self.employee.global_id
        return '-'

    @property
    def display_name(self):
        return self.employee_name or '-'

    def __repr__(self):
        return f'<Registration {self.id}>'


class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    global_id = db.Column(db.String(8))
    ip_address = db.Column(db.String(50))
    device_type = db.Column(db.String(50))
    browser = db.Column(db.String(100))
    status = db.Column(db.String(20))  # success / failed
    login_time = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<LoginLog {self.global_id} {self.status}>'


class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    @classmethod
    def get(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set(cls, key, value):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            setting.updated_at = datetime.now()
        else:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        db.session.commit()

    def __repr__(self):
        return f'<Settings {self.key}>'
