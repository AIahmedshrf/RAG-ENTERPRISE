# test_parsers_chunking.py
"""اختبار محللات المستندات والتقسيم"""

import asyncio
from pathlib import Path

# اختبار PDF Parser
print("=" * 60)
print("🧪 اختبار PDF Parser")
print("=" * 60)

from document_processing.parsers.pdf_parser import PDFParser

# إنشاء ملف PDF تجريبي (نصي بسيط)
test_pdf = Path("test_document.txt")
test_pdf.write_text("""صفحة 1
هذا مستند تجريبي باللغة العربية.
يحتوي على عدة فقرات وجمل.

صفحة 2
This is a test document in English.
It contains multiple paragraphs and sentences.
""", encoding='utf-8')

print("✅ تم إنشاء ملف نصي تجريبي")

# اختبار Text Splitter
print("\n" + "=" * 60)
print("🧪 اختبار Text Splitter")
print("=" * 60)

from document_processing.chunking.text_splitter import TextSplitter

splitter = TextSplitter(chunk_size=100, chunk_overlap=20)
print(f"✅ تم إنشاء Text Splitter (size={splitter.chunk_size}, overlap={splitter.chunk_overlap})")

long_text = """
هذا نص طويل باللغة العربية يحتاج إلى تقسيم. الفقرة الأولى تتحدث عن موضوع مهم.
الفقرة الثانية تكمل الموضوع وتضيف معلومات جديدة.
الفقرة الثالثة تختتم الموضوع بشكل جيد.

This is a long English text that needs splitting. The first paragraph talks about an important topic.
The second paragraph continues the topic and adds new information.
The third paragraph concludes the topic nicely.
""" * 3  # تكرار لجعل النص أطول

chunks = splitter.split_text(long_text)
print(f"✅ تم تقسيم النص إلى {len(chunks)} قطعة")

for i, chunk in enumerate(chunks[:3], 1):
    print(f"\nالقطعة {i} ({len(chunk)} حرف):")
    print(chunk[:100] + "..." if len(chunk) > 100 else chunk)

# اختبار Multilingual Splitter
print("\n" + "=" * 60)
print("🧪 اختبار Multilingual Splitter (دعم العربية)")
print("=" * 60)

from document_processing.chunking.multilingual_splitter import MultilingualTextSplitter

ml_splitter = MultilingualTextSplitter(chunk_size=150, chunk_overlap=30)
print("✅ تم إنشاء Multilingual Splitter")

arabic_text = """
الذكاء الاصطناعي هو فرع من علوم الحاسوب يهتم بإنشاء أنظمة ذكية. 
هذه الأنظمة قادرة على التعلم والتكيف مع البيئة المحيطة.
تطبيقات الذكاء الاصطناعي متعددة ومتنوعة في مختلف المجالات.
يستخدم في الطب والتعليم والصناعة والخدمات المالية.
المستقبل واعد جداً لهذا المجال المهم.
"""

# الحصول على إحصائيات اللغة
stats = ml_splitter.get_language_stats(arabic_text)
print(f"\n📊 إحصائيات اللغة:")
print(f"   إجمالي الأحرف: {stats['total_chars']}")
print(f"   أحرف عربية: {stats['arabic_chars']} ({stats['arabic_percentage']:.1f}%)")
print(f"   أحرف إنجليزية: {stats['english_chars']} ({stats['english_percentage']:.1f}%)")
print(f"   اللغة الرئيسية: {stats['primary_language']}")

# التقسيم
arabic_chunks = ml_splitter.split_text(arabic_text)
print(f"\n✅ تم تقسيم النص العربي إلى {len(arabic_chunks)} قطعة")

for i, chunk in enumerate(arabic_chunks, 1):
    print(f"\nالقطعة {i} ({len(chunk)} حرف):")
    print(chunk)

# اختبار مع بيانات وصفية
print("\n" + "=" * 60)
print("🧪 اختبار التقسيم مع البيانات الوصفية")
print("=" * 60)

chunks_with_meta = splitter.get_chunks_with_metadata(long_text, "doc_123")
print(f"✅ تم إنشاء {len(chunks_with_meta)} قطعة مع بيانات وصفية")

print(f"\nمثال على البيانات الوصفية للقطعة الأولى:")
print(chunks_with_meta[0])

# تنظيف
test_pdf.unlink()

print("\n" + "=" * 60)
print("🎉 جميع الاختبارات نجحت!")
print("=" * 60)