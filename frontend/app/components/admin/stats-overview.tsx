'use client'

import { useEffect, useState } from 'react'
import { StatsCard } from '../documents/stats-card'
import { FileText, MessageSquare, TrendingUp, Users, Database, Zap } from 'lucide-react'
import { documentsAPI } from '@/app/lib/api/documents'
import { chatAPI } from '@/app/lib/api/chat'

export function StatsOverview() {
  const [stats, setStats] = useState({
    documents: 0,
    chunks: 0,
    agents: 0,
    conversations: 0,
  })

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      // Documents stats
      const docStats = await documentsAPI.getStats() as any
      const agentsData = await chatAPI.getAgents() as any

      setStats({
        documents: docStats?.vector_store?.total_documents || 0,
        chunks: Object.values(docStats?.vector_store?.indexes || {}).reduce(
          (sum: number, val: any) => sum + (Number(val) || 0),
          0
        ),
        agents: agentsData?.agents?.length || 0,
        conversations: 0, // TODO: من API
      })
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatsCard
        title="إجمالي المستندات"
        value={stats.documents}
        icon={FileText}
        description="مستند مفهرس"
      />
      <StatsCard
        title="أجزاء البيانات"
        value={stats.chunks}
        icon={Database}
        description="جزء للبحث"
      />
      <StatsCard
        title="الوكلاء النشطون"
        value={stats.agents}
        icon={Zap}
        description="وكيل ذكي"
      />
      <StatsCard
        title="المحادثات"
        value={stats.conversations}
        icon={MessageSquare}
        description="محادثة"
      />
    </div>
  )
}
