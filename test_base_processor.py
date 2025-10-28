"""اختبار المعالج الأساسي"""

import asyncio
from pathlib import Path
from document_processing.processors.base_processor import (
    BaseDocumentProcessor,
    ProcessedDocument,
    DocumentMetadata
)

# معالج تجريبي للاختبار
class TestProcessor(BaseDocumentProcessor):
    def __init__(self):
        super().__init__()
        self.supported_formats = ["txt", "md"]
    
    async def process(self, file_path: str) -> ProcessedDocument:
        # التحقق من الملف
        self._validate_file(file_path)
        
        # قراءة المحتوى
        content = Path(file_path).read_text(encoding='utf-8')
        
        # استخراج البيانات الوصفية
        metadata = self._extract_metadata(file_path)
        metadata.language = self._detect_language(content)
        
        # إنشاء المستند المعالج
        doc = ProcessedDocument(
            id=self._generate_document_id(file_path),
            content=content,
            metadata=metadata
        )
        
        return doc

async def main():
    print("🧪 اختبار المعالج الأساسي...")
    print("=" * 50)
    
    # إنشاء معالج
    processor = TestProcessor()
    print(f"✅ تم إنشاء المعالج: {processor.processor_name}")
    print(f"   الصيغ المدعومة: {processor.supported_formats}")
    
    # إنشاء ملف تجريبي
    test_file = Path("test_document.txt")
    test_file.write_text("This is a test document.\nهذا مستند تجريبي.", encoding='utf-8')
    print(f"✅ تم إنشاء ملف تجريبي: {test_file}")
    
    # اختبار can_process
    can_process = processor.can_process(str(test_file))
    print(f"✅ يمكن معالجة الملف: {can_process}")
    
    # معالجة الملف
    doc = await processor.process(str(test_file))
    print(f"✅ تم معالجة المستند:")
    print(f"   المعرف: {doc.id}")
    print(f"   اسم الملف: {doc.metadata.filename}")
    print(f"   النوع: {doc.metadata.file_type}")
    print(f"   الحجم: {doc.metadata.file_size} bytes")
    print(f"   اللغة: {doc.metadata.language}")
    print(f"   طول المحتوى: {len(doc.content)} chars")
    
    # عرض الملخص
    summary = doc.get_summary()
    print(f"\n📊 ملخص المستند:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # تنظيف
    test_file.unlink()
    print(f"\n✅ تم حذف الملف التجريبي")
    
    print("\n" + "=" * 50)
    print("🎉 جميع الاختبارات نجحت!")

if __name__ == "__main__":
    asyncio.run(main())
