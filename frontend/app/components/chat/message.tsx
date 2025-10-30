'use client'

import { cn } from '@/app/lib/utils'
import { Card } from '../ui/card'
import { User, Bot, FileText } from 'lucide-react'

interface MessageProps {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{
    id: string
    score: number
    preview: string
  }>
}

export function ChatMessage({ role, content, sources }: MessageProps) {
  const isUser = role === 'user'

  return (
    <div
      className={cn(
        'flex gap-3 p-4',
        isUser ? 'justify-start' : 'justify-end'
      )}
    >
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
          <Bot className="w-5 h-5 text-primary-foreground" />
        </div>
      )}
      
      <div className={cn('flex flex-col gap-2 max-w-[80%]', isUser && 'items-end')}>
        <Card
          className={cn(
            'p-4',
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted'
          )}
        >
          <p className="text-sm whitespace-pre-wrap">{content}</p>
        </Card>

        {/* المصادر */}
        {sources && sources.length > 0 && (
          <div className="space-y-2 w-full">
            <p className="text-xs text-muted-foreground px-2">المصادر ({sources.length}):</p>
            {sources.map((source, idx) => (
              <Card key={idx} className="p-3 text-xs border-l-2 border-primary">
                <div className="flex items-start gap-2">
                  <FileText className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium">{source.id}</p>
                    <p className="text-muted-foreground mt-1">{source.preview}</p>
                    <p className="text-primary mt-1">درجة التطابق: {(source.score * 100).toFixed(1)}%</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
          <User className="w-5 h-5 text-secondary-foreground" />
        </div>
      )}
    </div>
  )
}
