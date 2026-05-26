import { useState } from 'react'
import { Button, Select, Tag } from 'antd'
import { LineChartOutlined, ThunderboltOutlined, LoadingOutlined } from '@ant-design/icons'
import { api } from '../services/api'

const { Option } = Select

const STAGE_MAP: Record<string, string> = {
  searching: '搜索市场信息',
  crawling: '爬取网页',
  extracting: '提取关键信息',
  generating: 'AI 生成分析报告',
}

export default function MarketAnalysis() {
  const [loading, setLoading] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  const [stage, setStage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [sources, setSources] = useState<string[]>([])
  const [processingTime, setProcessingTime] = useState<number | null>(null)
  const [risk, setRisk] = useState('medium')

  const handleAnalyze = async () => {
    setLoading(true); setError(null); setStreamingText('')
    setStage('searching'); setSources([]); setProcessingTime(null)

    try {
      await api.streamAnalyzeMarket({ risk_preference: risk }, (event) => {
        switch (event.type) {
          case 'status':
            setStage(event.data.stage)
            break
          case 'text':
            setStreamingText(prev => prev + event.data.content)
            break
          case 'done':
            setSources(event.data.sources || [])
            setProcessingTime(event.data.processing_time)
            setLoading(false); setStage(null)
            break
          case 'error':
            setError(event.data.message || '分析失败')
            setLoading(false); setStage(null)
            break
        }
      })
    } catch (err: any) {
      setError(err.message || '网络错误')
      setLoading(false); setStage(null)
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

      {error && (
        <div className="card" style={{ marginBottom: 24, padding: 20, color: 'var(--red)', fontFamily: 'var(--font-body)' }}>
          <strong>分析失败：</strong>{error}
        </div>
      )}

      {loading && stage && !streamingText && (
        <div className="card card-glow" style={{ marginBottom: 24, textAlign: 'center', padding: 40 }}>
          <LoadingOutlined style={{ fontSize: 32, color: 'var(--cyan)' }} spin />
          <p style={{ marginTop: 16, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 13 }}>
            <ThunderboltOutlined style={{ color: 'var(--cyan)' }} /> {STAGE_MAP[stage] || stage}...
          </p>
          <div style={{ marginTop: 8, width: 200, height: 3, margin: '8px auto 0', borderRadius: 2, overflow: 'hidden', background: 'var(--bg-surface)' }}>
            <div className="shimmer" style={{ height: '100%', width: '100%' }} />
          </div>
          <p style={{ marginTop: 12, fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
            预计耗时 1-3 分钟
          </p>
        </div>
      )}

      {streamingText && (
        <div className="card card-glow anim-slide-up">
          <h3 style={{ marginBottom: 16, fontFamily: 'var(--font-body)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            市场分析报告
            {loading && <Tag color="processing" style={{ fontSize: 11 }}>生成中</Tag>}
          </h3>
          <div className={loading ? 'streaming-cursor' : ''} style={{
            padding: 24, background: 'var(--bg-surface)', borderRadius: 8,
            border: '1px solid var(--border-subtle)', lineHeight: 2, whiteSpace: 'pre-wrap',
            fontFamily: 'var(--font-body)', fontSize: 14,
          }}>
            {streamingText}
          </div>
          {processingTime !== null && !loading && (
            <div style={{ marginTop: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                分析耗时: {processingTime.toFixed(2)}s
              </span>
              {sources.length > 0 && (
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                  参考来源: {sources.length} 个
                </span>
              )}
            </div>
          )}
          {sources.length > 0 && !loading && (
            <div style={{ marginTop: 8 }}>
              <div style={{ maxHeight: 100, overflow: 'auto' }}>
                {sources.map((s, i) => (
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
      )}
    </div>
  )
}
