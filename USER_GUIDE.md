# 📚 دليل الاستخدام الشامل - RAG-ENTERPRISE

**الإصدار**: 2.1.0  
**التاريخ**: 12 نوفمبر 2025

---

## 🎯 مقدمة

RAG-ENTERPRISE هو نظام ذكاء اصطناعي متكامل يوفر:

| الميزة | الوصف |
|--------|-------|
| **Retrieval Augmented Generation** | استرجاع المعلومات وتوليد الإجابات الذكية |
| **معالجة المستندات** | دعم PDF, Word, Excel, نصوص وأكثر |
| **الوكلاء الذكيين** | وكلاء متخصصين (QA, Research, Finance) |
| **قاعدة معرفة عميقة** | متجر متجهات + رسوم بيانية + نص كامل |
| **واجهة احترافية** | Dashboard متقدمة مع إدارة شاملة |
| **أمان عالي** | JWT Authentication + RBAC + Multi-tenancy |

---

## 🌐 نقاط الوصول الرئيسية

```
🔗 API:       http://localhost:8000
📚 Docs:      http://localhost:8000/docs
🎨 Frontend:  http://localhost:3000
💼 Admin:     http://localhost:3000/admin
```

---

## 📖 جدول المحتويات

1. [الإعدادات الأساسية](#الإعدادات-الأساسية)
2. [المصادقة والتفويض](#المصادقة-والتفويض)
3. [إدارة المستندات](#إدارة-المستندات)
4. [استخدام الدردشة الذكية](#استخدام-الدردشة-الذكية)
5. [الوكلاء الذكيين](#الوكلاء-الذكيين)
6. [لوحة الإدارة](#لوحة-الإدارة)
7. [API Reference](#api-reference)
8. [استكشاف الأخطاء](#استكشاف-الأخطاء)

---

## 🔧 الإعدادات الأساسية

### ملف .env

```properties
# التطبيق
APP_NAME=RAG-ENTERPRISE
APP_VERSION=2.1.0
DEBUG=true

# قاعدة البيانات
DATABASE_URL=sqlite:///./data/rag_enterprise.db

# الأمان
SECRET_KEY=rag-enterprise-secret-key-change-this

# التخزين
STORAGE_PATH=/tmp/rag-enterprise/storage

# السجلات
LOG_LEVEL=INFO
```

### التخصيص

```bash
# تحرير الإعدادات
nano .env

# إضافة Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your.openai.azure.com

# إضافة Redis
REDIS_URL=redis://localhost:6379/0
```

---

## 🔐 المصادقة والتفويض

### التسجيل (إنشاء حساب جديد)

**الواجهة الرسومية**:
```
1. افتح http://localhost:3000
2. انقر على "Register"
3. أدخل البريد الإلكتروني وكلمة المرور
4. انقر "Sign Up"
```

**عبر API**:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "User Name"
  }'
```

**الاستجابة**:
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "User Name",
  "created_at": "2025-11-12T21:00:00Z"
}
```

### تسجيل الدخول

**الواجهة الرسومية**:
```
1. افتح http://localhost:3000/login
2. أدخل بريدك الإلكتروني
3. أدخل كلمة المرور
4. انقر "Login"
```

**عبر API**:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@admin.com",
    "password": "admin123"
  }'
```

**الاستجابة**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "admin_id",
    "email": "admin@admin.com",
    "full_name": "Admin User"
  }
}
```

### استخدام Token

```bash
# حفظ Token في متغير
TOKEN="your_access_token_here"

# استخدامه في الطلبات
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/auth/me
```

### تحديث Token

```bash
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token"
  }'
```

---

## 📄 إدارة المستندات

### رفع مستند

**الواجهة الرسومية**:
```
1. افتح Dashboard
2. انقر على "Upload Document"
3. اختر ملفك (PDF, Word, نص، إلخ)
4. اختر مجموعة البيانات
5. انقر "Upload"
```

**عبر API**:
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "dataset_id=dataset_123"
```

**الاستجابة**:
```json
{
  "id": "doc_123",
  "name": "document.pdf",
  "dataset_id": "dataset_123",
  "file_size": 102400,
  "status": "PENDING",
  "created_at": "2025-11-12T21:00:00Z",
  "message": "Document uploaded successfully. Processing..."
}
```

### استخراج المستندات

```bash
# الحصول على جميع المستندات
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/documents

# الحصول على مستند واحد
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/documents/doc_123

# تصفية بمجموعة بيانات
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/documents?dataset_id=dataset_123"

# التصفح
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/documents?skip=0&limit=10"
```

### البحث في المستندات

```bash
# البحث البسيط
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/documents/search?q=keyword"

# البحث المتقدم
curl -X POST "http://localhost:8000/documents/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ما هي أهم نقاط الوثيقة؟",
    "dataset_id": "dataset_123",
    "filters": {
      "status": "COMPLETED"
    },
    "top_k": 5
  }'
```

### حذف مستند

```bash
curl -X DELETE "http://localhost:8000/documents/doc_123" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 💬 استخدام الدردشة الذكية

### بدء محادثة جديدة

**الواجهة الرسومية**:
```
1. افتح http://localhost:3000/chat
2. انقر على "New Conversation"
3. اختر مجموعة البيانات
4. ابدأ بالكتابة
```

**عبر API**:
```bash
# إنشاء محادثة
curl -X POST "http://localhost:8000/conversations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "عنوان المحادثة",
    "dataset_id": "dataset_123"
  }'
```

**الاستجابة**:
```json
{
  "id": "conv_123",
  "title": "عنوان المحادثة",
  "dataset_id": "dataset_123",
  "created_at": "2025-11-12T21:00:00Z"
}
```

### إرسال رسالة

```bash
curl -X POST "http://localhost:8000/chat/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_123",
    "message": "اشرح لي محتوى الوثيقة",
    "use_context": true
  }'
```

**الاستجابة**:
```json
{
  "id": "msg_123",
  "conversation_id": "conv_123",
  "role": "assistant",
  "content": "بناءً على الوثيقة، النقاط الرئيسية هي...",
  "sources": [
    {
      "document_id": "doc_123",
      "document_name": "document.pdf",
      "segment_id": "seg_123",
      "relevance": 0.92
    }
  ],
  "created_at": "2025-11-12T21:00:00Z"
}
```

### WebSocket للدردشة المباشرة

```javascript
// في frontend
const ws = new WebSocket(
  `ws://localhost:8000/ws/chat/conv_123?token=${token}`
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('جواب:', data.content);
};

ws.send(JSON.stringify({
  message: "سؤالك هنا"
}));
```

### تقييم الرسائل

```bash
# تقييم إيجابي
curl -X POST "http://localhost:8000/messages/msg_123/feedback" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 1,
    "comment": "إجابة مفيدة جداً"
  }'

# تقييم سلبي
curl -X POST "http://localhost:8000/messages/msg_123/feedback" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": -1,
    "comment": "الإجابة غير دقيقة"
  }'
```

---

## 🤖 الوكلاء الذكيين

### استخدام QA Agent

```bash
curl -X POST "http://localhost:8000/agents/qa/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "ما هو موضوع الوثيقة الرئيسي؟",
    "dataset_id": "dataset_123",
    "context_limit": 5
  }'
```

### استخدام Research Agent

```bash
curl -X POST "http://localhost:8000/agents/researcher/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "موضوع البحث",
    "depth": "high",
    "sources": ["dataset_123", "dataset_456"]
  }'
