# core/exceptions.py
"""
معالجة الاستثناءات المخصصة للنظام
"""


class RAGEnterpriseException(Exception):
    """الاستثناء الأساسي للنظام"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(RAGEnterpriseException):
    """خطأ في التكوين"""
    pass


class DocumentProcessingError(RAGEnterpriseException):
    """خطأ في معالجة المستندات"""
    pass


class SearchError(RAGEnterpriseException):
    """خطأ في البحث"""
    pass


class AgentExecutionError(RAGEnterpriseException):
    """خطأ في تنفيذ الوكيل"""
    pass


class FinancialDataError(RAGEnterpriseException):
    """خطأ في البيانات المالية"""
    pass


class AuthenticationError(RAGEnterpriseException):
    """خطأ في المصادقة"""
    pass


class RateLimitError(RAGEnterpriseException):
    """تجاوز الحد الأقصى للطلبات"""
    pass