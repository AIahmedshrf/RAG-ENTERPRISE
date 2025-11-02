// Adapted from Dify - Apps API Service
import apiAdapter from '../adapters/api-adapter';

const API_PREFIX = '/api/v1/admin/apps';

export const appsAPI = {
  async list(page = 1, limit = 20) {
    const response = await fetch(`${API_PREFIX}?page=${page}&limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch apps');
    return response.json();
  },

  async create(data: { name: string; mode: string; description?: string }) {
    const response = await fetch(`${API_PREFIX}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create app');
    return response.json();
  },

  async get(id: string) {
    const response = await fetch(`${API_PREFIX}/${id}`);
    if (!response.ok) throw new Error('Failed to fetch app');
    return response.json();
  },

  async update(id: string, data: any) {
    const response = await fetch(`${API_PREFIX}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update app');
    return response.json();
  },

  async delete(id: string) {
    const response = await fetch(`${API_PREFIX}/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete app');
  },

  async getStatistics(id: string) {
    const response = await fetch(`${API_PREFIX}/${id}/statistics`);
    if (!response.ok) throw new Error('Failed to fetch statistics');
    return response.json();
  },
};
