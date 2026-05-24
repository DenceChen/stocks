import { Card, Table, Tag, Empty } from 'antd'
import { HistoryOutlined, StarOutlined } from '@ant-design/icons'

interface HistoryItem {
  id: string
  stock_code: string
  stock_name: string
  type: 'stock' | 'market' | 'batch'
  risk_preference: string
  timestamp: string
  summary: string
}

const mockHistory: HistoryItem[] = [
  {
    id: '1',
    stock_code: '600519',
    stock_name: '贵州茅台',
    type: 'stock',
    risk_preference: 'low',
    timestamp: '2026-05-24 14:30:00',
    summary: '建议持有，当前估值偏高但业绩稳定...'
  },
  {
    id: '2',
    stock_code: '-',
    stock_name: '市场分析',
    type: 'market',
    risk_preference: 'medium',
    timestamp: '2026-05-24 12:15:00',
    summary: '市场情绪偏向谨慎，建议关注防御性板块...'
  },
  {
    id: '3',
    stock_code: '000858',
    stock_name: '五粮液',
    type: 'stock',
    risk_preference: 'medium',
    timestamp: '2026-05-23 16:45:00',
    summary: '白酒板块短期承压，建议观望...'
  }
]

export default function History() {
  const columns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => (
        <Tag color={type === 'stock' ? 'blue' : type === 'market' ? 'purple' : 'orange'}>
          {type === 'stock' ? '个股' : type === 'market' ? '市场' : '批量'}
        </Tag>
      )
    },
    {
      title: '股票',
      dataIndex: 'stock_name',
      key: 'name',
      render: (name: string, record: HistoryItem) => (
        record.type === 'stock' ? (
          <span>
            <span className="stock-code">{record.stock_code}</span>
            <span style={{ marginLeft: '8px', color: 'var(--text-secondary)' }}>{name}</span>
          </span>
        ) : name
      )
    },
    {
      title: '风险偏好',
      dataIndex: 'risk_preference',
      key: 'risk',
      width: 100,
      render: (risk: string) => {
        const colors: Record<string, string> = { low: 'green', medium: 'orange', high: 'red' }
        return <Tag color={colors[risk]}>{risk === 'low' ? '低' : risk === 'medium' ? '中' : '高'}</Tag>
      }
    },
    {
      title: '摘要',
      dataIndex: 'summary',
      key: 'summary',
      render: (text: string) => (
        <span style={{
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
          color: 'var(--text-secondary)'
        }}>
          {text}
        </span>
      )
    },
    {
      title: '',
      key: 'action',
      width: 50,
      render: () => (
        <StarOutlined style={{ cursor: 'pointer', color: 'var(--text-secondary)' }} />
      )
    }
  ]

  return (
    <div className="animate-slide-in">
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>
          分析历史
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          查看历史分析记录和收藏
        </p>
      </div>

      <Card className="dashboard-card">
        {mockHistory.length > 0 ? (
          <Table
            dataSource={mockHistory}
            columns={columns}
            rowKey="id"
            pagination={{ pageSize: 10 }}
          />
        ) : (
          <Empty
            image={<HistoryOutlined style={{ fontSize: '64px', color: 'var(--text-secondary)' }} />}
            description="暂无历史记录"
          />
        )}
      </Card>
    </div>
  )
}
