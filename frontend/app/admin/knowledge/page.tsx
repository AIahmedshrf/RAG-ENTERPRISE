"use client"

import React, { useState } from 'react'
import { endpoint } from '@/app/lib/api-constants'

export default function KnowledgePage() {
  const [q, setQ] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const handleSearch = async () => {
    setLoading(true)
    try {
      const res = await fetch(endpoint('/knowledge/search'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q })
      })
      const data = await res.json()
      setResults(data.results || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Knowledge Explorer</h2>
      <div className="flex gap-2 mb-4">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search the knowledge base..." className="flex-1 p-2 border rounded" />
        <button onClick={handleSearch} className="px-4 py-2 bg-blue-600 text-white rounded">{loading ? 'Searching...' : 'Search'}</button>
      </div>

      <div>
        {results.length === 0 ? (
          <div className="text-gray-600">No results yet.</div>
        ) : (
          <ul className="space-y-2">
            {results.map((r, idx) => (
              <li key={idx} className="p-3 border rounded">
                <div className="font-semibold">{r.document_id || 'Document'}</div>
                <div className="text-sm text-gray-700">{r.text_snippet || JSON.stringify(r).slice(0,200)}</div>
                <div className="text-xs text-gray-500 mt-1">score: {r.score ?? ''}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
