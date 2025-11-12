"use client"

import React, { useEffect, useState } from 'react'
import { endpoint } from '@/app/lib/api-constants'

type FormState = {
  name: string
  description: string
  dataset_ids: string
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const loadAgents = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(endpoint('/agents/'), {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      })
      const data = await res.json()
      setAgents(data.agents || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadAgents() }, [])

  const [form, setForm] = useState<FormState>({ name: '', description: '', dataset_ids: '' })
  const [creating, setCreating] = useState(false)

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(endpoint('/agents/'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          name: form.name,
          description: form.description,
          dataset_ids: form.dataset_ids ? form.dataset_ids.split(',').map(s => s.trim()) : [],
        }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to create agent')
      }
      await loadAgents()
      setForm({ name: '', description: '', dataset_ids: '' })
    } catch (err: any) {
      alert(err.message || 'Create failed')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Agents</h2>
        <div className="space-x-2">
          <button onClick={loadAgents} className="px-3 py-1 bg-gray-200 rounded">Refresh</button>
        </div>
      </div>

      <form onSubmit={handleCreate} className="mb-4 p-3 border rounded">
        <div className="grid grid-cols-3 gap-2 items-center">
          <input className="col-span-1 p-2 border rounded" placeholder="Name" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
          <input className="col-span-1 p-2 border rounded" placeholder="Description" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} />
          <input className="col-span-1 p-2 border rounded" placeholder="dataset1,dataset2" value={form.dataset_ids} onChange={e => setForm({ ...form, dataset_ids: e.target.value })} />
        </div>
        <div className="mt-2">
          <button type="submit" disabled={creating} className="px-3 py-1 bg-blue-600 text-white rounded">{creating ? 'Creating...' : 'Create Agent'}</button>
        </div>
      </form>

      {loading ? (
        <div>Loading...</div>
      ) : agents.length === 0 ? (
        <div className="text-gray-600">No agents yet. Use the API to create one.</div>
      ) : (
        <ul className="space-y-2">
          {agents.map((a) => (
            <li key={a.id} className="p-3 border rounded">
              <div className="font-semibold">{a.name}</div>
              <div className="text-sm text-gray-700">{a.description}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
