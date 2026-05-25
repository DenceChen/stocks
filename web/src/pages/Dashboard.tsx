import { useState, useEffect } from 'react'
import { Spin, Table } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '../services/api'

interface MarketData {
  shIndex: number; shChange: number; shPercent: number
  szIndex: number; szChange: number; szPercent: number
  turnover: string; upCount: number; downCount: number
}

interface HotStock {
  code: string; name: string; price: number; change: number; volume: string
}

interface RecentAnalysis {
  name: string; code: string; time: string; risk: string
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [market, setMarket] = useState<MarketData | null>(null)
  const [hotStocks, setHotStocks] = useState<HotStock[]>([])
  const [recent] = useState<RecentAnalysis[]>([
    { name: '贵州茅台', code: '600519', time: '10分钟前', risk: 'low' },
    { name: '五粮液', code: '000858', time: '25分钟前', risk: 'low' },
    { name: '中国平安', code: '601318', time: '1小时前', risk: 'medium' },
  ])

  const chartData = [
    { t: '09:30', v: 3100 }, { t: '10:00', v: 3115 },
    { t: '10:30', v: 3125 }, { t: '11:00', v: 3130 },
    { t: '11:30', v: 3140 }, { t: '13:00', v: 3145 },
    { t: '13:30', v: 3148 }, { t: '14:00', v: 3150 },
    { t: '14:30', v: 3155 }, { t: '15:00', v: 3153 },
  ]

