import { useState } from 'react'
import { Card, Button, Result, Spin, Select } from 'antd'
import { LineChartOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { api } from '../services/api'

const { Option } = Select

export default function MarketAnalysis() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [risk, setRisk] = useState('medium')

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await api.analyzeMarket({ risk_preference: risk })
      if (response.success) {
        setResult(response.data?.recommendation || '分析完成')
      } else {
        setError(response.error?.message || '分析失败')
      }
    } catch (err: any) {
      setError(err.message || '网络错误')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-slide-in">
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>
          市场分析
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          AI 全局分析当前市场趋势和热点
        </p>
      </div>

      <Card className="dashboard-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)' }}>
              风险偏好
            </label>
            <Select value={risk} onChange={setRisk} style={{ width: 200 }}>
              <Option value="low">低风险偏好</Option>
              <Option value="medium">中风险偏好</Option>
              <Option value="high">高风险偏好</Option>
            </Select>
          </div>
          <Button
            type="primary"
            size="large"
            icon={<LineChartOutlined />}
            loading={loading}
            onClick={handleAnalyze}
            style={{
              background: 'var(--accent-green)',
              borderColor: 'var(--accent-green)'
            }}
          >
            开始分析
          </Button>
        </div>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Spin size="large" />
          <p style={{ marginTop: '16px', color: 'var(--text-secondary)' }}>
            <ThunderboltOutlined spin style={{ color: 'var(--accent-green)' }} />
            {' '}正在分析市场动态，请稍候...
          </p>
        </div>
      )}

      {error && (
        <Result
          status="error"
          title="分析失败"
          subTitle={error}
        />
      )}

      {result && !loading && (
        <Card className="dashboard-card animate-slide-in">
          <h3 style={{ marginBottom: '16px' }}>市场分析报告</h3>
          <div style={{
            padding: '20px',
            background: 'var(--bg-tertiary)',
            borderRadius: '8px',
            lineHeight: 2,
            whiteSpace: 'pre-wrap'
          }}>
            {result}
          </div>
        </Card>
      )}
    </div>
  )
}
