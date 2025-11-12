'use client'

import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { TrendingUp, Loader2, FileText } from 'lucide-react'
import { financialAPI } from '@/app/lib/api/financial'

interface AnalysisResult {
  analysis: string
  financial_data?: {
    numbers: string[]
    ratios: string[]
  }
  sources?: Array<{
    id: string
    score: number
  }>
}

export function AnalysisForm() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await financialAPI.analyze({
        query,
        include_ratios: true,
      })
      setResult(response as AnalysisResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'حدث خطأ في التحليل')
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
            <TrendingUp className="w-5 h-5" />
            التحليل المالي
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">
              أدخل استفسارك المالي
            </label>
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="مثال: حلل الأداء المالي للشركة في Q1 2024"
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
            />
          </div>

          <div className="flex gap-2">
            <Button
              onClick={handleAnalyze}
              disabled={!query.trim() || loading}
              className="flex-1"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 ml-2 animate-spin" />
                  جاري التحليل...
                </>
              ) : (
                <>
                  <TrendingUp className="w-4 h-4 ml-2" />
                  تحليل
                </>
              )}
            </Button>
          </div>
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

      {/* Results */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle>نتائج التحليل</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Analysis Text */}
            <div className="prose prose-sm max-w-none dark:prose-invert">
              <p className="whitespace-pre-wrap">{result.analysis}</p>
            </div>

            {/* Financial Data */}
            {result.financial_data && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
                {result.financial_data.numbers.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 text-sm">الأرقام الرئيسية</h4>
                    <div className="space-y-1">
                      {result.financial_data.numbers.slice(0, 5).map((num, idx) => (
                        <div key={idx} className="text-sm bg-muted p-2 rounded">
                          {num}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {result.financial_data.ratios.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 text-sm">النسب المالية</h4>
                    <div className="space-y-1">
                      {result.financial_data.ratios.slice(0, 3).map((ratio, idx) => (
                        <div key={idx} className="text-sm bg-muted p-2 rounded">
                          {ratio}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Sources */}
            {result.sources && result.sources.length > 0 && (
              <div className="pt-4 border-t">
                <h4 className="font-semibold mb-2 text-sm flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  المصادر ({result.sources.length})
                </h4>
                <div className="space-y-2">
                  {result.sources.map((source, idx) => (
                    <div key={idx} className="text-xs bg-muted p-2 rounded flex justify-between">
                      <span>{source.id}</span>
                      <span className="text-primary">
                        {(source.score * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
