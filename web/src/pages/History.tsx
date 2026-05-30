import { useState, useEffect, useCallback } from 'react'
import { Table, Tag, Empty, Button, message, Spin } from 'antd'
import { HistoryOutlined, StarOutlined, StarFilled, ExpandOutlined, ShrinkOutlined, ClockCircleOutlined, DeleteOutlined, ClearOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api } from '../services/api'

const typeLabels: Record<string, string> = { stock: '个股', market: '市场', batch: '批量' }
const riskLabels: Record<string, string> = { low: '低', medium: '中', high: '高' }
const riskColors: Record<string, string> = { low: 'tag-risk-low', medium: 'tag-risk-medium', high: 'tag-risk-high' }

interface HistoryItem {
  id: number
  type: string
  stock_code: string
  stock_name: string
  risk_preference: string
  summary: string
  full_content?: string
  processing_time?: number
  sources?: string[]
  starred: boolean
  created_at: string
}

export default function History() {
  const [expandedRows, setExpandedRows] = useState<number[]>([])
  const [items, setItems] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(false)
  const [detailLoading, setDetailLoading] = useState<number | null>(null)
  const [details, setDetails] = useState<Record<number, HistoryItem>>({})
  const [totalCount, setTotalCount] = useState(0)
  const [page, setPage] = useState(1)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const res: any = await api.getHistory({ page, page_size: 10 })
      if (res.success) {
        setItems(res.data.items)
        setTotalCount(res.data.total_count)
      }
    } catch {
      message.error('加载历史记录失败')
    } finally {
      setLoading(false)
    }
  }, [page])

  useEffect(() => { refresh() }, [refresh])

  const handleToggleExpand = async (id: number) => {
    if (expandedRows.includes(id)) {
      setExpandedRows(prev => prev.filter(r => r !== id))
      return
    }

    // Load full content if not cached
    if (!details[id]) {
      setDetailLoading(id)
      try {
        const res: any = await api.getHistoryDetail(id)
        if (res.success) {
          setDetails(prev => ({ ...prev, [id]: res.data }))
        }
      } catch {
        message.error('加载详情失败')
      } finally {
        setDetailLoading(null)
      }
    }
    setExpandedRows(prev => [...prev, id])
  }

  const handleToggleStar = async (id: number) => {
    try {
      await api.toggleStar(id)
      setItems(prev => prev.map(item =>
        item.id === id ? { ...item, starred: !item.starred } : item
      ))
    } catch {
      message.error('操作失败')
    }
  }

  const handleDelete = async (id: number) => {
    try {
      await api.deleteHistory(id)
      setItems(prev => prev.filter(item => item.id !== id))
      setExpandedRows(prev => prev.filter(r => r !== id))
      setTotalCount(prev => prev - 1)
    } catch {
      message.error('删除失败')
    }
  }

  const handleClear = async () => {
    // Delete all items one by one
    try {
      for (const item of items) {
        await api.deleteHistory(item.id)
      }
      setItems([])
      setExpandedRows([])
      setDetails({})
      setTotalCount(0)
      message.success('历史已清空')
    } catch {
      message.error('清空失败')
    }
  }

  const columns = [
    {
      title: '时间', dataIndex: 'created_at', key: 'ts', width: 170,
      render: (v: string) => (
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>
          <ClockCircleOutlined style={{ marginRight: 6, fontSize: 10 }} />{v}
        </span>
      ),
    },
    {
      title: '类型', dataIndex: 'type', key: 'type', width: 80,
      render: (v: string) => <span className={`tag tag-risk-${v === 'stock' ? 'low' : v === 'market' ? 'medium' : 'high'}`}>{typeLabels[v]}</span>,
    },
    {
      title: '股票', dataIndex: 'stock_name', key: 'name',
      render: (v: string, r: HistoryItem) => r.type === 'stock' ? (
        <span><span className="stock-code">{r.stock_code}</span> <span style={{ color: 'var(--text-muted)', marginLeft: 6 }}>{v}</span></span>
      ) : <span>{v || '市场分析'}</span>,
    },
    {
      title: '风险偏好', dataIndex: 'risk_preference', key: 'risk', width: 80,
      render: (v: string) => <span className={`tag ${riskColors[v]}`}>{riskLabels[v]}</span>,
    },
    {
      title: '摘要', dataIndex: 'summary', key: 'summary',
      render: (v: string) => (
        <span style={{
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
          overflow: 'hidden', color: 'var(--text-muted)', fontSize: 12,
        }}>
          {v}
        </span>
      ),
    },
    {
      title: '', key: 'actions', width: 120,
      render: (_: unknown, r: HistoryItem) => (
        <div style={{ display: 'flex', gap: 4 }}>
          <Button
            type="text" size="small"
            icon={detailLoading === r.id ? <Spin size="small" /> : expandedRows.includes(r.id) ? <ShrinkOutlined /> : <ExpandOutlined />}
            onClick={(e) => { e.stopPropagation(); handleToggleExpand(r.id) }}
            style={{ color: 'var(--cyan)', fontSize: 13 }}
          />
          <Button
            type="text" size="small"
            icon={r.starred ? <StarFilled /> : <StarOutlined />}
            onClick={(e) => { e.stopPropagation(); handleToggleStar(r.id) }}
            style={{ color: r.starred ? 'var(--amber)' : 'var(--text-dim)', fontSize: 13 }}
          />
          <Button
            type="text" size="small"
            icon={<DeleteOutlined />}
            onClick={(e) => { e.stopPropagation(); handleDelete(r.id) }}
            style={{ color: 'var(--red)', fontSize: 13, opacity: 0.6 }}
          />
        </div>
      ),
    },
  ]

  return (
    <div className="anim-slide-up">
      <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h2>分析历史</h2>
          <p>查看历史分析记录和收藏（共 {totalCount} 条）</p>
        </div>
        {items.length > 0 && (
          <Button size="small" icon={<ClearOutlined />} onClick={handleClear} danger ghost>
            清空当前页
          </Button>
        )}
      </div>

      <div className="card" style={{ padding: 0 }}>
        {items.length > 0 || loading ? (
          <Table
            dataSource={items}
            columns={columns}
            rowKey="id"
            loading={loading}
            pagination={{
              current: page,
              pageSize: 10,
              total: totalCount,
              onChange: (p) => setPage(p),
              showSizeChanger: false,
            }}
            expandable={{
              expandedRowKeys: expandedRows,
              onExpandedRowsChange: (keys) => setExpandedRows(keys as number[]),
              expandIcon: () => null,
              expandedRowRender: (record: HistoryItem) => {
                const detail = details[record.id]
                const content = detail?.full_content || record.summary
                return (
                  <div style={{
                    margin: '4px 0',
                    padding: 20,
                    background: 'var(--bg-surface)',
                    borderRadius: 8,
                    border: '1px solid var(--border-subtle)',
                  }}>
                    <div style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      marginBottom: 16, paddingBottom: 12, borderBottom: '1px solid var(--border-subtle)',
                    }}>
                      <span style={{
                        fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 600,
                        color: 'var(--text-bright)',
                      }}>
                        {record.type === 'stock' ? `${record.stock_name} (${record.stock_code})` : '市场分析'} — 完整分析
                      </span>
                      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        {(detail?.processing_time ?? record.processing_time) && (
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                            耗时 {(detail?.processing_time ?? record.processing_time!)!.toFixed(1)}s
                          </span>
                        )}
                        <span className={`tag ${riskColors[record.risk_preference]}`}>
                          {riskLabels[record.risk_preference]}风险
                        </span>
                      </div>
                    </div>
                    <div className="markdown-body" style={{ fontSize: 14, lineHeight: 1.9 }}>
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {content}
                      </ReactMarkdown>
                    </div>
                    {(detail?.sources ?? record.sources) && (detail?.sources ?? record.sources)!.length > 0 && (
                      <div style={{
                        marginTop: 16, paddingTop: 12, borderTop: '1px solid var(--border-subtle)',
                      }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                          参考来源 ({(detail?.sources ?? record.sources)!.length})
                        </span>
                        <div style={{ marginTop: 4 }}>
                          {(detail?.sources ?? record.sources)!.map((s, i) => (
                            <a key={i} href={s} target="_blank" rel="noopener noreferrer" style={{
                              display: 'block', fontSize: 11, color: 'var(--blue)', fontFamily: 'var(--font-mono)',
                              marginBottom: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                            }}>
                              {i + 1}. {s}
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              },
            }}
          />
        ) : (
          <div style={{ padding: 60, textAlign: 'center' }}>
            <Empty image={<HistoryOutlined style={{ fontSize: 48, color: 'var(--text-dim)' }} />} description={<span style={{ color: 'var(--text-muted)' }}>暂无历史记录，完成一次分析后将自动保存</span>} />
          </div>
        )}
      </div>
    </div>
  )
}
