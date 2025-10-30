'use client'

import { useState, useEffect } from 'react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { DocumentCard } from './document-card'
import { UploadDialog } from './upload-dialog'
import { Plus, Search, Loader2 } from 'lucide-react'
import { documentsAPI, type Document } from '@/app/lib/api/documents'

export function DocumentsContainer() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)

  // Mock data للتطوير
  useEffect(() => {
    // TODO: استبدل بـ API call حقيقي عندما يكون endpoint جاهز
    const mockData: Document[] = [
      {
        id: '1',
        filename: 'تقرير الأعمال السنوي 2024.pdf',
        file_type: 'pdf',
        file_size: 2548576,
        language: 'ar',
        chunks_count: 45,
        created_at: new Date().toISOString(),
      },
      {
        id: '2',
        filename: 'دليل المستخدم.docx',
        file_type: 'docx',
        file_size: 1024000,
        language: 'ar',
        chunks_count: 23,
        created_at: new Date(Date.now() - 86400000).toISOString(),
      },
    ]
    
    setTimeout(() => {
      setDocuments(mockData)
      setLoading(false)
    }, 500)
  }, [])

  const handleUploadComplete = () => {
    // TODO: إعادة تحميل القائمة
    console.log('Upload completed')
  }

  const handleViewDocument = (id: string) => {
    console.log('View document:', id)
    // TODO: فتح modal لعرض تفاصيل المستند
  }

  const handleDeleteDocument = (id: string) => {
    console.log('Delete document:', id)
    // TODO: تأكيد الحذف ثم الحذف
  }

  const filteredDocuments = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b bg-background p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-semibold">📄 المستندات</h2>
            <p className="text-sm text-muted-foreground mt-1">
              إدارة ومعالجة المستندات
            </p>
          </div>
          <Button onClick={() => setUploadDialogOpen(true)}>
            <Plus className="w-4 h-4 ml-2" />
            رفع مستند
          </Button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="بحث في المستندات..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pr-10"
          />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredDocuments.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-lg font-semibold mb-2">
              {searchQuery ? 'لا توجد نتائج' : 'لا توجد مستندات'}
            </h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery
                ? 'جرب مصطلح بحث آخر'
                : 'ابدأ برفع مستند جديد'}
            </p>
            {!searchQuery && (
              <Button onClick={() => setUploadDialogOpen(true)}>
                <Plus className="w-4 h-4 ml-2" />
                رفع أول مستند
              </Button>
            )}
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm text-muted-foreground">
                {filteredDocuments.length} مستند
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredDocuments.map((doc) => (
                <DocumentCard
                  key={doc.id}
                  {...doc}
                  onView={handleViewDocument}
                  onDelete={handleDeleteDocument}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* Upload Dialog */}
      <UploadDialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        onUploadComplete={handleUploadComplete}
      />
    </div>
  )
}
