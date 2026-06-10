# Quick Start Guide - نظام حجز المواعيد

## 🚀 البدء السريع

### متطلبات النظام

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- 2GB RAM minimum
- Connection to internet

### التثبيت خطوة بخطوة

#### 1. استنساخ المستودع

```bash
git clone https://github.com/molebelr-crypto/Salon-Booking-.git
cd Salon-Booking-
```

#### 2. إعداد بيئة افتراضية

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

#### 4. إنشاء ملف البيئة

```bash
cp .env.example .env
```

#### 5. تحديث ملف .env

```bash
nano .env
```

أضف القيم الآتية:

```env
BOT_TOKEN=your_regenerated_token_from_botfather
ADMIN_ID=your_telegram_user_id
DATABASE_URL=postgresql://salon_user:strong_password@localhost:5432/salon_booking
ENVIRONMENT=development
DEBUG=True
```

#### 6. إعداد قاعدة البيانات

```bash
# استخدم PostgreSQL
psql -U postgres

# داخل PostgreSQL:
CREATE DATABASE salon_booking;
CREATE USER salon_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE salon_booking TO salon_user;
\q

# تهيئة الجداول
python -c "from database import init_db; init_db()"
```

#### 7. تشغيل البوت

```bash
python main.py
```

يجب أن ترى:

```
============================================================
🏪 نظام حجز المواعيد - Salon Booking System
============================================================
🌍 البيئة: development
🔧 وضع التطوير: True
📊 مستوى التسجيل: DEBUG
============================================================
💾 Initializing database...
✅ Database initialized successfully
🤖 Creating bot application...
✅ Bot application created successfully
📱 Starting with polling mode
🔌 Server: 0.0.0.0:8000
👂 Listening for updates...
```

---

## 📱 اختبار البوت

### على Telegram

1. ابحث عن بوتك في Telegram
2. اضغط `/start`
3. اختبر الأوامر:

```
/help              → عرض المساعدة
/about             → عن التطبيق
/book              → حجز موعد جديد (كعميل)
/newowner          → تسجيل صالون جديد
/owner             → لوحة ملاك الصالون
/admin             → لوحة الإدارة (للمسؤول فقط)
/pay               → نظام الدفع
```

---

## 🔄 سير العمل الكامل

### لعميل جديد:

1. اضغط `/start`
2. اختر "📅 Book Appointment"
3. أدخل رمز الصالون
4. اختر الخدمة والموظف
5. اختر التاريخ والوقت
6. ادفع (اختياري: أدخل كود خصم)
7. تأكيد الحجز ✅

### لملاك صالون جديد:

1. اضغط `/newowner`
2. أجب على 7 أسئلة:
   - اسم الصالون
   - رقم الهاتف
   - العنوان
   - ساعات العمل (البداية)
   - ساعات العمل (النهاية)
   - اختر أيام الدوام
   - تأكيد البيانات
3. احصل على معرف الصالون والفترة التجريبية المجانية
4. اضغط `/owner` للدخول إلى لوحة التحكم
5. أضف الخدمات والموظفين

### لملاك صالون لترقية الاشتراك:

1. اضغط `/pay`
2. اختر طريقة الدفع (Zain Cash أو تحويل بنكي)
3. اختر الخطة
4. أرسل بيانات التحويل
5. قارن البيانات وأكد
6. انتظر موافقة المسؤول

### للمسؤول لموافقة الدفعات:

1. اضغط `/admin`
2. اختر "💰 الدفعات المعلقة"
3. اضغط ✅ للموافقة أو ❌ للرفض
4. سيتم تفعيل الاشتراك تلقائياً

---

## 🗄️ بنية قاعدة البيانات

```
tenants                    (الصالونات)
├── services              (الخدمات)
├── staff                 (الموظفين)
├── bookings              (الحجوزات)
├── customers             (العملاء)
├── payments              (الدفعات)
├── promo_codes           (أكواد الخصم)
├── subscription_history  (سجل الاشتراكات)
├── waiting_list          (قائمة الانتظار)
└── settings              (الإعدادات)
```

