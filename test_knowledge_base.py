# test_knowledge_base.py
"""اختبار نظام قاعدة المعرفة"""

import asyncio

print("=" * 60)
print("🧪 اختبار نظام قاعدة المعرفة")
print("=" * 60)

from knowledge_base.vector_store.embeddings import EmbeddingsGenerator
from knowledge_base.vector_store.memory_store import MemoryVectorStore
from knowledge_base.retrieval.hybrid_search import HybridSearchEngine

async def main():
    # 1. إنشاء المكونات
    print("\n1️⃣ إنشاء المكونات...")
    embeddings = EmbeddingsGenerator()
    vector_store = MemoryVectorStore()
    search_engine = HybridSearchEngine(embeddings, vector_store)
    print("✅ تم إنشاء جميع المكونات")
    
    # 2. إضافة مستندات تجريبية
    print("\n2️⃣ إضافة مستندات تجريبية...")
    
    test_docs = [
        {
            "id": "doc1",
            "content": "الذكاء الاصطناعي هو فرع من علوم الحاسوب يهتم بإنشاء أنظمة ذكية قادرة على التعلم.",
            "metadata": {"type": "general", "language": "ar"}
        },
        {
            "id": "doc2",
            "content": "تطبيقات الذكاء الاصطناعي متعددة في مجالات الطب والتعليم والصناعة.",
            "metadata": {"type": "general", "language": "ar"}
        },
        {
            "id": "doc3",
            "content": "Machine Learning is a subset of AI that focuses on learning from data.",
            "metadata": {"type": "general", "language": "en"}
        },
        {
            "id": "doc4",
            "content": "التقارير المالية توضح الأداء المالي للشركات خلال فترة محددة.",
            "metadata": {"type": "financial", "language": "ar"}
        }
    ]
    
    # توليد embeddings وإضافة المستندات
    for doc in test_docs:
        embedding = await embeddings.generate(doc["content"])
        await vector_store.add_document(
            doc_id=doc["id"],
            content=doc["content"],
            embedding=embedding,
            metadata=doc["metadata"]
        )
    
    print(f"✅ تم إضافة {len(test_docs)} مستندات")
    
    # 3. عرض إحصائيات
    print("\n3️⃣ إحصائيات المخزن:")
    stats = vector_store.get_stats()
    print(f"   إجمالي المستندات: {stats['total_documents']}")
    for idx, count in stats['indexes'].items():
        print(f"   {idx}: {count} مستندات")
    
    # 4. اختبار البحث
    print("\n4️⃣ اختبار البحث...")
    
    queries = [
        "ما هو الذكاء الاصطناعي؟",
        "التطبيقات في الطب",
        "Machine Learning",
        "التقارير المالية"
    ]
    
    for query in queries:
        print(f"\n🔍 الاستعلام: '{query}'")
        
        results = await search_engine.search(
            query=query,
            top_k=2,
            index_name="general"
        )
        
        print(f"   عدد النتائج: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"\n   نتيجة {i}:")
            print(f"      المعرف: {result['id']}")
            print(f"      الدرجة: {result['combined_score']:.3f}")
            print(f"      نوع البحث: {result.get('search_types', [])}")
            print(f"      المحتوى: {result['content'][:80]}...")
    
    # 5. اختبار التشابه
    print("\n\n5️⃣ اختبار التشابه بين Embeddings...")
    
    text1 = "الذكاء الاصطناعي"
    text2 = "الذكاء الاصطناعي والتعلم الآلي"
    text3 = "التقارير المالية"
    
    emb1 = await embeddings.generate(text1)
    emb2 = await embeddings.generate(text2)
    emb3 = await embeddings.generate(text3)
    
    sim_1_2 = embeddings.cosine_similarity(emb1, emb2)
    sim_1_3 = embeddings.cosine_similarity(emb1, emb3)
    
    print(f"   التشابه بين '{text1}' و '{text2}': {sim_1_2:.3f}")
    print(f"   التشابه بين '{text1}' و '{text3}': {sim_1_3:.3f}")
    
    print("\n" + "=" * 60)
    print("🎉 جميع الاختبارات نجحت!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())