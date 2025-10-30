'use client'

import { useState } from 'react'
import { AnalysisForm } from '@/app/components/financial/analysis-form'
import { InvestmentAdvice } from '@/app/components/financial/investment-advice'
import { Button } from '@/app/components/ui/button'

export default function FinancialPage() {
  const [activeTab, setActiveTab] = useState<'analysis' | 'investment'>('analysis')

  return (
    <div className="h-full overflow-y-auto">
      <div className="border-b bg-background p-6">
        <h2 className="text-2xl font-semibold mb-4">💰 الخدمات المالية</h2>
        
        {/* Tabs */}
        <div className="flex gap-2">
          <Button
            variant={activeTab === 'analysis' ? 'default' : 'outline'}
            onClick={() => setActiveTab('analysis')}
          >
            📊 التحليل المالي
          </Button>
          <Button
            variant={activeTab === 'investment' ? 'default' : 'outline'}
            onClick={() => setActiveTab('investment')}
          >
            💡 الاستشارات الاستثمارية
          </Button>
        </div>
      </div>

      <div className="p-6">
        {activeTab === 'analysis' ? <AnalysisForm /> : <InvestmentAdvice />}
      </div>
    </div>
  )
}
