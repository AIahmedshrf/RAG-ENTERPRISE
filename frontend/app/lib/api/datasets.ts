// Adapted from Dify - Datasets API Service
const API_PREFIX = '/api/v1/admin/datasets';

export const datasetsAPI = {
  async list(page = 1, limit = 20) {
    const response = await fetch(`${API_PREFIX}?page=${page}&limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch datasets');
    return response.json();
  },

  async create(data: { name: string; description?: string; indexing_technique?: string }) {
    const response = await fetch(`${API_PREFIX}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create dataset');
    return response.json();
  },

  async get(id: string) {
    const response = await fetch(`${API_PREFIX}/${id}`);
    if (!response.ok) throw new Error('Failed to fetch dataset');
    return response.json();
  },

  async delete(id: string) {
    const response = await fetch(`${API_PREFIX}/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete dataset');
  },

  async getDocuments(id: string, page = 1, limit = 20) {
    const response = await fetch(`${API_PREFIX}/${id}/documents?page=${page}&limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch documents');
    return response.json();
  },

  async getStatistics(id: string) {
    const response = await fetch(`${API_PREFIX}/${id}/statistics`);
    if (!response.ok) throw new Error('Failed to fetch statistics');
    return response.json();
  },
};
