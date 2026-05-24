import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Spin, Table, Tag } from 'antd'
import { ArrowUpOutlined, ArrowDownOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '../services/api'

interface MarketOverview {
  shIndex: number
  shChange: number
  szIndex: number
  szChange: number
  chgPercent: number
  turnover: string
}

interface RecentStock {
  code: string
  name: string
  price: number
  change: number
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [marketData, setMarketData] = useState<MarketOverview | null>(null)
  const [recentStocks, setRecentStocks] = useState<RecentStock[]>([])

  useEffect(() => {
    fetchMarketData()
  }, [])

  const fetchMarketData = async () => {
    try {
      // 模拟市场数据
      setMarketData({
        shIndex: 3152.98,
        shChange: 45.32,
        szIndex: 10234.56,
        szChange: 123.45,
        chgPercent: 1.28,
        turnover: '8926亿'
      })

      setRecentStocks([
        { code: '600519', name: '贵州茅台', price: 1680.50, change: 2.35 },
        { code: '000858', name: '五粮液', price: 145.20, change: -1.28 },
        { code: '601318', name: '中国平安', price: 48.50, change: 0.85 },
        { code: '600036', name: '招商银行', price: 35.80, change: 1.52 },
        { code: '300750', name: '宁德时代', price: 182.30, change: 3.21 },
      ])

      setLoading(false)
    } catch (error) {
      console.error('获取市场数据失败:', error)
      setLoading(false)
    }
  }

  const columns = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      render: (code: string) => <span className="stock-code">{code}</span>
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => <span className="stock-name">{name}</span>
    },
    {
      title: '最新价',
      dataIndex: 'price',
      key: 'price',
      render: (price: number) => `¥${price.toFixed(2)}`
    },
    {
      title: '涨跌幅',
      dataIndex: 'change',
      key: 'change',
      render: (change: number) => (
        <span className={change >= 0 ? 'price-up' : 'price-down'}>
          {change >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
          {Math.abs(change).toFixed(2)}%
        </span>
      )
    }
  ]

  const mockChartData = [
    { time: '09:30', index: 3100 },
    { time: '10:00', index: 3115 },
    { time: '10:30', index: 3125 },
    { time: '11:00', index: 3130 },
    { time: '11:30', index: 3140 },
    { time: '13:00', index: 3145 },
    { time: '13:30', index: 3148 },
    { time: '14:00', index: 3150 },
    { time: '14:30', index: 3155 },
    { time: '15:00', index: 3153 },
  ]

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div className="animate-slide-in">
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>
          市场概览
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          实时追踪 A 股市场动态
        </p>
      </div>

      {/* 指数卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <div className="dashboard-card">
            <Statistic
              title={<span style={{ color: 'var(--text-secondary)' }}>上证指数</span>}
              value={marketData?.shIndex}
              precision={2}
              suffix={<span style={{ fontSize: '14px' }}>点</span>}
            />
            <div className={marketData!.shChange >= 0 ? 'price-up' : 'price-down'} style={{ marginTop: '8px' }}>
              {marketData!.shChange >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              {' '}{Math.abs(marketData!.shChange).toFixed(2)} ({marketData!.shChange >= 0 ? '+' : ''}{marketData!.chgPercent.toFixed(2)}%)
            </div>
          </div>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <div className="dashboard-card">
            <Statistic
              title={<span style={{ color: 'var(--text-secondary)' }}>深证成指</span>}
              value={marketData?.szIndex}
              precision={2}
              suffix={<span style={{ fontSize: '14px' }}>点</span>}
            />
            <div className={marketData!.szChange >= 0 ? 'price-up' : 'price-down'} style={{ marginTop: '8px' }}>
              {marketData!.szChange >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              {' '}{Math.abs(marketData!.szChange).toFixed(2)}
            </div>
          </div>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <div className="dashboard-card">
            <Statistic
              title={<span style={{ color: 'var(--text-secondary)' }}>成交额</span>}
              value={marketData?.turnover}
              prefix={<ThunderboltOutlined />}
            />
            <div style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
              市场活跃度较高
            </div>
          </div>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <div className="dashboard-card">
            <Statistic
              title={<span style={{ color: 'var(--text-secondary)' }}>上涨家数</span>}
              value={3245}
              valueStyle={{ color: 'var(--accent-green)' }}
            />
            <Tag color="green" style={{ marginTop: '8px' }}>强势</Tag>
          </div>
        </Col>
      </Row>

      {/* 图表和表格 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <div className="dashboard-card" style={{ height: '400px' }}>
            <h3 style={{ marginBottom: '16px' }}>上证指数走势</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockChartData}>
                <XAxis
                  dataKey="time"
                  axisLine={{ stroke: 'var(--border-color)' }}
                  tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                />
                <YAxis
                  domain={['auto', 'auto']}
                  axisLine={{ stroke: 'var(--border-color)' }}
                  tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-secondary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '4px'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="index"
                  stroke="var(--accent-green)"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Col>
        <Col xs={24} lg={10}>
          <div className="dashboard-card" style={{ height: '400px' }}>
            <h3 style={{ marginBottom: '16px' }}>热门股票</h3>
            <Table
              dataSource={recentStocks}
              columns={columns}
              rowKey="code"
              pagination={false}
              size="small"
            />
          </div>
        </Col>
      </Row>
    </div>
  )
}