  useEffect(() => {
    setMarket({
      shIndex: 3215.47, shChange: 26.89, shPercent: 0.85,
      szIndex: 10835.28, szChange: 120.15, szPercent: 1.12,
      turnover: '4528亿', upCount: 2847, downCount: 1235,
    })
    setHotStocks([
      { code: '600519', name: '贵州茅台', price: 1680.00, change: 2.35, volume: '54.8亿' },
      { code: '000858', name: '五粮液', price: 145.20, change: 1.89, volume: '65.6亿' },
      { code: '601318', name: '中国平安', price: 48.50, change: 1.56, volume: '43.4亿' },
      { code: '600036', name: '招商银行', price: 35.80, change: 1.23, volume: '18.7亿' },
      { code: '000001', name: '平安银行', price: 12.35, change: 0.98, volume: '42.6亿' },
      { code: '600028', name: '中国石化', price: 5.85, change: 0.52, volume: '33.2亿' },
      { code: '600000', name: '浦发银行', price: 8.45, change: -0.35, volume: '19.8亿' },
      { code: '601166', name: '兴业银行', price: 17.25, change: -0.52, volume: '71.1亿' },
    ])
    setLoading(false)
  }, [])

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Spin size="large" />
      </div>
    )
  }

  const columns = [
    {
      title: '排名', key: 'rank', width: 50,
      render: (_: any, __: any, i: number) => (
        <span style={{
          fontFamily: 'var(--font-mono)', fontSize: 11, color: i < 3 ? 'var(--cyan)' : 'var(--text-dim)',
          fontWeight: i < 3 ? 600 : 400,
        }}>{i + 1}</span>
      )
    },
    { title: '代码', dataIndex: 'code', key: 'code', render: (v: string) => <span className="stock-code">{v}</span> },
    { title: '名称', dataIndex: 'name', key: 'name' },
    {
      title: '最新价', dataIndex: 'price', key: 'price',
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
      title: '成交额', dataIndex: 'volume', key: 'vol',
      render: (v: string) => <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 12 }}>{v}</span>
    },
  ]

  const indexCards = market ? [
    { label: '上证指数', value: market.shIndex, change: market.shChange, percent: market.shPercent, unit: '点' },
    { label: '深证成指', value: market.szIndex, change: market.szChange, percent: market.szPercent, unit: '点' },
    { label: '成交额', value: market.turnover, change: null, percent: null, unit: '' },
    { label: '上涨/下跌', value: `${market.upCount}`, sub: `/${market.downCount}`, change: null, percent: null, unit: '家' },
  ] : []

  return (
    <div className="anim-slide-up">
      <div className="section-header">
        <h2>市场仪表盘</h2>
        <p>实时监控市场动态 <span className="pulse-dot" style={{ marginLeft: 8 }} /></p>
      </div>

      {/* Index Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12, marginBottom: 24 }}>
        {indexCards.map((card, i) => (
          <div key={i} className={`card card-glow anim-slide-up stagger-${i + 1}`} style={{ position: 'relative', overflow: 'hidden' }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginBottom: 8, letterSpacing: .5, textTransform: 'uppercase' }}>
              {card.label}
              {i < 2 && <span className="pulse-dot" style={{ marginLeft: 6, width: 4, height: 4 }} />}
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 4 }}>
              <span style={{
                fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 700, color: 'var(--text-bright)',
                lineHeight: 1,
              }}>
                {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
              </span>
              {card.sub && <span style={{ color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', fontSize: 16 }}>{card.sub}</span>}
              {card.unit && <span style={{ fontSize: 12, color: 'var(--text-dim)', marginLeft: 2 }}>{card.unit}</span>}
            </div>
            {card.change !== null && (
              <div className={card.change >= 0 ? 'price-up' : 'price-down'} style={{
                fontFamily: 'var(--font-mono)', fontSize: 12, marginTop: 6, display: 'flex', alignItems: 'center', gap: 4,
              }}>
                {card.change >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                {Math.abs(card.change).toFixed(2)}
                <span style={{ opacity: .7 }}>({card.change >= 0 ? '+' : ''}{card.percent!.toFixed(2)}%)</span>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Chart + Table */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 12, marginBottom: 24 }}>
        <div className="card card-glow" style={{ padding: 0 }}>
          <div style={{ padding: '16px 20px 8px' }}>
            <span style={{ fontFamily: 'var(--font-body)', fontWeight: 600, fontSize: 14, color: 'var(--text-bright)' }}>
              🔥 热门股票
            </span>
          </div>
          <Table dataSource={hotStocks} columns={columns} rowKey="code" pagination={false} size="small" />
        </div>
        <div className="card card-glow">
          <div style={{ marginBottom: 12 }}>
            <span style={{ fontFamily: 'var(--font-body)', fontWeight: 600, fontSize: 14, color: 'var(--text-bright)' }}>
              上证走势
            </span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00e5cc" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#00e5cc" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="t" axisLine={false} tickLine={false} tick={{ fill: '#3a4a5e', fontSize: 11 }} />
              <YAxis hide domain={['data - 20', 'data + 20']} />
              <Tooltip
                contentStyle={{
                  background: 'rgba(11, 17, 32, 0.95)', border: '1px solid rgba(0,229,204,0.2)',
                  borderRadius: 8, fontFamily: 'var(--font-mono)', fontSize: 12,
                }}
                labelStyle={{ color: 'var(--text-muted)' }}
                itemStyle={{ color: 'var(--cyan)' }}
              />
              <Area type="monotone" dataKey="v" stroke="#00e5cc" strokeWidth={2} fill="url(#areaGrad)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent + Quick Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div className="card card-glow">
          <div style={{ fontFamily: 'var(--font-body)', fontWeight: 600, fontSize: 14, color: 'var(--text-bright)', marginBottom: 16 }}>
            最近分析
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {recent.map((item, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '10px 12px', borderRadius: 8,
                background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)',
              }}>
                <div>
                  <div style={{ fontWeight: 500, fontSize: 13, color: 'var(--text-bright)' }}>{item.name}</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>{item.code}</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: 11, color: 'var(--text-dim)' }}>{item.time}</div>
                  <span className={`tag tag-risk-${item.risk}`}>
                    {item.risk === 'low' ? '低风险' : item.risk === 'medium' ? '中风险' : '高风险'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card card-glow">
          <div style={{ fontFamily: 'var(--font-body)', fontWeight: 600, fontSize: 14, color: 'var(--text-bright)', marginBottom: 16 }}>
            快速操作
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            {[
              { icon: '📊', label: '个股分析', path: '/stock' },
              { icon: '🌐', label: '市场分析', path: '/market' },
              { icon: '📦', label: '批量分析', path: '/batch' },
              { icon: '📈', label: '实时行情', path: '/quotes' },
            ].map((action, i) => (
              <div key={i} className="action-card" onClick={() => window.location.href = action.path}>
                <div className="action-icon">{action.icon}</div>
                <div className="action-label">{action.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
