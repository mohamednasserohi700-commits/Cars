"""
سكريبت لإضافة عمود pickup_time (وقت الركوب من المحطة) إلى جدول registrations
في حال كانت قاعدة البيانات قديمة ولا تحتوي على هذا العمود.

طريقة التشغيل:
    python add_pickup_time_column.py

يعمل تلقائيًا سواء كانت قاعدة البيانات SQLite محلية أو PostgreSQL (عبر DATABASE_URL).
آمن للتشغيل أكثر من مرة: لو العمود موجود بالفعل لن يفعل شيئًا.
"""

import sys
from sqlalchemy import text, inspect

# استيراد إعدادات المشروع نفسها لمعرفة مكان قاعدة البيانات تلقائيًا
from config import get_database_url
from app import create_app, db

COLUMN_NAME = 'pickup_time'
TABLE_NAME = 'registrations'


def main():
    app = create_app('default')

    with app.app_context():
        db_url = get_database_url()
        print(f'جاري الاتصال بقاعدة البيانات: {db_url.split("@")[-1] if "@" in db_url else db_url}')

        inspector = inspect(db.engine)

        if TABLE_NAME not in inspector.get_table_names():
            print(f'خطأ: الجدول "{TABLE_NAME}" غير موجود في قاعدة البيانات.')
            sys.exit(1)

        existing_columns = [col['name'] for col in inspector.get_columns(TABLE_NAME)]

        if COLUMN_NAME in existing_columns:
            print(f'العمود "{COLUMN_NAME}" موجود بالفعل في جدول "{TABLE_NAME}". لا حاجة لأي تعديل.')
            return

        print(f'العمود "{COLUMN_NAME}" غير موجود. جاري إضافته...')

        # نوع العمود يختلف قليلاً بين SQLite و PostgreSQL لكن VARCHAR(10) يعمل في كلتيهما
        alter_sql = text(f'ALTER TABLE {TABLE_NAME} ADD COLUMN {COLUMN_NAME} VARCHAR(10)')

        try:
            with db.engine.connect() as conn:
                conn.execute(alter_sql)
                conn.commit()
            print(f'تم بنجاح إضافة العمود "{COLUMN_NAME}" إلى جدول "{TABLE_NAME}".')
            print('يمكنك الآن إعادة تشغيل السيرفر بشكل طبيعي.')
        except Exception as e:
            print(f'حدث خطأ أثناء إضافة العمود: {e}')
            sys.exit(1)


if __name__ == '__main__':
    main()
