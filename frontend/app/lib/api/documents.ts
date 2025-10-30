import { apiClient } from './client'

export interface Document {
  id: string
  filename: string
  file_type: string
  file_size: number
  language: string
  chunks_count: number
  created_at: string
}

export interface UploadDocumentResponse {
  success: boolean
  document: Document
  indexing: {
    chunks_indexed: number
    status: string
  }
}

export const documentsAPI = {
  upload: async (file: File, language: string = 'ar'): Promise<UploadDocumentResponse> => {
    return apiClient.uploadFile('/api/v1/documents/upload', file, { language })
  },

  getStats: async () => {
    return apiClient.get('/api/v1/documents/stats')
  },

  getSupportedFormats: async () => {
    return apiClient.get('/api/v1/documents/supported-formats')
  },
}
