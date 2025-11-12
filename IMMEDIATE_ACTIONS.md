# 🎯 خطوات البدء الفورية

**التاريخ**: 12 نوفمبر 2025  
**المدة المتوقعة**: 30 دقيقة للتشغيل الكامل

---

## ✅ الخطوة 1: التحقق من البيئة (2 دقيقة)

```bash
cd /workspaces/RAG-ENTERPRISE

# التحقق من Python
python --version  
# النتيجة المتوقعة: Python 3.12.1

# التحقق من Node.js
node --version  
# النتيجة المتوقعة: v22.20.0

# التحقق من Virtual Environment
source venv/bin/activate
which python
# النتيجة المتوقعة: /workspaces/RAG-ENTERPRISE/venv/bin/python
```

---

## ✅ الخطوة 2: التحقق من المكتبات (2 دقيقة)

```bash
# التحقق من المكتبات الأساسية
python -c "import fastapi, sqlalchemy, pydantic; print('✓ All libraries OK')"

# إذا كان هناك خطأ:
pip install -r requirements.txt --upgrade
```

---

## ✅ الخطوة 3: فحص قاعدة البيانات (2 دقيقة)

```bash
# فحص الاتصال
python -c "
from api.database import check_database_health
import json
print(json.dumps(check_database_health(), indent=2))
"

# إذا كانت قاعدة البيانات غير متاحة:
rm rag_enterprise.db* 2>/dev/null
python api/init_db.py
```

---

## ✅ الخطوة 4: بدء Backend (5 دقائق)

### الخيار A: استخدام Script (الأفضل)
```bash
./start_api.sh
# ستشاهد: API started (PID: XXXXX)
```

### الخيار B: المباشر
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### اختبار التشغيل
```bash
# في نافذة جديدة:
curl http://localhost:8000/

# يجب أن ترى:
# {"name":"RAG-ENTERPRISE API","version":"2.1.0","status":"running"}

# فحص الصحة:
curl http://localhost:8000/health/health | python -m json.tool
```

---

## ✅ الخطوة 5: بدء Frontend (10 دقائق)

### في نافذة جديدة:

```bash
cd frontend

# التثبيت (المرة الأولى فقط)
npm install

# بدء التطوير
npm run dev
```

### اختبار التشغيل
```bash
# في متصفح:
# http://localhost:3000
# يجب أن ترى: صفحة تسجيل الدخول
```

---

## ✅ الخطوة 6: اختبار المصادقة (5 دقائق)

```bash
# الحصول على Token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.com",
    "password": "admin123"
  }' | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"

# استخدام Token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/auth/me | python -m json.tool
```

---

## 🎯 اختبارات سريعة

### 1. اختبار API الصحة

```bash
curl -s http://localhost:8000/health/health | python -m json.tool
```

**النتيجة المتوقعة**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T21:12:06.331096",
  "version": "2.1.0",
  "database": {
    "status": "healthy",
    "connection": "connected"
  }
}
```

### 2. اختبار المصادقة

```bash
# تسجيل الدخول
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.com",
    "password": "admin123"
  }' | python -m json.tool
```

**النتيجة المتوقعة**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. اختبار جلب المستندات

```bash
TOKEN="your_token_here"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/documents | python -m json.tool
```

---

## 📊 استخدام Postman أو Insomnia

### 1. استيراد OpenAPI Schema

```bash
# الحصول على OpenAPI Schema
curl http://localhost:8000/openapi.json > openapi.json

# استيراده في Postman/Insomnia
```

### 2. المتغيرات المهمة

```
BASE_URL: http://localhost:8000
TOKEN: {قيمة JWT من تسجيل الدخول}
DATASET_ID: {معرف مجموعة بيانات}
DOCUMENT_ID: {معرف مستند}
```

---

## 🚨 استكشاف الأخطاء

### Backend لا يبدأ

```bash
# 1. تحقق من الأخطاء
python api/main.py

# 2. تحقق من السجل
tail -f api.log

# 3. تحقق من المنفذ
lsof -i :8000
# إذا كان مستخدماً:
kill -9 <PID>
```

### Database Error

```bash
# 1. تحقق من الاتصال
python -c "from api.database import check_database_health; print(check_database_health())"

# 2. أعد التهيئة
rm rag_enterprise.db* 2>/dev/null
python api/init_db.py

