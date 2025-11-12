// Documents Management (Client View)
'use client';

import React, { useState, useCallback } from 'react';
import { Button } from '@/app/components/ui/button';

export default function DocumentsPage() {
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState<any[]>([]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files?.length) return;

    setUploading(true);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('Please login first');
        return;
      }

      for (const file of Array.from(files)) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('dataset_id', 'default-dataset'); // TODO: Get from context

        const response = await fetch('http://localhost:8000/documents/upload', {
          method: 'POST',
          body: formData,
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }
      }

      alert('Documents uploaded successfully!');
      // Reload documents list
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload documents');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Documents</h1>
          <p className="mt-2 text-gray-600">Upload and manage your documents</p>
        </div>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-xl border-2 border-dashed border-gray-300 p-12 text-center hover:border-blue-500 transition-colors">
        <div className="text-6xl mb-4">📄</div>
        <h3 className="text-lg font-semibold mb-2">Upload Documents</h3>
        <p className="text-gray-600 mb-4">
          Drag and drop files here, or click to browse
        </p>
        <input
          type="file"
          multiple
          onChange={handleFileUpload}
          className="hidden"
          id="file-upload"
          accept=".pdf,.doc,.docx,.txt"
        />
        <label htmlFor="file-upload" className="cursor-pointer inline-block">
          <Button disabled={uploading} type="button">
            {uploading ? 'Uploading...' : 'Choose Files'}
          </Button>
        </label>
        <p className="text-xs text-gray-500 mt-4">
          Supported: PDF, DOC, DOCX, TXT
        </p>
      </div>

      {/* Documents List */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Documents</h3>
        
        {documents.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No documents yet. Upload your first document!
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center gap-3">
                  <div className="text-3xl">📄</div>
                  <div>
                    <p className="font-medium">{doc.name}</p>
                    <p className="text-sm text-gray-500">{doc.size}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button className="text-blue-600 hover:text-blue-800">View</button>
                  <button className="text-red-600 hover:text-red-800">Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
