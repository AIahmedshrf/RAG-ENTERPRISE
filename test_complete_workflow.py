# test_complete_workflow.py
"""اختبار سير العمل الكامل: رفع → فهرسة → محادثة"""

import asyncio
import httpx
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

async def test_complete_workflow():
    print("=" * 70)
    print("🧪 اختبار سير العمل الكامل")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        # 1. إنشاء ملف تجريبي
        print("\n1️⃣ إنشاء ملف تجريبي...")
        test_file = Path("test_ai_document.txt")
        test_file.write_text("""
الذكاء الاصطناعي وتطبيقاته

الذكاء الاصطناعي هو فرع من علوم الحاسوب يهتم بإنشاء أنظمة ذكية قادرة على التعلم والتكيف.

التطبيقات الرئيسية:
- الطب: تشخيص الأمراض وتحليل الصور الطبية
- التعليم: أنظمة تعليمية ذكية ومخصصة
- الصناعة: الأتمتة والروبوتات الذكية
- الخدمات المالية: تحليل البيانات واكتشاف الاحتيال

التحديات:
يواجه الذكاء الاصطناعي تحديات أخلاقية وتقنية مثل الخصوصية والتحيز في البيانات.
        """, encoding='utf-8')
        print(f"✅ تم إنشاء: {test_file}")
        
        # 2. رفع وفهرسة المستند
        print("\n2️⃣ رفع وفهرسة المستند...")
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'text/plain')}
            data = {'language': 'ar', 'index_name': 'general'}
            
            response = await client.post(
                f"{BASE_URL}/documents/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ رفع ناجح:")
            print(f"   المعرف: {result['document']['id']}")
            print(f"   القطع: {result['document']['chunks_count']}")
            print(f"   المفهرسة: {result['indexing']['chunks_indexed']}")
            print(f"   الحالة: {result['indexing']['status']}")
        else:
            print(f"❌ فشل الرفع: {response.text}")
            return
        
        # 3. التحقق من الإحصائيات
        print("\n3️⃣ التحقق من إحصائيات المخزن...")
        response = await client.get(f"{BASE_URL}/documents/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ إحصائيات المخزن:")
            print(f"   إجمالي المستندات: {stats['vector_store']['total_documents']}")
            print(f"   الفهارس: {stats['vector_store']['indexes']}")
        
        # 4. اختبار المحادثة مع البحث
        print("\n4️⃣ اختبار المحادثة مع البحث...")
        
        queries = [
            "ما هي تطبيقات الذكاء الاصطناعي في الطب؟",
            "ما هي التحديات التي تواجه الذكاء الاصطناعي؟",
            "اذكر مجالات استخدام الذكاء الاصطناعي"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n   📝 سؤال {i}: {query}")
            
            response = await client.post(
                f"{BASE_URL}/chat/message",
                json={
                    "query": query,
                    "use_search": True,
                    "top_k": 3,
                    "agent": "researcher"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ الإجابة: {result['answer'][:200]}...")
                print(f"   📚 المصادر: {result['total_sources']}")
                if result.get('sources'):
                    for src in result['sources'][:2]:
                        print(f"      - {src['id']} (درجة: {src['score']:.3f})")
            else:
                print(f"   ❌ فشل: {response.text}")
        
        # 5. اختبار قائمة الوكلاء
        print("\n5️⃣ قائمة الوكلاء...")
        response = await client.get(f"{BASE_URL}/chat/agents")
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ الوكلاء المتاحين:")
            for agent in agents['agents']:
                print(f"   - {agent['name']}: {agent['stats']}")
        
        # تنظيف
        test_file.unlink()
        print("\n" + "=" * 70)
        print("🎉 اكتمل الاختبار!")
        print("=" * 70)

if __name__ == "__main__":
    print("\n⚠️  تأكد من تشغيل السيرفر أولاً:")
    print("   uvicorn api.main:app --reload\n")
    
    asyncio.run(test_complete_workflow())