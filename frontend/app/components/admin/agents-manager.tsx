'use client'

import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { chatAPI } from '@/app/lib/api/chat'
import { Bot, Activity } from 'lucide-react'

interface Agent {
  name: string
  description: string
  stats: {
    calls: number
    total_tokens: number
    errors: number
  }
}

export function AgentsManager() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAgents()
  }, [])

  const loadAgents = async () => {
    try {
      const data = await chatAPI.getAgents()
      if (data && typeof data === 'object' && 'agents' in data) {
        setAgents((data as any).agents || [])
      } else if (Array.isArray(data)) {
        setAgents(data)
      }
    } catch (error) {
      console.error('Failed to load agents:', error)
      setAgents([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bot className="w-5 h-5" />
          الوكلاء الأذكياء
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-sm text-muted-foreground">جاري التحميل...</p>
        ) : (
          <div className="space-y-3">
            {agents.map((agent) => (
              <div
                key={agent.name}
                className="p-4 border rounded-lg hover:bg-accent transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold">{agent.name}</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      {agent.description}
                    </p>
                    <div className="flex gap-4 mt-3 text-xs text-muted-foreground">
                      <span>📞 {agent.stats.calls} استدعاء</span>
                      <span>🎯 {agent.stats.total_tokens} token</span>
                      {agent.stats.errors > 0 && (
                        <span className="text-destructive">
                          ⚠️ {agent.stats.errors} خطأ
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-xs text-muted-foreground">نشط</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
