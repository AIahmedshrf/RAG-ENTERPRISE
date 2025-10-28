# document_processing/chunking/multilingual_splitter.py
"""
مقسم النصوص متعدد اللغات - مع دعم محسّن للعربية
"""

from typing import List
import re

from .text_splitter import TextSplitter
from utilities.logger import logger


class MultilingualTextSplitter(TextSplitter):
    """مقسم نصوص مع دعم محسّن للعربية"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        # فواصل مخصصة للعربية
        arabic_separators = [
            "\n\n",      # فقرات
            "\n",        # أسطر
            ".",         # نقطة (إنجليزي)
            "。",         # نقطة (صيني/ياباني)
            "؛",         # فاصلة منقوطة (عربي)
            ".",         # نقطة (عربي)
            "!",         # تعجب
            "؟",         # استفهام (عربي)
            "?",         # استفهام (إنجليزي)
            "،",         # فاصلة (عربي)
            ",",         # فاصلة (إنجليزي)
            " و ",       # حرف عطف
            " أو ",      # حرف عطف
            " ثم ",      # حرف عطف
            " ",         # مسافة
            ""           # حرف
        ]
        
        super().__init__(chunk_size, chunk_overlap, arabic_separators)
        logger.info("Initialized MultilingualTextSplitter with Arabic support")
    
    def split_text(self, text: str) -> List[str]:
        """تقسيم مع معالجة خاصة للعربية"""
        
        # تنظيف النص العربي
        text = self._clean_arabic_text(text)
        
        # التقسيم الأساسي
        chunks = super().split_text(text)
        
        # معالجة إضافية للعربية
        chunks = [self._post_process_arabic_chunk(chunk) for chunk in chunks]
        
        return chunks
    
    def _clean_arabic_text(self, text: str) -> str:
        """تنظيف النص العربي"""
        # توحيد الهمزات
        text = re.sub(r'[إأآا]', 'ا', text)
        
        # توحيد التاء المربوطة والهاء
        text = re.sub(r'ة', 'ه', text)
        
        # إزالة التشكيل
        arabic_diacritics = re.compile(r'[\u064B-\u065F\u0670]')
        text = arabic_diacritics.sub('', text)
        
        # إزالة المسافات المتعددة
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _post_process_arabic_chunk(self, chunk: str) -> str:
        """معالجة نهائية للقطعة العربية"""
        # إزالة المسافات من البداية والنهاية
        chunk = chunk.strip()
        
        # التأكد من عدم بدء القطعة بحرف عطف
        arabic_conjunctions = ['و', 'أو', 'ثم', 'لكن', 'بل']
        for conj in arabic_conjunctions:
            if chunk.startswith(conj + ' '):
                chunk = chunk[len(conj):].strip()
        
        return chunk
    
    def is_arabic(self, text: str) -> bool:
        """التحقق من وجود نص عربي"""
        arabic_pattern = re.compile(r'[\u0600-\u06FF]')
        return bool(arabic_pattern.search(text))
    
    def get_language_stats(self, text: str) -> dict:
        """إحصائيات اللغة في النص"""
        total_chars = len(text)
        
        # حساب الأحرف العربية
        arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
        
        # حساب الأحرف الإنجليزية
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        return {
            "total_chars": total_chars,
            "arabic_chars": arabic_chars,
            "english_chars": english_chars,
            "arabic_percentage": (arabic_chars / total_chars * 100) if total_chars > 0 else 0,
            "english_percentage": (english_chars / total_chars * 100) if total_chars > 0 else 0,
            "primary_language": "arabic" if arabic_chars > english_chars else "english"
        }