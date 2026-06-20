"""
Run once to fix all missing columns in the registrations table.
    python fix_all.py
"""
import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), 'transport.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(registrations)")
columns = [row[1] for row in cursor.fetchall()]
print("Current columns:", columns)

# Rebuild table with all needed columns
print("\nRebuilding registrations table...")
cursor.executescript("""
    ALTER TABLE registrations RENAME TO registrations_backup;

    CREATE TABLE registrations (
        id INTEGER PRIMARY KEY,
        employee_id INTEGER REFERENCES employees(id),
        guest_global_id VARCHAR(8),
        employee_name VARCHAR(100),
        bus_id INTEGER NOT NULL REFERENCES buses(id),
        station_id INTEGER NOT NULL REFERENCES stations(id),
        shift VARCHAR(20) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        travel_date DATE NOT NULL,
        registration_date DATETIME,
        affiliate VARCHAR(20)
    );

    INSERT INTO registrations (id, employee_id, guest_global_id, employee_name, bus_id, station_id, shift, phone, travel_date, registration_date, affiliate)
    SELECT
        b.id,
        b.employee_id,
        CASE WHEN b.employee_id IS NULL THEN COALESCE(b.guest_global_id, b.global_id_fallback) ELSE NULL END,
        CASE
            WHEN b.employee_id IS NOT NULL THEN (SELECT name FROM employees WHERE id = b.employee_id)
            ELSE COALESCE(b.employee_name_col, b.guest_global_id, b.global_id_fallback)
        END,
        b.bus_id, b.station_id, b.shift, b.phone, b.travel_date, b.registration_date, b.affiliate
    FROM (
        SELECT
            id, employee_id, bus_id, station_id, shift, phone, travel_date, registration_date, affiliate,
            CASE WHEN EXISTS(SELECT 1 FROM pragma_table_info('registrations_backup') WHERE name='guest_global_id')
                THEN guest_global_id ELSE NULL END AS guest_global_id,
            CASE WHEN EXISTS(SELECT 1 FROM pragma_table_info('registrations_backup') WHERE name='employee_name')
                THEN employee_name ELSE NULL END AS employee_name_col,
            NULL as global_id_fallback
        FROM registrations_backup
    ) b;

    DROP TABLE registrations_backup;
""")

conn.commit()
conn.close()
print("✅ Done! All columns are now in place.")
print("   You can delete this file.")
