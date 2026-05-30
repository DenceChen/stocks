import { useState } from 'react'
import { Button, Select, Tag } from 'antd'
import { LineChartOutlined, LoadingOutlined, DownOutlined, RightOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api } from '../services/api'

const { Option } = Select

const STAGE_MAP: Record<string, string> = {
  searching: '搜索市场信息',
  crawling: '爬取网页',
  extracting: '提取关键信息',
  generating: 'AI 生成分析报告',
}

function parseThinkAndContent(text: string): { think: string | null; content: string } {
  const thinkMatch = text.match(/<think\s*>([\s\S]*?)(<\/think>|$)/)
  if (thinkMatch) {
    const think = thinkMatch[1].trim()
    const content = text.slice(thinkMatch[0].length).trim()
    return { think: think || null, content }
  }
  return { think: null, content: text }
}

function ThinkBlock({ text }: { text: string }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div style={{ marginBottom: 16, borderRadius: 8, border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          padding: '10px 14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
          background: 'var(--bg-surface)', fontSize: 12, color: 'var(--text-dim)',
          fontFamily: 'var(--font-mono)', userSelect: 'none',
        }}
      >
        {expanded ? <DownOutlined style={{ fontSize: 10 }} /> : <RightOutlined style={{ fontSize: 10 }} />}
        <span>AI 思考过程</span>
        <span style={{ opacity: 0.5 }}>{expanded ? '(点击收起)' : `(${text.length} 字, 点击展开)`}</span>
      </div>
      {expanded && (
        <div style={{
          padding: 14, background: 'rgba(0,0,0,0.15)', fontSize: 12, lineHeight: 1.8,
          color: 'var(--text-dim)', fontFamily: 'var(--font-body)', whiteSpace: 'pre-wrap',
          maxHeight: 400, overflow: 'auto',
        }}>
          {text}
        </div>
      )}
    </div>
  )
}

export default function MarketAnalysis() {
  const [loading, setLoading] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  const [stage, setStage] = useState<string | null>(null)
  const [stageDetail, setStageDetail] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [sources, setSources] = useState<string[]>([])
  const [processingTime, setProcessingTime] = useState<number | null>(null)
  const [risk, setRisk] = useState('medium')

  const handleAnalyze = async () => {
    const currentRisk = risk
    setLoading(true); setError(null); setStreamingText('')
    setStage('searching'); setStageDetail(null); setSources([]); setProcessingTime(null)

    try {
      await api.streamAnalyzeMarket({ risk_preference: currentRisk }, (event) => {
        switch (event.type) {
          case 'status':
            setStage(event.data.stage)
            setStageDetail(event.data.detail || null)
            break
          case 'text':
            setStreamingText(prev => prev + event.data.content)
            break
          case 'done':
            const doneSources = event.data.sources || []
            const doneTime = event.data.processing_time
            setSources(doneSources)
            setProcessingTime(doneTime)
            setLoading(false); setStage(null); setStageDetail(null)
            break
          case 'error':
            setError(event.data.message || '分析失败')
            setLoading(false); setStage(null); setStageDetail(null)
            break
        }
      })
    } catch (err: any) {
      setError(err.message || '网络错误')
      setLoading(false); setStage(null); setStageDetail(null)
    }
  }

  const displayText = streamingText
  const { think, content: mainContent } = parseThinkAndContent(displayText)

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

      {loading && stage && !mainContent && (
        <div className="card card-glow" style={{ marginBottom: 24, padding: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <LoadingOutlined style={{ fontSize: 24, color: 'var(--cyan)' }} spin />
            <div>
              <div style={{ color: 'var(--text-bright)', fontFamily: 'var(--font-body)', fontWeight: 500 }}>
                {stage && STAGE_MAP[stage]}...
              </div>
              {stageDetail && (
                <pre style={{
                  margin: '8px 0 0', fontSize: 11, color: 'var(--text-dim)',
                  fontFamily: 'var(--font-mono)', whiteSpace: 'pre-wrap', lineHeight: 1.6,
                  maxHeight: 120, overflow: 'auto',
                }}>
                  {stageDetail}
                </pre>
              )}
            </div>
          </div>
          <div style={{ width: '100%', height: 3, borderRadius: 2, overflow: 'hidden', background: 'var(--bg-surface)' }}>
            <div className="shimmer" style={{ height: '100%', width: '100%' }} />
          </div>
        </div>
      )}

      {(mainContent || (!loading && streamingText)) && (
        <div className="card card-glow anim-slide-up">
          <h3 style={{ marginBottom: 16, fontFamily: 'var(--font-body)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            <LineChartOutlined style={{ color: 'var(--cyan)' }} />
            市场分析报告
            {loading && <Tag color="processing" style={{ marginLeft: 8, fontSize: 11 }}>生成中</Tag>}
          </h3>
          <div className={loading ? 'streaming-cursor' : ''} style={{
            padding: 20, background: 'var(--bg-surface)', borderRadius: 8,
            border: '1px solid var(--border-subtle)', lineHeight: 1.9,
            fontFamily: 'var(--font-body)', fontSize: 14, color: 'var(--text-primary)',
            minHeight: mainContent ? 'auto' : 120,
          }}>
            {think && <ThinkBlock text={think} />}
            {mainContent ? (
              <div className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{mainContent}</ReactMarkdown>
              </div>
            ) : (loading ? '' : '等待分析...')}
          </div>
          {processingTime !== null && !loading && (
            <div style={{ marginTop: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                参考来源 ({sources.length})
              </span>
              <div style={{ maxHeight: 100, overflow: 'auto', marginTop: 4 }}>
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
