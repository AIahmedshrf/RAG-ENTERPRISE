// Financial Intelligence Page
'use client';

import React, { useState } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';

export default function FinancialPage() {
  const [symbol, setSymbol] = useState('');
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!symbol) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/v1/financial/analyze/${symbol}`);
      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Financial Intelligence</h1>
        <p className="mt-2 text-gray-600">AI-powered market analysis and insights</p>
      </div>

      {/* Analysis Input */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Stock Analysis</h3>
        <div className="flex gap-4">
          <Input
            placeholder="Enter stock symbol (e.g., AAPL)"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            className="flex-1"
          />
          <Button onClick={handleAnalyze} loading={loading}>
            Analyze
          </Button>
        </div>
      </div>

      {/* Results */}
      {analysis && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="text-sm text-gray-600 mb-1">Current Price</div>
            <div className="text-3xl font-bold text-gray-900">$150.25</div>
            <div className="text-sm text-green-600 mt-1">+2.5%</div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="text-sm text-gray-600 mb-1">Market Cap</div>
            <div className="text-3xl font-bold text-gray-900">$2.5T</div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="text-sm text-gray-600 mb-1">AI Score</div>
            <div className="text-3xl font-bold text-blue-600">8.5/10</div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-2">Market Overview</h3>
          <p className="text-sm text-gray-600 mb-4">Real-time market insights</p>
          <Button variant="secondary">View Markets</Button>
        </div>
        
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-2">Portfolio Analysis</h3>
          <p className="text-sm text-gray-600 mb-4">Track your investments</p>
          <Button variant="secondary">View Portfolio</Button>
        </div>
      </div>
    </div>
  );
}
