'use client'

import { useState, useRef, useEffect } from 'react'
import { ChatMessage } from './message'
import { ChatInput } from './chat-input'
import { chatAPI, type ChatResponse } from '@/app/lib/api/chat'
import { Card } from '../ui/card'
import { Loader2, AlertCircle } from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: ChatResponse['sources']
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (content: string) => {
    // إضافة رسالة المستخدم
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
    }
    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      // إرسال للـ API
      const response = await chatAPI.sendMessage({
        query: content,
        use_search: true,
        top_k: 5,
        agent: 'auto',
      })

      // إضافة رد المساعد
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'حدث خطأ في الاتصال')
      console.error('Chat error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="border-b bg-background p-4">
        <h2 className="text-xl font-semibold">💬 المحادثة الذكية</h2>
        <p className="text-sm text-muted-foreground">اسأل عن أي شيء في المستندات</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <Card className="p-8 text-center max-w-md">
              <h3 className="text-lg font-semibold mb-2">مرحباً بك! 👋</h3>
              <p className="text-muted-foreground">
                يمكنك البدء بطرح أسئلة عن المستندات المرفوعة، أو الحصول على معلومات عامة.
              </p>
            </Card>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} {...message} />
        ))}

        {isLoading && (
          <div className="flex justify-center">
            <Card className="p-4 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">جاري التفكير...</span>
            </Card>
          </div>
        )}

        {error && (
          <Card className="p-4 bg-destructive/10 border-destructive">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0" />
              <div>
                <p className="font-medium text-destructive">حدث خطأ</p>
                <p className="text-sm text-destructive/80">{error}</p>
              </div>
            </div>
          </Card>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
    </div>
  )
}
