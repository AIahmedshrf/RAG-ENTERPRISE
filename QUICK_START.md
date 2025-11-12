# 🚀 دليل البدء السريع - RAG-ENTERPRISE

## ✅ الحالة الحالية

- **Backend**: ✅ يعمل على `localhost:8000`
- **Database**: ✅ متصل وصحي
- **Python**: ✅ 3.12.1
- **Node.js**: ✅ v22.20.0

---

## 📋 المتطلبات الأساسية

```bash
# نظام التشغيل: Ubuntu 24.04.3 LTS
# Python: 3.12.1
# Node.js: v22.20.0
# Docker: متاح (اختياري)
```

---

## 🔧 خطوات البدء (في المجلد الرئيسي)

### 1️⃣ تفعيل البيئة الافتراضية

```bash
cd /workspaces/RAG-ENTERPRISE
source venv/bin/activate
```

### 2️⃣ تحديث المتطلبات (اختياري)

```bash
pip install -r requirements.txt
```

### 3️⃣ تشغيل الـ Backend

**الخيار الأول: استخدام Script**
```bash
./start_api.sh
```

**الخيار الثاني: التشغيل المباشر**
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**الخيار الثالث: في Background**
```bash
nohup uvicorn api.main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
```

### 4️⃣ تشغيل الـ Frontend (في نافذة جديدة)

```bash
cd frontend
npm install  # في المرة الأولى فقط
npm run dev
```

---

## 🌐 الوصول إلى التطبيق

### API Documentation
```
📘 http://localhost:8000/docs         (Swagger UI)
📗 http://localhost:8000/redoc        (ReDoc)
🔗 http://localhost:8000/openapi.json (OpenAPI Schema)
```

### API Health Check
```
curl http://localhost:8000/health/health
```

### Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "url": "./rag_enterprise.db"
}
```

### Frontend
```
🎨 http://localhost:3000              (تطبيق المستخدم)
👨‍💼 http://localhost:3000/admin       (لوحة الإدارة)
```

---

## 🔑 بيانات دخول تجريبية

### Admin User
- **البريد**: `admin@admin.com`
- **كلمة المرور**: `admin123` (أو حسب الإعدادات)

### Test User
- **البريد**: `user@demo.com`
- **كلمة المرور**: `demo123`

---

## 📊 اختبار API

### 1. تسجيل الدخول والحصول على JWT Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.com",
    "password": "admin123"
  }'
```

**النتيجة**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. الحصول على معلومات المستخدم الحالي

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. رفع مستند

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/file.pdf" \
  -F "dataset_id=YOUR_DATASET_ID"
```

### 4. الحصول على قائمة المستندات

```bash
curl -X GET "http://localhost:8000/documents" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. البحث في المستندات

```bash
curl -X GET "http://localhost:8000/documents/search?q=keyword" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🗄️ إدارة قاعدة البيانات

### فحص صحة قاعدة البيانات

```bash
source venv/bin/activate
python -c "from api.database import check_database_health; print(check_database_health())"
```

### تشغيل Migrations

```bash
alembic upgrade head
```

### إنشاء Migration جديد

```bash
alembic revision --autogenerate -m "تحديث الجداول"
```

### إعادة تعيين قاعدة البيانات (حذر!)

```bash
rm rag_enterprise.db*
python api/init_db.py
```

---

## 📦 رفع مستندات وملفات

### الملفات المدعومة
- PDF (`.pdf`)
- Word (`.docx`, `.doc`)
- نصوص (`.txt`, `.md`)
- Excel (`.csv`, `.xlsx`)
- JSON (`.json`)

### الحد الأقصى لحجم الملف: 10 MB

### مثال على الرفع باستخدام Python

```python
import requests

headers = {
    "Authorization": f"Bearer {access_token}"
}

files = {
    "file": open("document.pdf", "rb"),
}

data = {
    "dataset_id": "your-dataset-id"
}

response = requests.post(
    "http://localhost:8000/documents/upload",
    headers=headers,
    files=files,
    data=data
)

print(response.json())
```

---

## 🧪 الاختبارات

### تشغيل جميع الاختبارات

```bash
pytest
```

### تشغيل اختبارات معينة

```bash
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v
```

### مع تقرير التغطية

```bash
pytest --cov=. --cov-report=html
```

---

## 📋 تشغيل خط أنابيب المعالجة

### معالجة مستند واحد

```bash
python -c "
from document_processing.processors.base_processor import process_document
from api.database import SessionLocal

db = SessionLocal()
result = process_document('doc-id', '/path/to/file.pdf', '.pdf', db)
print(result)
"
```

### معالجة مجموعة كاملة

```bash
python scripts/process_dataset.py --dataset-id=YOUR_DATASET_ID
```

---

## 🤖 استخدام الوكلاء الذكيين

### 1. QA Agent (الأسئلة والأجوبة)

```python
from agents.general.qa_agent import QAAgent
from api.database import SessionLocal

