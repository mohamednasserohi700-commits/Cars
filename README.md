# 🚌 نظام إدارة تسجيل خطوط النقل

نظام ويب احترافي لإدارة تسجيل خطوط نقل الموظفين، مبني بـ **Python Flask**.

---

## 🚀 التشغيل السريع

### 1. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 2. تشغيل النظام (أول مرة)
```bash
python run.py
```

سيتم تلقائياً:
- إنشاء قاعدة البيانات
- إضافة بيانات تجريبية

### 3. فتح المتصفح
```
http://localhost:5000
```

---

## 🔑 بيانات الدخول

| النوع | المعلومات |
|-------|-----------|
| **Admin** | اسم المستخدم: `admin` / كلمة المرور: `admin123` |
| **موظف تجريبي** | الرقم العالمي: `12345678` |
| **موظف تجريبي** | الرقم العالمي: `87654321` |
| **موظف تجريبي** | الرقم العالمي: `11223344` |

---

## 📁 هيكل المشروع

```
BusTransportSystem/
├── app/
│   ├── __init__.py          # Factory + Extensions
│   ├── models/              # SQLAlchemy Models
│   ├── routes/
│   │   ├── auth.py          # Login/Logout
│   │   ├── admin.py         # Admin Dashboard
│   │   └── employee.py      # Employee Registration
│   ├── templates/
│   │   ├── auth/            # Login pages
│   │   ├── admin/           # Admin panel
│   │   └── employee/        # Employee pages
│   ├── static/              # CSS, JS, Images
│   └── utils/               # Helpers
├── config.py                # Configuration
├── run.py                   # Entry point
└── requirements.txt
```

---

## ✨ المميزات

### للموظف
- تسجيل دخول بالرقم العالمي (8 أرقام)
- اختيار الخط والمحطة والوردية
- تحويل تلقائي للخط البديل عند الامتلاء
- منع التسجيل المكرر في نفس اليوم

### للمسئول
- **Dashboard** مع إحصائيات ورسوم بيانية
- إدارة الموظفين (إضافة/تعديل/حذف/استيراد/تصدير Excel)
- إدارة خطوط السير والمحطات والسائقين
- سجلات التسجيل مع التصفية والتصدير
- سجلات الدخول (IP، المتصفح، نوع الجهاز)
- إعدادات متكاملة (فتح/إغلاق، أوقات، أيام، شعار)
- تقارير مع رسوم بيانية

---

## 🛡️ الأمان

- CSRF Protection على جميع النماذج
- Password Hashing (Werkzeug)
- Session Management
- Flask-Login لحماية صفحات Admin
- تسجيل جميع محاولات الدخول

---

## 🔧 إعدادات الإنتاج

### تغيير قاعدة البيانات إلى PostgreSQL
في `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@host/dbname'
```

### متغيرات البيئة
```bash
export SECRET_KEY='your-secret-key-here'
export DATABASE_URL='postgresql://...'
export FLASK_ENV='production'
```

---

## 📊 نماذج البيانات

- **Admin** - مسئولو النظام
- **Employee** - الموظفون (الرقم العالمي فريد)
- **Bus** - خطوط السير (مع خط بديل)
- **Driver** - السائقون
- **Station** - محطات كل خط
- **Registration** - تسجيلات الموظفين
- **LoginLog** - سجل عمليات الدخول
- **Settings** - إعدادات النظام (key-value)
