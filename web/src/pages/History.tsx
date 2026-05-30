import { useState, useEffect, useCallback } from 'react'
import { Table, Tag, Empty, Button } from 'antd'
import { HistoryOutlined, StarOutlined, StarFilled, ExpandOutlined, ShrinkOutlined, ClockCircleOutlined, DeleteOutlined, ClearOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { getHistory, toggleStar, deleteHistory, clearHistory, HistoryItem } from '../services/history'

const typeLabels: Record<string, string> = { stock: '个股', market: '市场', batch: '批量' }
const riskLabels: Record<string, string> = { low: '低', medium: '中', high: '高' }
const riskColors: Record<string, string> = { low: 'tag-risk-low', medium: 'tag-risk-medium', high: 'tag-risk-high' }

export default function History() {
  const [expandedRows, setExpandedRows] = useState<string[]>([])
  const [items, setItems] = useState<HistoryItem[]>([])

  const refresh = useCallback(() => setItems(getHistory()), [])

  useEffect(() => { refresh() }, [refresh])

  const handleToggleExpand = (id: string) => {
    setExpandedRows(prev =>
      prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id]
    )
  }

  const handleToggleStar = (id: string) => {
    setItems(toggleStar(id))
  }

  const handleDelete = (id: string) => {
    setItems(deleteHistory(id))
    setExpandedRows(prev => prev.filter(r => r !== id))
  }

  const handleClear = () => {
    clearHistory()
    setItems([])
    setExpandedRows([])
  }

  const columns = [
    {
      title: '时间', dataIndex: 'timestamp', key: 'ts', width: 170,
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
      ) : <span>{v}</span>,
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
            icon={expandedRows.includes(r.id) ? <ShrinkOutlined /> : <ExpandOutlined />}
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
          <p>查看历史分析记录和收藏（共 {items.length} 条）</p>
        </div>
        {items.length > 0 && (
          <Button size="small" icon={<ClearOutlined />} onClick={handleClear} danger ghost>
            清空历史
          </Button>
        )}
      </div>

      <div className="card" style={{ padding: 0 }}>
        {items.length > 0 ? (
          <Table
            dataSource={items}
            columns={columns}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            expandable={{
              expandedRowKeys: expandedRows,
              onExpandedRowsChange: (keys) => setExpandedRows(keys as string[]),
              expandIcon: () => null,
              expandedRowRender: (record: HistoryItem) => (
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
                      {record.type === 'stock' ? `${record.stock_name} (${record.stock_code})` : record.stock_name} — 完整分析
                    </span>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                      {record.processing_time && (
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                          耗时 {record.processing_time.toFixed(1)}s
                        </span>
                      )}
                      <span className={`tag ${riskColors[record.risk_preference]}`}>
                        {riskLabels[record.risk_preference]}风险
                      </span>
                    </div>
                  </div>
                  <div className="markdown-body" style={{ fontSize: 14, lineHeight: 1.9 }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {record.full_content || record.summary}
                    </ReactMarkdown>
                  </div>
                  {record.sources && record.sources.length > 0 && (
                    <div style={{
                      marginTop: 16, paddingTop: 12, borderTop: '1px solid var(--border-subtle)',
                    }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                        参考来源 ({record.sources.length})
                      </span>
                      <div style={{ marginTop: 4 }}>
                        {record.sources.map((s, i) => (
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
              ),
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