# 3. شغل الهجرات
alembic upgrade head
```

### Frontend لا يبدأ

```bash
# 1. تحقق من المشاكل
cd frontend
npm list

# 2. أعد التثبيت
rm -rf node_modules package-lock.json
npm install

# 3. امسح الـ Cache
npm cache clean --force
npm run dev
```

### CORS Error

```bash
# هذا طبيعي في البداية
# تحقق من .env:
cat .env | grep CORS

# الحل المؤقت: استخدم curl أو Postman بدلاً من المتصفح
```

---

## 📁 ملفات مهمة للمراجعة

```
✅ COMPREHENSIVE_ANALYSIS.md     - تحليل شامل للمشروع
✅ QUICK_START.md                - دليل البدء السريع
✅ DEVELOPMENT_ROADMAP.md        - خطة التطوير المتكاملة
✅ .env                          - إعدادات البيئة
✅ docker-compose.yml            - تشكيل Docker
✅ requirements.txt              - المتطلبات
```

---

## 🎬 الخطوات التالية بعد التشغيل

### الأولويات الفورية:

1. **رفع مستند تجريبي**
   ```bash
   # استخدم الـ Frontend أو:
   curl -X POST "http://localhost:8000/documents/upload" \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@test_document.pdf" \
     -F "dataset_id=YOUR_DATASET_ID"
   ```

2. **معالجة المستند**
   - تحقق من رسائل السجل
   - اختبر استخراج النص

3. **اختبار البحث**
   ```bash
   curl "http://localhost:8000/documents/search?q=keyword" \
     -H "Authorization: Bearer $TOKEN"
   ```

4. **دردشة مع Chatbot**
   - استخدم الـ Frontend
   - اختبر الإجابات

---

## 📞 الدعم السريع

### أسئلة شائعة:

**س: كيف أغير كلمة المرور؟**
```bash
# في قاعدة البيانات:
sqlite3 rag_enterprise.db "UPDATE user SET password_hash='...' WHERE email='admin@admin.com';"
# أفضل: استخدم API
```

**س: كيف أضيف مستخدم جديد؟**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "full_name": "New User"
  }'
```

**س: كيف أحذف مستند؟**
```bash
curl -X DELETE "http://localhost:8000/documents/{document_id}" \
  -H "Authorization: Bearer $TOKEN"
```

**س: كيف أعيد تعيين قاعدة البيانات؟**
```bash
rm rag_enterprise.db* 2>/dev/null
python api/init_db.py
# ستفقد جميع البيانات!
```

---

## ⏱️ الجدول الزمني المقترح

```
الآن (15 دقيقة):
├── ✅ قراءة هذا الملف
├── ✅ بدء Backend
└── ✅ بدء Frontend

الساعة التالية (30 دقيقة):
├── اختبار المصادقة
├── اختبار رفع مستند
├── اختبار البحث
└── استكشاف الواجهة

اليوم (2-3 ساعات):
├── قراءة COMPREHENSIVE_ANALYSIS.md
├── قراءة DEVELOPMENT_ROADMAP.md
├── تشغيل الاختبارات
└── اختبار جميع المميزات

هذا الأسبوع:
├── بدء تحسينات معالجة المستندات
├── إضافة اختبارات شاملة
└── توثيق التعديلات
```

---

## ✨ نصائح مهمة

### 1. استخدم Virtual Environment دائماً

```bash
source venv/bin/activate
# تأكد من أن الـ prompt يحتوي على (venv)
```

### 2. احفظ Token في متغير

```bash
export RAG_TOKEN="your_token_here"
curl -H "Authorization: Bearer $RAG_TOKEN" ...
```

### 3. استخدم jq لتنسيق JSON

```bash
curl ... | jq .
```

### 4. راقب السجلات

```bash
# في terminal منفصل:
tail -f api.log
tail -f frontend_logs.txt
```

### 5. استخدم Git للتحكم بالتغييرات

```bash
git status
git add .
git commit -m "وصف التغييرات"
```

---

## 🎉 تم! أنت جاهز!

**الخطوة التالية**: افتح المتصفح وادخل إلى `http://localhost:3000`

**استمتع بالتطوير!** 🚀

---

**إذا واجهت أي مشاكل**, اقرأ:
- `COMPREHENSIVE_ANALYSIS.md` - للتفاصيل
- `QUICK_START.md` - للمزيد من الأوامر
- `DEVELOPMENT_ROADMAP.md` - لخطة التطوير
