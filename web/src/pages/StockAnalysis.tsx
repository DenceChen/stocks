import { useState } from 'react'
import { Form, Input, Select, Button, Descriptions, Tag } from 'antd'
import { SearchOutlined, SafetyCertificateOutlined, LoadingOutlined, DownOutlined, RightOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api } from '../services/api'

const { Option } = Select

interface AnalysisResult {
  stock_code: string; stock_name: string; recommendation: string
  quote: { current_price: number; change_percent: number; volume: number } | null
  financials: { pe_ratio: number; pb_ratio: number; roe: number } | null
  processing_time: number; sources: string[]
}

const STAGE_MAP: Record<string, string> = {
  searching: '搜索信息',
  crawling: '爬取网页',
  extracting: '提取关键信息',
  generating: 'AI 生成建议',
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
  const preview = text.length > 150 ? text.slice(0, 150) + '...' : text

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

export default function StockAnalysis() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [streamingText, setStreamingText] = useState('')
  const [stage, setStage] = useState<string | null>(null)
  const [stageDetail, setStageDetail] = useState<string | null>(null)
  const [form] = Form.useForm()

  const handleAnalyze = async (values: { stockCode: string; stockName?: string; risk: string }) => {
    setLoading(true); setError(null); setResult(null)
    setStreamingText(''); setStage('searching'); setStageDetail(null)

    try {
      await api.streamAnalyzeStock({
        stock_code: values.stockCode, stock_name: values.stockName, risk_preference: values.risk
      }, (event) => {
        switch (event.type) {
          case 'status':
            setStage(event.data.stage)
            setStageDetail(event.data.detail || null)
            break
          case 'quote':
            setResult(prev => prev ? { ...prev, quote: event.data } : {
              stock_code: values.stockCode, stock_name: values.stockName || '',
              recommendation: '', quote: event.data, financials: null,
              processing_time: 0, sources: []
            })
            break
          case 'financials':
            setResult(prev => prev ? { ...prev, financials: event.data } : {
              stock_code: values.stockCode, stock_name: values.stockName || '',
              recommendation: '', quote: null, financials: event.data,
              processing_time: 0, sources: []
            })
            break
          case 'text':
            setStreamingText(prev => prev + event.data.content)
            break
          case 'done':
            const doneResult = {
              stock_code: event.data.stock_code || values.stockCode,
              stock_name: event.data.stock_name || values.stockName || '',
              recommendation: event.data.recommendation,
              quote: null as any,
              financials: null as any,
              processing_time: event.data.processing_time,
              sources: event.data.sources || []
            }
            setResult(prev => ({
              ...doneResult,
              quote: prev?.quote ?? null,
              financials: prev?.financials ?? null,
            }))
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

  const displayText = streamingText || result?.recommendation || ''
  const { think, content: mainContent } = parseThinkAndContent(displayText)

  return (
    <div className="anim-slide-up">
      <div className="section-header">
        <h2>个股分析</h2>
        <p>输入股票代码，获取 AI 驱动的投资分析</p>
      </div>

      <div className="card card-glow" style={{ marginBottom: 24 }}>
        <Form form={form} layout="vertical" onFinish={handleAnalyze} initialValues={{ risk: 'medium' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
            <Form.Item name="stockCode" label={<span style={{ color: 'var(--text-muted)', fontSize: 12 }}>股票代码</span>}
              rules={[{ required: true, message: '请输入股票代码' }]}>
              <Input placeholder="如: 600519" style={{ fontFamily: 'var(--font-mono)' }} />
            </Form.Item>
            <Form.Item name="stockName" label={<span style={{ color: 'var(--text-muted)', fontSize: 12 }}>股票名称(可选)</span>}>
              <Input placeholder="如: 贵州茅台" />
            </Form.Item>
            <Form.Item name="risk" label={<span style={{ color: 'var(--text-muted)', fontSize: 12 }}>风险偏好</span>}>
              <Select>
                <Option value="low">低风险</Option>
                <Option value="medium">中风险</Option>
                <Option value="high">高风险</Option>
              </Select>
            </Form.Item>
          </div>
          <Button type="primary" htmlType="submit" size="large" icon={<SearchOutlined />} loading={loading}>
            开始分析
          </Button>
        </Form>
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

      {(mainContent || (result && !loading)) && (
        <div className="anim-slide-up">
          <div style={{ display: 'grid', gridTemplateColumns: result?.quote ? '280px 1fr' : '1fr', gap: 16 }}>
            {result?.quote && (
              <div className="card card-glow">
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                  <SafetyCertificateOutlined style={{ fontSize: 22, color: 'var(--cyan)' }} />
                  <span style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 600 }}>
                    {result.stock_name || result.stock_code}
                  </span>
                  <span className="stock-code">{result.stock_code}</span>
                </div>
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="当前价">
                    <span style={{ fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700, color: 'var(--text-bright)' }}>
                      ¥{result.quote?.current_price?.toFixed(2) || '-'}
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="涨跌幅">
                    <span className={result.quote?.change_percent >= 0 ? 'price-up' : 'price-down'}
                      style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                      {result.quote?.change_percent?.toFixed(2) || '-'}%
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="PE">{result.financials?.pe_ratio?.toFixed(2) || '-'}</Descriptions.Item>
                  <Descriptions.Item label="PB">{result.financials?.pb_ratio?.toFixed(2) || '-'}</Descriptions.Item>
                  <Descriptions.Item label="ROE">{result.financials?.roe?.toFixed(2) || '-'}%</Descriptions.Item>
                </Descriptions>
                {(result.processing_time || loading) && (
                  <div style={{ marginTop: 12, padding: '8px 12px', background: 'var(--bg-surface)', borderRadius: 6, border: '1px solid var(--border-subtle)' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                      {loading ? `${STAGE_MAP[stage!] || ''}...` : `分析耗时: ${result.processing_time?.toFixed(2)}s`}
                    </span>
                  </div>
                )}
              </div>
            )}

            <div className="card card-glow">
              <h3 style={{ marginBottom: 16, fontFamily: 'var(--font-body)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                <SafetyCertificateOutlined style={{ color: 'var(--cyan)' }} />
                AI 投资建议
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
              {result?.sources?.length > 0 && !loading && (
                <div style={{ marginTop: 16 }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                    参考来源 ({result.sources.length})
                  </span>
                  <div style={{ maxHeight: 100, overflow: 'auto', marginTop: 4 }}>
                    {result.sources.map((s, i) => (
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
          </div>
        </div>
      )}
    </div>
  )
}