---

## 🔧 المتغيرات البيئية المهمة

```env
# التوكن
BOT_TOKEN=your_token

# الإدارة
ADMIN_ID=your_id

# قاعدة البيانات
DATABASE_URL=postgresql://user:pass@localhost/salon_booking
REDIS_URL=redis://localhost:6379/0

# البيئة
ENVIRONMENT=development|production
DEBUG=True|False

# الاشتراكات
TRIAL_DAYS=14

# التسجيل
LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
LOG_FILE=logs/app.log

# الويبهوك (للإنتاج)
WEBHOOK_URL=https://your-domain.com
WEBHOOK_PATH=/webhook

# JWT
JWT_SECRET=your_secret_key
```

---

## 📊 معلومات الخطط

| الميزة | تجريبية | أساسية | معيارية | احترافية | مدى الحياة |
|--------|---------|---------|---------|----------|-----------|
| السعر | مجاني | $9.99 | $19.99 | $49.99 | $999 |
| الموظفين | 1 | 1 | 5 | ∞ | ∞ |
| الحجوزات | 100 | 100 | 500 | ∞ | ∞ |
| التنبيهات | ❌ | ❌ | ✅ | ✅ | ✅ |
| التحليلات | ❌ | ✅ | ✅ | ✅ | ✅ |
| الفروع | ❌ | ❌ | ❌ | ✅ | ✅ |
| مدة الصلاحية | 14 يوم | شهرية | شهرية | شهرية | أبدي |

---

## 🚨 استكشاف الأخطاء

### البوت لا يستجيب

```bash
# تحقق من التوكن
python -c "from config import config; print(config.BOT_TOKEN)"

# تحقق من الأخطاء
tail -f logs/app.log

# أعد تشغيل البوت
python main.py
```

### خطأ في قاعدة البيانات

```bash
# اختبر الاتصال
psql -U salon_user -d salon_booking -h localhost

# أعد التهيئة
python -c "from database import init_db; init_db()"
```

### مشاكل Redis

```bash
# تحقق من الخدمة
redis-cli ping

# أعد التشغيل
sudo systemctl restart redis-server
```

---

## 🎓 أمثلة الاستخدام

### إضافة خدمة جديدة (كملاك صالون)

```
/owner → Manage Services → Add Service
اسم الخدمة: حلاقة شعر
السعر: $25
المدة: 30 دقيقة
```

### استخدام كود خصم

```
كود الخصم: SUMMER20
نوع الخصم: نسبة 20%
أو
كود الخصم: FLAT5
الخصم الثابت: $5
```

### تتبع العملاء

```
عدد الزيارات: 5
إجمالي الإنفاق: $125
الموظف المفضل: أحمد
ملاحظات: عميل مهم
```

---

## 📞 الدعم والمساعدة

- 📧 البريد الإلكتروني: support@salonbooking.com
- 💬 Telegram: @SalonBookingSupport
- 📚 الوثائق: README.md و DEPLOYMENT.md

---

## ✅ قائمة التحقق قبل الإنتاج

- [ ] تم تغيير BOT_TOKEN
- [ ] تم تغيير ADMIN_ID
- [ ] تم تغيير JWT_SECRET
- [ ] تم إعداد PostgreSQL
- [ ] تم إعداد Redis
- [ ] تم إعداد SSL/HTTPS
- [ ] تم إعداد النسخ الاحتياطية
- [ ] تم إعداد المراقبة
- [ ] تم اختبار جميع الميزات
- [ ] تم إعداد الويبهوك

---

**🎉 مبروك! نظامك الآن جاهز للاستخدام!**

للمزيد من المعلومات، راجع:
- **README.md** - الوثائق الكاملة
- **DEPLOYMENT.md** - نشر في الإنتاج
- **MONITORING.md** - مراقبة والتسجيل
- **DOCKER_DEPLOYMENT.md** - نشر باستخدام Docker
- **TOKEN_GUIDE.md** - دليل التوكن الآمن
