import { useState } from 'react'
import { Input, Table, Select } from 'antd'

const mockQuotes = [
  { code: '600519', name: '贵州茅台', price: 1680.00, change: 2.35, amount: 38.50, volume: '325万', turnover: '54.80亿' },
  { code: '000858', name: '五粮液', price: 145.20, change: 1.89, amount: 2.70, volume: '452万', turnover: '65.60亿' },
  { code: '601318', name: '中国平安', price: 48.50, change: 1.56, amount: 0.75, volume: '895万', turnover: '43.40亿' },
  { code: '600036', name: '招商银行', price: 35.80, change: 1.23, amount: 0.44, volume: '523万', turnover: '18.70亿' },
  { code: '000001', name: '平安银行', price: 12.35, change: 0.98, amount: 0.12, volume: '345万', turnover: '42.60亿' },
  { code: '600028', name: '中国石化', price: 5.85, change: 0.52, amount: 0.03, volume: '567万', turnover: '33.20亿' },
  { code: '600000', name: '浦发银行', price: 8.45, change: -0.35, amount: -0.03, volume: '234万', turnover: '19.80亿' },
  { code: '601166', name: '兴业银行', price: 17.25, change: -0.52, amount: -0.09, volume: '412万', turnover: '71.10亿' },
]

export default function Quotes() {
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('change-desc')

  const filtered = mockQuotes
    .filter(s => s.code.includes(search) || s.name.includes(search))
    .sort((a, b) => {
      if (sortBy === 'change-desc') return b.change - a.change
      if (sortBy === 'change-asc') return a.change - b.change
      return 0
    })

  const columns = [
    { title: '代码', dataIndex: 'code', key: 'code', render: (v: string) => <span className="stock-code">{v}</span> },
    { title: '名称', dataIndex: 'name', key: 'name' },
    {
      title: '当前价', dataIndex: 'price', key: 'price',
      render: (v: number) => <span style={{ fontFamily: 'var(--font-mono)' }}>¥{v.toFixed(2)}</span>
    },
    {
      title: '涨跌幅', dataIndex: 'change', key: 'change',
      render: (v: number) => (
        <span className={v >= 0 ? 'price-up' : 'price-down'} style={{ fontFamily: 'var(--font-mono)', fontWeight: 500 }}>
          {v >= 0 ? '+' : ''}{v.toFixed(2)}%
        </span>
      )
    },
    {
      title: '涨跌额', dataIndex: 'amount', key: 'amount',
      render: (v: number) => (
        <span className={v >= 0 ? 'price-up' : 'price-down'} style={{ fontFamily: 'var(--font-mono)' }}>
          {v >= 0 ? '+' : ''}{v.toFixed(2)}
        </span>
      )
    },
    { title: '成交量', dataIndex: 'volume', key: 'vol', render: (v: string) => <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 12 }}>{v}</span> },
    { title: '成交额', dataIndex: 'turnover', key: 'turnover', render: (v: string) => <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 12 }}>{v}</span> },
  ]

  return (
    <div className="anim-slide-up">
      <div className="section-header">
        <h2>实时行情</h2>
        <p>A股实时行情监控</p>
      </div>

      <div className="card" style={{ marginBottom: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
        <Input
          placeholder="搜索股票代码或名称"
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ maxWidth: 300, fontFamily: 'var(--font-mono)' }}
          allowClear
        />
        <Select value={sortBy} onChange={setSortBy} style={{ width: 160 }}>
          <Select.Option value="change-desc">按涨跌幅排序</Select.Option>
          <Select.Option value="change-asc">按跌幅排序</Select.Option>
        </Select>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>
            股票列表 ({filtered.length})
          </span>
        </div>
        <Table dataSource={filtered} columns={columns} rowKey="code" pagination={false} size="small" />
      </div>
    </div>
  )
}
