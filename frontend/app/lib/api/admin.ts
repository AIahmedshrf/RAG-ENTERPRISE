import { apiClient } from './client'

// ===== Users Management =====

export interface User {
  id: number
  email: string
  username: string
  full_name: string
  role: string
  is_active: boolean
}

export interface UserCreate {
  email: string
  username: string
  full_name: string
  password: string
  role?: string
}

export interface UserStats {
  total_users: number
  active_users: number
  admin_users: number
  inactive_users: number
}

export const usersAPI = {
  list: async (skip: number = 0, limit: number = 100): Promise<User[]> => {
    return apiClient.get(`/api/v1/admin/users/?skip=${skip}&limit=${limit}`)
  },

  get: async (userId: number): Promise<User> => {
    return apiClient.get(`/api/v1/admin/users/${userId}`)
  },

  create: async (user: UserCreate): Promise<User> => {
    return apiClient.post('/api/v1/admin/users/', user)
  },

  delete: async (userId: number) => {
    return apiClient.post(`/api/v1/admin/users/${userId}`, {})
  },

  getStats: async (): Promise<UserStats> => {
    return apiClient.get('/api/v1/admin/users/stats/summary')
  },
}

// ===== Models Management =====

export interface AIModel {
  id: string
  name: string
  provider: string
  deployment_name?: string
  status: string
  created_at: string
}

export interface ModelConfig {
  name: string
  provider: string
  deployment_name?: string
  api_key?: string
  endpoint?: string
  max_tokens?: number
  temperature?: number
}

export interface Provider {
  id: string
  name: string
}

export const modelsAPI = {
  list: async (): Promise<AIModel[]> => {
    const response = await apiClient.get<{ success: boolean; models: AIModel[] }>(
      '/api/v1/admin/models/'
    )
    return response.models
  },

  get: async (modelId: string): Promise<AIModel> => {
    return apiClient.get(`/api/v1/admin/models/${modelId}`)
  },

  create: async (model: ModelConfig): Promise<AIModel> => {
    const response = await apiClient.post<{ success: boolean; model: AIModel }>(
      '/api/v1/admin/models/',
      model
    )
    return response.model
  },

  delete: async (modelId: string) => {
    return apiClient.post(`/api/v1/admin/models/${modelId}`, {})
  },

  getProviders: async (): Promise<Provider[]> => {
    const response = await apiClient.get<{ providers: Provider[] }>(
      '/api/v1/admin/models/providers/list'
    )
    return response.providers
  },
}
