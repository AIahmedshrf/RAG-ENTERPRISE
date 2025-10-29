# utilities/helpers.py
"""
دوال مساعدة عامة
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import mimetypes

from utilities.logger import logger


def generate_unique_id(prefix: str = "", suffix: str = "") -> str:
    """
    توليد معرف فريد
    
    Args:
        prefix: بادئة اختيارية
        suffix: لاحقة اختيارية
        
    Returns:
        str: المعرف الفريد
    """
    timestamp = datetime.now().isoformat()
    unique_string = f"{prefix}_{timestamp}_{suffix}"
    hash_id = hashlib.md5(unique_string.encode()).hexdigest()
    
    if prefix:
        return f"{prefix}_{hash_id}"
    return hash_id


def get_file_extension(filename: str) -> str:
    """
    الحصول على امتداد الملف
    
    Args:
        filename: اسم الملف
        
    Returns:
        str: الامتداد (بدون نقطة)
    """
    return Path(filename).suffix.lower().lstrip('.')


def get_mime_type(filename: str) -> Optional[str]:
    """
    الحصول على نوع MIME
    
    Args:
        filename: اسم الملف
        
    Returns:
        Optional[str]: نوع MIME
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type


def format_file_size(size_bytes: int) -> str:
    """
    تنسيق حجم الملف بشكل قابل للقراءة
    
    Args:
        size_bytes: الحجم بالبايت
        
    Returns:
        str: الحجم المنسق (مثل: 1.5 MB)
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def sanitize_filename(filename: str) -> str:
    """
    تنظيف اسم الملف من الأحرف غير الآمنة
    
    Args:
        filename: اسم الملف الأصلي
        
    Returns:
        str: اسم الملف المُنظف
    """
    import re
    
    # إزالة المسارات
    filename = Path(filename).name
    
    # استبدال الأحرف غير الآمنة
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)
    
    # إزالة المسافات المتعددة
    filename = re.sub(r'\s+', '_', filename)
    
    return filename


def ensure_directory(directory: str) -> Path:
    """
    التأكد من وجود المجلد وإنشائه إذا لم يكن موجوداً
    
    Args:
        directory: مسار المجلد
        
    Returns:
        Path: كائن Path للمجلد
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {directory}")
    return path


def safe_json_serialize(obj: Any) -> Dict:
    """
    تحويل كائن إلى قاموس قابل للتحويل إلى JSON
    
    Args:
        obj: الكائن
        
    Returns:
        Dict: القاموس
    """
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: safe_json_serialize(value) for key, value in obj.items()}
    else:
        return obj


async def save_upload_file(upload_file, destination: str) -> str:
    """
    حفظ ملف مرفوع
    
    Args:
        upload_file: ملف FastAPI UploadFile
        destination: مسار الحفظ
        
    Returns:
        str: المسار الكامل للملف المحفوظ
    """
    # التأكد من وجود المجلد
    dest_path = Path(destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # حفظ الملف
    with open(dest_path, 'wb') as f:
        content = await upload_file.read()
        f.write(content)
    
    logger.info(f"Saved uploaded file to: {destination}")
    return str(dest_path)