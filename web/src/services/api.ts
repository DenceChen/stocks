import axios from 'axios'
import { getToken } from './auth'

const BASE_URL = '/api/v1'

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 600000,
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  response => response.data,
  error => {
    if (axios.isCancel(error)) {
      console.log('Request canceled')
      return Promise.reject({ name: 'CanceledError', message: 'Request canceled' })
    }
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export type SSEEvent = {
  type: string
  data: any
}

async function parseSSE(
  url: string,
  body: any,
  onEvent: (event: SSEEvent) => void
): Promise<void> {
  const token = getToken()
  const separator = url.includes('?') ? '&' : '?'
  const fullUrl = token ? `${url}${separator}token=${encodeURIComponent(token)}` : url

  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(fullUrl, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })

    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    let currentEvent = ''
    let currentData = ''

    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim()
      } else if (line.startsWith('data: ')) {
        currentData += (currentData ? '\n' : '') + line.slice(6)
      } else if (line === '' && currentEvent && currentData) {
        try {
          const parsed = JSON.parse(currentData)
          onEvent({ type: currentEvent, data: parsed })
        } catch {
          onEvent({ type: currentEvent, data: currentData })
        }
        currentEvent = ''
        currentData = ''
      }
    }
  }

  // Handle remaining buffer
  if (buffer.trim()) {
    const lines = buffer.split('\n')
    let evt = '', dat = ''
    for (const line of lines) {
      if (line.startsWith('event: ')) evt = line.slice(7).trim()
      else if (line.startsWith('data: ')) dat = line.slice(6)
    }
    if (evt && dat) {
      try { onEvent({ type: evt, data: JSON.parse(dat) }) } catch { onEvent({ type: evt, data: dat }) }
    }
  }
}

export const api = {
  healthCheck: () => apiClient.get('/health'),
  getQuote: (code: string) => apiClient.get(`/quote/${code}`),
  getRealtimeQuotes: (codes: string[]) =>
    apiClient.get('/quotes/realtime', { params: { codes: codes.join(',') } }),
  getFinancials: (code: string) => apiClient.get(`/financials/${code}`),
  getKline: (code: string, period = 'daily', adjust = 'qfq') =>
    apiClient.get(`/kline/${code}`, { params: { period, adjust } }),

  analyzeStock: (data: {
    stock_code: string; stock_name?: string; risk_preference?: string; max_urls?: number
  }, options?: { signal?: AbortSignal }) => apiClient.post('/analyze/stock', data, options),

  analyzeMarket: (data: {
    search_queries?: string[]; risk_preference?: string; max_urls?: number
  }, options?: { signal?: AbortSignal }) => apiClient.post('/analyze/market', data, options),

  analyzeBatch: (data: {
    stocks: Array<{ code: string; name?: string }>; risk_preference?: string; max_urls_per_stock?: number
  }, options?: { signal?: AbortSignal }) => apiClient.post('/analyze/batch', data, options),

  getTaskStatus: (taskId: string) => apiClient.get(`/tasks/${taskId}`),

  streamAnalyzeStock: (
    data: { stock_code: string; stock_name?: string; risk_preference?: string; max_urls?: number },
    onEvent: (event: SSEEvent) => void
  ) => parseSSE(`${BASE_URL}/analyze/stock/stream`, data, onEvent),

  streamAnalyzeMarket: (
    data: { search_queries?: string[]; risk_preference?: string; max_urls?: number },
    onEvent: (event: SSEEvent) => void
  ) => parseSSE(`${BASE_URL}/analyze/market/stream`, data, onEvent),

  // History API
  getHistory: (params?: { page?: number; page_size?: number; type?: string; starred_only?: boolean }) =>
    apiClient.get('/history', { params }),
  getHistoryDetail: (id: number) => apiClient.get(`/history/${id}`),
  toggleStar: (id: number) => apiClient.put(`/history/${id}/star`),
  deleteHistory: (id: number) => apiClient.delete(`/history/${id}`),
}
