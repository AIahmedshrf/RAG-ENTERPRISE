export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'user'
}

export interface Agent {
  name: string
  description: string
  stats: {
    agent: string
    calls: number
    total_tokens: number
    errors: number
  }
}

export interface SystemStats {
  vector_store: {
    total_documents: number
    indexes: Record<string, number>
  }
}
