import request from './index'

export const agentApi = {
  chat: (data: { message: string; project_id?: string; context?: any }) =>
    request.post('/api/v1/agent/chat', data),
  demoChat: (data: { message: string; agent?: string; context?: any }) =>
    request.post('/api/v1/agent/demo-chat', data),
  getDemoCase: () => request.get('/api/v1/agent/demo-case'),
  getDemoProject: () => request.get('/api/v1/agent/demo-project'),
  getHistory: (params?: { limit?: number; offset?: number }) =>
    request.get('/api/v1/agent/history', { params }),
  clearHistory: () => request.delete('/api/v1/agent/history'),
  saveToProject: (data: any) => request.post('/api/v1/agent/save-to-project', data),
}