agent = QAAgent()
db = SessionLocal()

result = await agent.execute({
    "question": "ما هو موضوع الوثيقة؟",
    "dataset_id": "your-dataset-id",
    "db": db
})

print(result)
```

### 2. Research Agent (البحث)

```python
from agents.general.researcher_agent import ResearcherAgent

agent = ResearcherAgent()

result = await agent.execute({
    "topic": "موضوع البحث",
    "depth": "high"
})

print(result)
```

### 3. Financial Agent (التحليل المالي)

```python
from agents.financial.financial_analyst_agent import FinancialAnalystAgent

agent = FinancialAnalystAgent()

result = await agent.execute({
    "report": "financial_data.pdf",
    "analysis_type": "risk"
})

print(result)
```

---

## 🔍 استخدام نظام RAG

### البحث المتقدم

```bash
curl -X POST "http://localhost:8000/chat/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ما هي أهم نقاط الوثيقة؟",
    "dataset_id": "your-dataset-id",
    "top_k": 5
  }'
```

### الدردشة مع Context

```bash
curl -X POST "http://localhost:8000/chat/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "اشرح لي...",
    "conversation_id": "your-conversation-id",
    "dataset_id": "your-dataset-id"
  }'
```

---

## 🐳 النشر باستخدام Docker (اختياري)

### البناء والتشغيل

```bash
docker-compose up -d
```

### التحقق من السجلات

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### الإيقاف

```bash
docker-compose down
```

---

## 🛠️ استكشاف الأخطاء

### المشكلة: Backend لا يبدأ

```bash
# 1. تحقق من الملف
ls -la api/main.py

# 2. تحقق من الأخطاء
python api/main.py

# 3. تحقق من السجل
cat api.log
```

### المشكلة: خطأ في قاعدة البيانات

```bash
# 1. تحقق من الاتصال
python -c "from api.database import check_database_health; print(check_database_health())"

# 2. أعد تهيئة قاعدة البيانات
rm rag_enterprise.db*
python api/init_db.py

# 3. شغّل الهجرات
alembic upgrade head
```

### المشكلة: خطأ في Frontend

```bash
# 1. تحقق من المتطلبات
cd frontend && npm list

# 2. أعد التثبيت
rm -rf node_modules package-lock.json
npm install

# 3. امسح الـ Cache
npm cache clean --force
```

### المشكلة: CORS Errors

```bash
# تحقق من .env
cat .env | grep CORS

# يمكنك تعديل main.py مؤقتاً
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # في التطوير فقط
# )
```

---

## 📈 المراقبة والسجلات

### عرض السجلات في الوقت الفعلي

```bash
# Backend
tail -f api.log

# Frontend (في مجلد frontend)
npm run dev  # يعرض السجلات مباشرة
```

### إحصائيات الخادم

```bash
# استهلاك الموارد
top

# عمليات Python
ps aux | grep python

# منافذ مفتوحة
netstat -tuln | grep -E "3000|8000|5432|6379"
```

---

## 🎯 الخطوات التالية

بعد التشغيل الناجح:

1. ✅ **اختبر API**: تسجيل الدخول والحصول على Token
2. ✅ **رفع مستند**: جرب رفع ملف PDF أو Word
3. ✅ **معالجة المستند**: تحقق من التقسيم والاستخراج
4. ✅ **البحث المتقدم**: اختبر البحث في المستندات
5. ✅ **الدردشة الذكية**: جرب Chatbot مع RAG
6. ✅ **لوحة الإدارة**: استكشف إحصائيات النظام

---

## 📞 الحصول على المساعدة

### المشاكل الشائعة والحلول

تراجع الملف الشامل:
```bash
cat COMPREHENSIVE_ANALYSIS.md
```

### معلومات إضافية

- قاعدة البيانات: `rag_enterprise.db`
- السجلات: `api.log`
- التوثيق: `docs/`
- الاختبارات: `tests/`

---

## ✨ نصائح للتطوير

### استخدام Virtual Environment بشكل صحيح

```bash
# التفعيل
source venv/bin/activate

# إضافة مكتبات جديدة
pip install package-name

# تحديث requirements
pip freeze > requirements.txt
```

### تنسيق الكود

```bash
# استخدام black
black .

# التحقق من flake8
flake8 .

# ترتيب الـ imports
isort .
```

### نوع التحقق (Type Checking)

```bash
# استخدام mypy
mypy .
```

---

## 🎉 تم! أنت الآن جاهز للبدء!

استمتع بتطوير RAG-ENTERPRISE! 🚀

---

**آخر تحديث**: 12 نوفمبر 2025
