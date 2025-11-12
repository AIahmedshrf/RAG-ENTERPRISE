"use client"

import React, { useState } from 'react'
import { endpoint } from '@/app/lib/api-constants'

export default function UploadPage() {
  const [files, setFiles] = useState<FileList | null>(null)
  const [status, setStatus] = useState<any>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!files || files.length === 0) return

    const form = new FormData()
    Array.from(files).forEach(f => form.append('files', f))
    form.append('dataset_id', 'demo')

    setStatus('Uploading...')
    try {
      const res = await fetch(endpoint('/knowledge/documents/upload'), {
        method: 'POST',
        body: form
      })
      const data = await res.json()
      setStatus(data)
    } catch (e) {
      setStatus({ error: String(e) })
    }
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Upload Documents</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input type="file" multiple onChange={(e) => setFiles(e.target.files)} />
        <div>
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Upload</button>
        </div>
      </form>

      <pre className="mt-4 bg-gray-50 p-3 rounded">
        {status ? JSON.stringify(status, null, 2) : 'No activity yet.'}
      </pre>
    </div>
  )
}
