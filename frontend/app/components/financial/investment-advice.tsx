'use client'

import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Lightbulb, Loader2, AlertTriangle } from 'lucide-react'
import { financialAPI } from '@/app/lib/api/financial'

type RiskLevel = 'conservative' | 'moderate' | 'aggressive'

export function InvestmentAdvice() {
  const [query, setQuery] = useState('')
  const [riskLevel, setRiskLevel] = useState<RiskLevel>('moderate')
  const [loading, setLoading] = useState(false)
  const [advice, setAdvice] = useState<string | null>(null)
  const [disclaimer, setDisclaimer] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGetAdvice = async () => {
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setAdvice(null)

    try {
      const response = await financialAPI.getInvestmentAdvice({
        query,
        risk_tolerance: riskLevel,
      })
      setAdvice(response.advice)
      setDisclaimer(response.disclaimer)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'حدث خطأ')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5" />
            الاستشارات الاستثمارية
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">
              استفسارك الاستثماري
            </label>
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="مثال: هل الاستثمار في التكنولوجيا جيد الآن؟"
              onKeyPress={(e) => e.key === 'Enter' && handleGetAdvice()}
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-2 block">
              مستوى تحمل المخاطر
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'conservative', label: 'محافظ', emoji: '🛡️' },
                { value: 'moderate', label: 'متوسط', emoji: '⚖️' },
                { value: 'aggressive', label: 'عالي', emoji: '🚀' },
              ].map((option) => (
                <Button
                  key={option.value}
                  variant={riskLevel === option.value ? 'default' : 'outline'}
                  onClick={() => setRiskLevel(option.value as RiskLevel)}
                  className="flex items-center gap-2"
                >
                  <span>{option.emoji}</span>
                  <span className="text-xs">{option.label}</span>
                </Button>
              ))}
            </div>
          </div>

          <Button
            onClick={handleGetAdvice}
            disabled={!query.trim() || loading}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 ml-2 animate-spin" />
                جاري التحليل...
              </>
            ) : (
              <>
                <Lightbulb className="w-4 h-4 ml-2" />
                احصل على استشارة
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="p-4 text-destructive">
            <p className="text-sm">{error}</p>
          </CardContent>
        </Card>
      )}

      {/* Advice */}
      {advice && (
        <Card>
          <CardHeader>
            <CardTitle>الاستشارة الاستثمارية</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <p className="whitespace-pre-wrap">{advice}</p>
            </div>

            {disclaimer && (
              <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-amber-800 dark:text-amber-200">
                    {disclaimer}
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
