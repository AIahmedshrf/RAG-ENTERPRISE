# document_processing/chunking/text_splitter.py
"""
مقسم النصوص - من aisearchmm
يقسم النصوص الطويلة إلى أجزاء (chunks) مناسبة لـ RAG
"""

from typing import List, Optional
import re

from utilities.logger import logger


class TextSplitter:
    """مقسم النصوص الذكي"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        """
        Args:
            chunk_size: الحد الأقصى لحجم القطعة (بالأحرف)
            chunk_overlap: التداخل بين القطع
            separators: فواصل النص (الأولوية من الأول للأخير)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # الفواصل الافتراضية (بترتيب الأولوية)
        self.separators = separators or [
            "\n\n",  # فقرات
            "\n",    # أسطر
            ". ",    # جمل (إنجليزي)
            "。",     # جمل (صيني/ياباني)
            "؛ ",    # جمل (عربي)
            "، ",    # فواصل (عربي)
            ", ",    # فواصل (إنجليزي)
            " ",     # كلمات
            ""       # أحرف
        ]
        
        logger.info(f"Initialized TextSplitter (chunk_size={chunk_size}, overlap={chunk_overlap})")
    
    def split_text(self, text: str) -> List[str]:
        """
        تقسيم النص إلى أجزاء
        
        Args:
            text: النص المراد تقسيمه
            
        Returns:
            List[str]: قائمة الأجزاء
        """
        if not text or not text.strip():
            return []
        
        # إزالة المسافات الزائدة
        text = text.strip()
        
        # إذا كان النص أصغر من الحد، إرجاعه كما هو
        if len(text) <= self.chunk_size:
            return [text]
        
        # تقسيم باستخدام الفواصل
        chunks = self._split_with_separators(text)
        
        # دمج القطع الصغيرة
        chunks = self._merge_small_chunks(chunks)
        
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def _split_with_separators(self, text: str) -> List[str]:
        """تقسيم باستخدام الفواصل بالترتيب"""
        
        def _split_recursive(text: str, separators: List[str]) -> List[str]:
            """تقسيم متكرر"""
            if not separators:
                # لا توجد فواصل، تقسيم حسب الحجم
                return self._split_by_size(text)
            
            separator = separators[0]
            remaining_separators = separators[1:]
            
            # تقسيم بالفاصل الحالي
            if separator:
                splits = text.split(separator)
            else:
                splits = list(text)
            
            # معالجة كل جزء
            final_chunks = []
            current_chunk = ""
            
            for i, split in enumerate(splits):
                # إضافة الفاصل مرة أخرى (ماعدا آخر جزء)
                if i < len(splits) - 1:
                    split = split + separator
                
                # إذا كان الجزء أكبر من الحد، تقسيمه بفاصل آخر
                if len(split) > self.chunk_size:
                    if current_chunk:
                        final_chunks.append(current_chunk)
                        current_chunk = ""
                    
                    # تقسيم متكرر بفاصل أصغر
                    sub_chunks = _split_recursive(split, remaining_separators)
                    final_chunks.extend(sub_chunks)
                
                # إذا أضافة هذا الجزء لن تتجاوز الحد
                elif len(current_chunk) + len(split) <= self.chunk_size:
                    current_chunk += split
                
                # تجاوز الحد، حفظ القطعة الحالية وبدء جديدة
                else:
                    if current_chunk:
                        final_chunks.append(current_chunk)
                    current_chunk = split
            
            # إضافة آخر قطعة
            if current_chunk:
                final_chunks.append(current_chunk)
            
            return final_chunks
        
        return _split_recursive(text, self.separators)
    
    def _split_by_size(self, text: str) -> List[str]:
        """تقسيم حسب الحجم فقط (آخر خيار)"""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks
    
    def _merge_small_chunks(self, chunks: List[str]) -> List[str]:
        """دمج القطع الصغيرة جداً"""
        if not chunks:
            return []
        
        merged = []
        current = chunks[0]
        
        for i in range(1, len(chunks)):
            # إذا كانت القطعة الحالية صغيرة جداً، دمجها مع التالية
            if len(current) < self.chunk_size // 2:
                current = current + " " + chunks[i]
            else:
                merged.append(current)
                current = chunks[i]
        
        # إضافة آخر قطعة
        if current:
            merged.append(current)
        
        return merged
    
    def split_with_overlap(self, text: str) -> List[str]:
        """
        تقسيم مع تداخل محدد
        
        Args:
            text: النص
            
        Returns:
            List[str]: قائمة الأجزاء المتداخلة
        """
        # تقسيم أولي
        initial_chunks = self.split_text(text)
        
        if self.chunk_overlap == 0 or len(initial_chunks) <= 1:
            return initial_chunks
        
        # إضافة التداخل
        overlapped_chunks = []
        
        for i in range(len(initial_chunks)):
            chunk = initial_chunks[i]
            
            # إضافة نهاية القطعة السابقة
            if i > 0:
                prev_chunk = initial_chunks[i - 1]
                overlap = prev_chunk[-self.chunk_overlap:]
                chunk = overlap + " " + chunk
            
            overlapped_chunks.append(chunk)
        
        return overlapped_chunks
    
    def get_chunks_with_metadata(self, text: str, document_id: str) -> List[dict]:
        """
        تقسيم مع إضافة بيانات وصفية لكل قطعة
        
        Args:
            text: النص
            document_id: معرف المستند
            
        Returns:
            List[dict]: قائمة القطع مع بياناتها
        """
        chunks = self.split_text(text)
        
        result = []
        for i, chunk in enumerate(chunks):
            result.append({
                "chunk_id": f"{document_id}_chunk_{i}",
                "content": chunk,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "char_count": len(chunk),
                "word_count": len(chunk.split())
            })
        
        return result