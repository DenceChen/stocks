import axios from 'axios'

const BASE_URL = '/api/v1'

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const api = {
  // 健康检查
  healthCheck: () => apiClient.get('/health'),

  // 股票行情
  getQuote: (code: string) => apiClient.get(`/quote/${code}`),

  // 批量行情
  getRealtimeQuotes: (codes: string[]) =>
    apiClient.get('/quotes/realtime', { params: { codes: codes.join(',') } }),

  // 财务数据
  getFinancials: (code: string) => apiClient.get(`/financials/${code}`),

  // K线数据
  getKline: (code: string, period = 'daily', adjust = 'qfq') =>
    apiClient.get(`/kline/${code}`, { params: { period, adjust } }),

  // 单股分析
  analyzeStock: (data: {
    stock_code: string
    stock_name?: string
    risk_preference?: string
    max_urls?: number
  }) => apiClient.post('/analyze/stock', data),

  // 市场分析
  analyzeMarket: (data: {
    search_queries?: string[]
    risk_preference?: string
    max_urls?: number
  }) => apiClient.post('/analyze/market', data),

  // 批量分析
  analyzeBatch: (data: {
    stocks: Array<{ code: string; name?: string }>
    risk_preference?: string
    max_urls_per_stock?: number
  }) => apiClient.post('/analyze/batch', data),

  // 任务状态
  getTaskStatus: (taskId: string) => apiClient.get(`/tasks/${taskId}`)
}
