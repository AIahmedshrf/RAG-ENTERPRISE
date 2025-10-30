# RAG-ENTERPRISE Frontend

واجهة المستخدم لنظام RAG-ENTERPRISE.

## التقنيات المستخدمة

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Radix UI
- Zustand

## التشغيل

```bash
# تثبيت المتطلبات
npm install

# التشغيل في وضع التطوير
npm run dev

# البناء للإنتاج
npm run build

# التشغيل في وضع الإنتاج
npm start

#البنية
app/
├─ components/     # المكونات القابلة لإعادة الاستخدام
├─ lib/           # المكتبات والأدوات
├─ styles/        # ملفات الأنماط
└─ (app)/         # الصفحات الرئيسية


الاتصال بالـ Backend

Backend API: http://localhost:8000

يتم تكوينه في .env.local

# تشغيل Backend (في terminal آخر)
cd /workspaces/RAG-ENTERPRISE
source venv/bin/activate
uvicorn api.main:app --reload