```

### استخدام Financial Agent

```bash
curl -X POST "http://localhost:8000/agents/financial/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "risk",
    "report_id": "doc_123",
    "parameters": {
      "risk_level": "high"
    }
  }'
```

---

## 👨‍💼 لوحة الإدارة

### لوحة القيادة

**الوصول**: http://localhost:3000/admin

**يعرض**:
- إحصائيات النظام
- عدد المستخدمين والمستندات
- النشاط الأخير
- الأداء والموارد

### إدارة التطبيقات

```bash
# الحصول على جميع التطبيقات
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/apps

# إنشاء تطبيق جديد
curl -X POST "http://localhost:8000/admin/apps" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "اسم التطبيق",
    "description": "الوصف",
    "type": "chat"
  }'

# تحديث التطبيق
curl -X PUT "http://localhost:8000/admin/apps/app_123" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "اسم جديد"
  }'

# حذف التطبيق
curl -X DELETE "http://localhost:8000/admin/apps/app_123" \
  -H "Authorization: Bearer $TOKEN"
```

### إدارة مجموعات البيانات

```bash
# الحصول على جميع المجموعات
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/datasets

# إنشاء مجموعة جديدة
curl -X POST "http://localhost:8000/admin/datasets" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "اسم المجموعة",
    "description": "الوصف",
    "category": "finance"
  }'
```

### إدارة المستخدمين

```bash
# الحصول على جميع المستخدمين
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/users

# إضافة مستخدم جديد
curl -X POST "http://localhost:8000/admin/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "full_name": "اسم المستخدم",
    "role": "analyst"
  }'

# تحديث الدور
curl -X PUT "http://localhost:8000/admin/users/user_123/role" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "admin"
  }'
