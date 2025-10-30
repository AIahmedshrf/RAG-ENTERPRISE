'use client'

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card'
import { Button } from '../ui/button'
import { FileText, Download, Trash2, Eye } from 'lucide-react'
import { formatFileSize, formatDate } from '@/app/lib/utils'

interface DocumentCardProps {
  id: string
  filename: string
  file_type: string
  file_size: number
  language: string
  chunks_count: number
  created_at: string
  onView?: (id: string) => void
  onDelete?: (id: string) => void
}

export function DocumentCard({
  id,
  filename,
  file_type,
  file_size,
  language,
  chunks_count,
  created_at,
  onView,
  onDelete,
}: DocumentCardProps) {
  const getFileIcon = () => {
    switch (file_type) {
      case 'pdf':
        return '📄'
      case 'docx':
      case 'doc':
        return '📝'
      case 'xlsx':
      case 'xls':
        return '📊'
      case 'pptx':
      case 'ppt':
        return '📽️'
      default:
        return '📄'
    }
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1">
            <div className="text-4xl">{getFileIcon()}</div>
            <div className="flex-1 min-w-0">
              <CardTitle className="text-base truncate" title={filename}>
                {filename}
              </CardTitle>
              <CardDescription className="mt-1">
                {formatFileSize(file_size)} • {chunks_count} أجزاء
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          {/* Metadata */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">اللغة:</span>
            <span className="font-medium">
              {language === 'ar' ? '🇸🇦 عربي' : '🇬🇧 English'}
            </span>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">تاريخ الرفع:</span>
            <span className="font-medium text-xs">
              {formatDate(created_at)}
            </span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">النوع:</span>
            <span className="font-medium uppercase">{file_type}</span>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2 border-t">
            <Button
              variant="outline"
              size="sm"
              className="flex-1"
              onClick={() => onView?.(id)}
            >
              <Eye className="w-4 h-4 ml-2" />
              عرض
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDelete?.(id)}
            >
              <Trash2 className="w-4 h-4 text-destructive" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
