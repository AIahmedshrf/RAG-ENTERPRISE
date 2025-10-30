'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Upload, FileText, X, Loader2, CheckCircle } from 'lucide-react'
import { documentsAPI } from '@/app/lib/api/documents'
import { formatFileSize } from '@/app/lib/utils'

interface UploadDialogProps {
  open: boolean
  onClose: () => void
  onUploadComplete?: () => void
}

export function UploadDialog({ open, onClose, onUploadComplete }: UploadDialogProps) {
  const [file, setFile] = useState<File | null>(null)
  const [language, setLanguage] = useState('ar')
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      setUploadStatus('idle')
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setUploadStatus('uploading')
    setError(null)

    try {
      const result = await documentsAPI.upload(file, language)
      
      setUploadStatus('success')
      setTimeout(() => {
        onUploadComplete?.()
        handleClose()
      }, 1500)
    } catch (err) {
      setUploadStatus('error')
      setError(err instanceof Error ? err.message : 'فشل رفع الملف')
    } finally {
      setUploading(false)
    }
  }

  const handleClose = () => {
    setFile(null)
    setUploadStatus('idle')
    setError(null)
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>رفع مستند جديد</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* File Input */}
          <div>
            <label className="block text-sm font-medium mb-2">اختر ملف</label>
            <div className="border-2 border-dashed rounded-lg p-6 text-center hover:border-primary transition-colors cursor-pointer">
              <input
                type="file"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                accept=".pdf,.docx,.txt,.xlsx,.pptx,.md"
                disabled={uploading}
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="w-12 h-12 mx-auto text-muted-foreground mb-2" />
                <p className="text-sm text-muted-foreground">
                  اضغط لاختيار ملف أو اسحبه هنا
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  PDF, DOCX, TXT, XLSX, PPTX, MD
                </p>
              </label>
            </div>

            {/* Selected File */}
            {file && (
              <div className="mt-3 p-3 bg-muted rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(file.size)}
                    </p>
                  </div>
                </div>
                {!uploading && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setFile(null)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                )}
              </div>
            )}
          </div>

          {/* Language Selection */}
          <div>
            <label className="block text-sm font-medium mb-2">اللغة</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full h-10 px-3 rounded-md border border-input bg-background"
              disabled={uploading}
            >
              <option value="ar">العربية</option>
              <option value="en">English</option>
            </select>
          </div>

          {/* Status Messages */}
          {uploadStatus === 'success' && (
            <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-2 text-green-700 dark:text-green-400">
              <CheckCircle className="w-5 h-5" />
              <span className="text-sm">تم رفع المستند بنجاح!</span>
            </div>
          )}

          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive rounded-lg text-destructive text-sm">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={handleClose} disabled={uploading}>
              إلغاء
            </Button>
            <Button onClick={handleUpload} disabled={!file || uploading}>
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 ml-2 animate-spin" />
                  جاري الرفع...
                </>
              ) : (
                'رفع'
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
