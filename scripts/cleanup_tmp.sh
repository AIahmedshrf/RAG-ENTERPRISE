#!/bin/bash

echo "🧹 تنظيف /tmp/rag-enterprise..."

# حذف الملفات القديمة (أكثر من 7 أيام)
find /tmp/rag-enterprise/storage -type f -mtime +7 -delete 2>/dev/null

# حذف logs القديمة
find /tmp/rag-enterprise/logs -name "*.log.*" -mtime +3 -delete 2>/dev/null

# عرض المساحة
echo ""
echo "📊 Storage size:"
du -sh /tmp/rag-enterprise/* 2>/dev/null

echo ""
echo "✅ Cleanup complete"