```

---

## 📊 API Reference

### Authentication Endpoints

| الطلب | المسار | الوصف |
|------|--------|-------|
| POST | `/auth/register` | تسجيل حساب جديد |
| POST | `/auth/login` | تسجيل الدخول |
| POST | `/auth/refresh` | تحديث Token |
| GET | `/auth/me` | بيانات المستخدم الحالي |
| POST | `/auth/logout` | تسجيل الخروج |

### Document Endpoints

| الطلب | المسار | الوصف |
|------|--------|-------|
| POST | `/documents/upload` | رفع مستند |
| GET | `/documents` | قائمة المستندات |
| GET | `/documents/{id}` | تفاصيل مستند |
| DELETE | `/documents/{id}` | حذف مستند |
| GET | `/documents/search` | البحث |

### Chat Endpoints

| الطلب | المسار | الوصف |
|------|--------|-------|
| POST | `/conversations` | إنشاء محادثة |
| GET | `/conversations` | قائمة المحادثات |
| GET | `/conversations/{id}` | تفاصيل محادثة |
| POST | `/chat/message` | إرسال رسالة |
| WS | `/ws/chat/{id}` | WebSocket للدردشة |

### Admin Endpoints

| الطلب | المسار | الوصف |
|------|--------|-------|
| GET | `/admin/apps` | قائمة التطبيقات |
| POST | `/admin/apps` | إنشاء تطبيق |
| GET | `/admin/datasets` | قائمة المجموعات |
| POST | `/admin/datasets` | إنشاء مجموعة |
| GET | `/admin/users` | قائمة المستخدمين |
| GET | `/admin/workspace` | معلومات مساحة العمل |

---

## 🐛 استكشاف الأخطاء

### خطأ: "Invalid credentials"

```bash
# تحقق من بيانات المستخدم
# استخدم بيانات افتراضية:
# البريد: admin@admin.com
# كلمة المرور: admin123

# إعادة تعيين كلمة المرور:
python -c "
from api.models.user import User
from core.auth import AuthService
from api.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter_by(email='admin@admin.com').first()
user.password_hash = AuthService.get_password_hash('admin123')
db.commit()
print('✓ Password reset')
"
```

### خطأ: "Token expired"

```bash
# استخدم refresh token للحصول على token جديد
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token"
  }'
```

### خطأ: "Document processing failed"

```bash
# تحقق من السجلات
tail -f api.log

# تحقق من صيغة الملف
file document.pdf

# جرب ملف مختلف
```

### خطأ: "Database connection failed"

```bash
# تحقق من الاتصال
python -c "from api.database import check_database_health; print(check_database_health())"

# أعد التهيئة
rm rag_enterprise.db*
python api/init_db.py
```

---

## 💡 نصائح للاستخدام الأفضل

### 1. استخدم مجموعات بيانات منفصلة

```
- Marketing: للوثائق التسويقية
- Financial: للتقارير المالية
- Technical: للوثائق التقنية
```

### 2. استخدم الفلترة للبحث الدقيق

```bash
curl "http://localhost:8000/documents/search?q=keyword&dataset_id=dataset_123&status=COMPLETED"
```

### 3. استخدم Context Limit لتحسين الأداء

```bash
curl -X POST "http://localhost:8000/chat/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "سؤالك",
    "context_limit": 3
  }'
```

### 4. راقب الأداء

```bash
# عرض الإحصائيات
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/analytics/usage
```

### 5. احفظ المحادثات المهمة

```bash
# استخدم الـ Frontend لوضع علامات
```

---

## 🎓 أمثلة عملية

### مثال 1: تحليل وثيقة مالية

```bash
# 1. رفع الوثيقة
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@financial_report.pdf" \
  -F "dataset_id=financial_dataset"

# 2. انتظر المعالجة (30 ثانية)

# 3. اطرح أسئلة
curl -X POST "http://localhost:8000/chat/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_123",
    "message": "ما هو صافي الربح؟"
  }'

# 4. استخدم Financial Agent
curl -X POST "http://localhost:8000/agents/financial/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "profitability",
    "report_id": "doc_123"
  }'
```

### مثال 2: بحث شامل متعدد الوثائق

```bash
# 1. أنشئ مجموعة بحث
curl -X POST "http://localhost:8000/agents/researcher/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "تأثير التكنولوجيا على الأعمال",
    "depth": "high",
    "sources": ["dataset_1", "dataset_2", "dataset_3"]
  }'

# 2. اجمع النتائج
```

### مثال 3: بناء Chatbot مخصص

```bash
# 1. أنشأ تطبيق
curl -X POST "http://localhost:8000/admin/apps" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support Bot",
    "description": "Bot لخدمة العملاء",
    "type": "chat",
    "dataset_id": "support_docs"
  }'

# 2. دع المستخدمين يستخدمونه
```

---

## 📞 الدعم والمساعدة

### الملفات المرجعية:
- `COMPREHENSIVE_ANALYSIS.md` - التحليل الشامل
- `QUICK_START.md` - البدء السريع
- `DEVELOPMENT_ROADMAP.md` - خطة التطوير

### الاتصال:
- 📧 البريد الإلكتروني
- 💬 Slack
- 📞 الهاتف

---

**آخر تحديث**: 12 نوفمبر 2025  
**الإصدار**: 2.1.0
