import { Table, Tag, Empty } from 'antd'
import { HistoryOutlined, StarOutlined } from '@ant-design/icons'

interface HistoryItem {
  id: string; stock_code: string; stock_name: string
  type: 'stock' | 'market' | 'batch'; risk_preference: string
  timestamp: string; summary: string
}

const mockHistory: HistoryItem[] = [
  { id: '1', stock_code: '600519', stock_name: '贵州茅台', type: 'stock', risk_preference: 'low', timestamp: '2026-05-24 14:30:00', summary: '建议持有，当前估值偏高但业绩稳定...' },
  { id: '2', stock_code: '-', stock_name: '市场分析', type: 'market', risk_preference: 'medium', timestamp: '2026-05-24 12:15:00', summary: '市场情绪偏向谨慎，建议关注防御性板块...' },
  { id: '3', stock_code: '000858', stock_name: '五粮液', type: 'stock', risk_preference: 'medium', timestamp: '2026-05-23 16:45:00', summary: '白酒板块短期承压，建议观望...' },
]

const typeLabels: Record<string, string> = { stock: '个股', market: '市场', batch: '批量' }
const riskLabels: Record<string, string> = { low: '低', medium: '中', high: '高' }

export default function History() {
  const columns = [
    { title: '时间', dataIndex: 'timestamp', key: 'ts', width: 170, render: (v: string) => <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>{v}</span> },
    {
      title: '类型', dataIndex: 'type', key: 'type', width: 80,
      render: (v: string) => <span className={`tag tag-risk-${v === 'stock' ? 'low' : v === 'market' ? 'medium' : 'high'}`}>{typeLabels[v]}</span>
    },
    {
      title: '股票', dataIndex: 'stock_name', key: 'name',
      render: (v: string, r: HistoryItem) => r.type === 'stock' ? (
        <span><span className="stock-code">{r.stock_code}</span> <span style={{ color: 'var(--text-muted)', marginLeft: 6 }}>{v}</span></span>
      ) : <span>{v}</span>
    },
    {
      title: '风险偏好', dataIndex: 'risk_preference', key: 'risk', width: 80,
      render: (v: string) => <span className={`tag tag-risk-${v}`}>{riskLabels[v]}</span>
    },
    {
      title: '摘要', dataIndex: 'summary', key: 'summary',
      render: (v: string) => <span style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', color: 'var(--text-muted)', fontSize: 12 }}>{v}</span>
    },
    { title: '', key: 'action', width: 40, render: () => <StarOutlined style={{ cursor: 'pointer', color: 'var(--text-dim)' }} /> },
  ]

  return (
    <div className="anim-slide-up">
      <div className="section-header">
        <h2>分析历史</h2>
        <p>查看历史分析记录和收藏</p>
      </div>

      <div className="card" style={{ padding: 0 }}>
        {mockHistory.length > 0 ? (
          <Table dataSource={mockHistory} columns={columns} rowKey="id" pagination={{ pageSize: 10 }} />
        ) : (
          <div style={{ padding: 60, textAlign: 'center' }}>
            <Empty image={<HistoryOutlined style={{ fontSize: 48, color: 'var(--text-dim)' }} />} description={<span style={{ color: 'var(--text-muted)' }}>暂无历史记录</span>} />
          </div>
        )}
      </div>
    </div>
  )
}
