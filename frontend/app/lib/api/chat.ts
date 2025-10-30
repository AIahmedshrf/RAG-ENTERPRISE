import { apiClient } from './client'

export interface ChatMessage {
  query: string
  use_search?: boolean
  top_k?: number
  agent?: string
}

export interface ChatResponse {
  success: boolean
  query: string
  answer: string
  agent_used: string
  sources?: Array<{
    id: string
    score: number
    preview: string
  }>
  total_sources: number
}

export const chatAPI = {
  sendMessage: async (message: ChatMessage): Promise<ChatResponse> => {
    return apiClient.post('/api/v1/chat/message', message)
  },

  getAgents: async () => {
    return apiClient.get('/api/v1/chat/agents')
  },

  resetMemory: async () => {
    return apiClient.post('/api/v1/chat/reset-memory')
  },
}
