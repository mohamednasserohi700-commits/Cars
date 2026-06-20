import os
from app import create_app, db
from app.models import Admin, Employee, Bus, Driver, Station, Settings

app = create_app(os.environ.get('FLASK_ENV', 'development'))


def seed_database():
    """Seed the database with initial data."""
    # Create admin
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("✓ Admin created: admin / admin123")

    # Default settings
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

    # Sample drivers
    if Driver.query.count() == 0:
        drivers = [
            Driver(name='أحمد محمد', phone='0501234567'),
            Driver(name='خالد علي', phone='0507654321'),
            Driver(name='سعد عبدالله', phone='0509876543'),
        ]
        for d in drivers:
            db.session.add(d)
        db.session.flush()
        print("✓ Sample drivers created")

        # Sample buses
        bus1 = Bus(name='خط حي النزهة', total_seats=45, driver_id=drivers[0].id)
        bus2 = Bus(name='خط حي الروضة', total_seats=40, driver_id=drivers[1].id)
        bus3 = Bus(name='خط حي المروة', total_seats=35, driver_id=drivers[2].id)
        db.session.add_all([bus1, bus2, bus3])
        db.session.flush()

        # Set backup buses
        bus1.backup_bus_id = bus2.id
        bus2.backup_bus_id = bus3.id

        # Sample stations
        stations_data = [
            (bus1.id, ['بداية الخط', 'حي النزهة', 'دوار الملك', 'المدينة الطبية', 'البوابة الرئيسية']),
            (bus2.id, ['حي الروضة', 'الطريق الدائري', 'حي السلام', 'البوابة الشمالية']),
            (bus3.id, ['حي المروة', 'شارع الأمير', 'المجمع الحكومي', 'البوابة الرئيسية']),
        ]
        for bus_id, station_names in stations_data:
            for i, name in enumerate(station_names):
                db.session.add(Station(name=name, bus_id=bus_id, order=i+1))
        print("✓ Sample buses and stations created")

    # Sample employees
    if Employee.query.count() == 0:
        employees = [
            Employee(global_id='12345678', name='محمد عبدالرحمن', department='الموارد البشرية', affiliate='مكتب'),
            Employee(global_id='87654321', name='فاطمة أحمد', department='المالية', affiliate='CFI'),
            Employee(global_id='11223344', name='عمر خالد', department='تقنية المعلومات', affiliate='مكتب'),
            Employee(global_id='44332211', name='نورة سعد', department='المشتريات', affiliate='مكتب'),
            Employee(global_id='55667788', name='عبدالله محمد', department='الهندسة', affiliate='CFI'),
        ]
        for emp in employees:
            db.session.add(emp)
        print("✓ Sample employees created")

    db.session.commit()
    print("\n✅ Database seeded successfully!")
    print("─" * 40)
    print("🔑 Admin login: admin / admin123")
    print("👤 Test employee IDs: 12345678, 87654321, 11223344")
    print("─" * 40)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    print("\n🚀 Starting server at http://127.0.0.1:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
