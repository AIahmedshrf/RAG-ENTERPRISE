export const API = {
  BASE: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  DOCUMENTS: '/documents',
  KNOWLEDGE: '/knowledge',
  AGENTS: '/agents',
  AUTH: '/auth',
}

export function endpoint(path: string) {
  // ensure leading slash
  if (!path.startsWith('/')) path = '/' + path
  return `${API.BASE}${path}`
}
