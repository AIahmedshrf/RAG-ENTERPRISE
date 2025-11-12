"use client"

import React, { useEffect, useState } from 'react'
import { endpoint } from '@/app/lib/api-constants'

export default function DocsPage() {
  const [docs, setDocs] = useState<any[]>([])

  const load = async () => {
    try {
  const res = await fetch(endpoint('/knowledge/documents'))
      const data = await res.json()
  setDocs(data.documents || [])
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Documents</h2>
      {docs.length === 0 ? <div>No documents</div> : (
        <ul className="space-y-2">
          {docs.map(d => (
            <li key={d.id} className="p-3 border rounded">
              <div className="font-semibold">{d.name}</div>
              <div className="text-sm text-gray-600">Status: {d.status}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
