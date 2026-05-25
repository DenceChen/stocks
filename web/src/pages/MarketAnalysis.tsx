import { useState, useEffect, useRef } from 'react'
import { Card, Button, Result, Spin, Select } from 'antd'
import { LineChartOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { api } from '../services/api'

const { Option } = Select

export default function MarketAnalysis() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [risk, setRisk] = useState('medium')
  const abortRef = useRef<AbortController | null>(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    return () => { mountedRef.current = false; abortRef.current?.abort() }
  }, [])

  const handleAnalyze = async () => {
    abortRef.current?.abort()
    abortRef.current = new AbortController()
    setLoading(true); setError(null); setResult(null)

    try {
      const res = await api.analyzeMarket({ risk_preference: risk }, { signal: abortRef.current.signal })
      if (mountedRef.current) {
        res.success ? setResult(res.data?.recommendation || '分析完成') : setError(res.error?.message || '分析失败')
      }
    } catch (err: any) {
      if (mountedRef.current && err.name !== 'CanceledError') setError(err.message || '网络错误')
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  }

  return (
    <div className="anim-slide-up">
      <div className="section-header">
        <h2>市场分析</h2>
        <p>AI 全局分析当前市场趋势和热点</p>
      </div>

      <div className="card card-glow" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div>
            <label style={{ display: 'block', marginBottom: 8, color: 'var(--text-muted)', fontSize: 12 }}>风险偏好</label>
            <Select value={risk} onChange={setRisk} style={{ width: 200 }}>
              <Option value="low">低风险偏好</Option>
              <Option value="medium">中风险偏好</Option>
              <Option value="high">高风险偏好</Option>
            </Select>
          </div>
          <Button type="primary" size="large" icon={<LineChartOutlined />} loading={loading} onClick={handleAnalyze}>
            开始分析
          </Button>
        </div>
      </div>

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: 60 }}>
          <Spin size="large" />
          <p style={{ marginTop: 16, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 13 }}>
            <ThunderboltOutlined style={{ color: 'var(--cyan)' }} spin /> 正在分析市场动态，请稍候...
          </p>
          <div style={{ marginTop: 8, width: 200, height: 3, margin: '8px auto 0', borderRadius: 2, overflow: 'hidden', background: 'var(--bg-surface)' }}>
            <div className="shimmer" style={{ height: '100%', width: '100%' }} />
          </div>
          <p style={{ marginTop: 12, fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
            预计耗时 3-5 分钟
          </p>
        </div>
      )}

      {error && (
        <div className="card">
          <Result status="error" title="分析失败" subTitle={error} />
        </div>
      )}

      {result && !loading && (
        <div className="card card-glow anim-slide-up">
          <h3 style={{ marginBottom: 16, fontFamily: 'var(--font-body)', fontWeight: 600 }}>
            📊 市场分析报告
          </h3>
          <div style={{
            padding: 24, background: 'var(--bg-surface)', borderRadius: 8,
            border: '1px solid var(--border-subtle)', lineHeight: 2, whiteSpace: 'pre-wrap',
            fontFamily: 'var(--font-body)', fontSize: 14,
          }}>
            {result}
          </div>
        </div>
      )}
    </div>
  )
}
