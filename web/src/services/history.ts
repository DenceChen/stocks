const STORAGE_KEY = 'stocks_analysis_history'

export interface HistoryItem {
  id: string
  stock_code: string
  stock_name: string
  type: 'stock' | 'market' | 'batch'
  risk_preference: string
  timestamp: string
  summary: string
  full_content?: string
  processing_time?: number
  sources?: string[]
  starred?: boolean
}

export function getHistory(): HistoryItem[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveHistory(items: HistoryItem[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
}

export function addHistory(item: Omit<HistoryItem, 'id' | 'starred'>): HistoryItem {
  const record: HistoryItem = {
    ...item,
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
    starred: false,
  }
  const items = getHistory()
  items.unshift(record)
  if (items.length > 200) items.length = 200
  saveHistory(items)
  return record
}

export function toggleStar(id: string) {
  const items = getHistory()
  const item = items.find(i => i.id === id)
  if (item) {
    item.starred = !item.starred
    saveHistory(items)
  }
  return items
}

export function deleteHistory(id: string) {
  const items = getHistory().filter(i => i.id !== id)
  saveHistory(items)
  return items
}

export function clearHistory() {
  saveHistory([])
}
