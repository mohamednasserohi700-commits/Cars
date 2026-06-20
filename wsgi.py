import os
from app import create_app, db
from app.models import Admin, Employee, Bus, Driver, Station, Settings

app = create_app(os.environ.get('FLASK_ENV', 'production'))

def init_db():
    """Initialize database and seed if empty."""
    with app.app_context():
        db.create_all()
        
        # Seed only if empty
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(username='admin')
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)

        defaults = {
            'registration_open': '1',
            'allowed_days': '0,1,2,3,4',
            'time_from': '00:00',
            'time_to': '23:59',
            'contact_phone': '0500000000',
            'company_name': 'شركة النقل',
            'theme': 'light',
        }
        for key, value in defaults.items():
            if not Settings.query.filter_by(key=key).first():
                db.session.add(Settings(key=key, value=value))

        db.session.commit()

init_db()

if __name__ == '__main__':
    app.run()
