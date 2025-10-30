import { apiClient } from './client'

export interface FinancialAnalysisRequest {
  query: string
  include_ratios?: boolean
}

export interface InvestmentAdviceRequest {
  query: string
  risk_tolerance?: 'conservative' | 'moderate' | 'aggressive'
}

export const financialAPI = {
  analyze: async (request: FinancialAnalysisRequest) => {
    return apiClient.post('/api/v1/financial/analyze', request)
  },

  getInvestmentAdvice: async (request: InvestmentAdviceRequest) => {
    return apiClient.post('/api/v1/financial/investment-advice', request)
  },

  getAgents: async () => {
    return apiClient.get('/api/v1/financial/agents')
  },
}
