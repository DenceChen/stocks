import { useState, useEffect, useRef } from 'react'
import { Card, Row, Col, Form, Input, Select, Button, Result, Spin, Tag, Descriptions } from 'antd'
import { SearchOutlined, SafetyCertificateOutlined, AlertOutlined } from '@ant-design/icons'
import { api } from '../services/api'

const { Option } = Select

interface AnalysisResult {
  stock_code: string; stock_name: string; recommendation: string
  quote: { current_price: number; change_percent: number; volume: number }
  financials: { pe_ratio: number; pb_ratio: number; roe: number }
  processing_time: number; sources: string[]
}

export default function StockAnalysis() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [form] = Form.useForm()
  const abortRef = useRef<AbortController | null>(null)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    return () => { mountedRef.current = false; abortRef.current?.abort() }
  }, [])

  const handleAnalyze = async (values: { stockCode: string; stockName?: string; risk: string }) => {
    abortRef.current?.abort()
    abortRef.current = new AbortController()
    setLoading(true); setError(null); setResult(null)

    try {
      const res = await api.analyzeStock({
        stock_code: values.stockCode, stock_name: values.stockName, risk_preference: values.risk
      }, { signal: abortRef.current.signal })

      if (mountedRef.current) {
        res.success ? setResult(res.data) : setError(res.error?.message || '分析失败')
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
        <h2>个股分析</h2>
        <p>输入股票代码，获取 AI 驱动的投资分析</p>
      </div>

      <div className="card card-glow" style={{ marginBottom: 24 }}>
        <Form form={form} layout="vertical" onFinish={handleAnalyze} initialValues={{ risk: 'medium' }}>
          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Form.Item name="stockCode" label={<span style={{ color: 'var(--text-muted)', fontSize: 12 }}>股票代码</span>}
                rules={[{ required: true, message: '请输入股票代码' }]}>
                <Input placeholder="如: 600519" style={{ fontFamily: 'var(--font-mono)' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="stockName" label={<span style={{ color: 'var(--text-muted)', fontSize: 12 }}>股票名称(可选)</span>}>
                <Input placeholder="如: 贵州茅台" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item name="risk" label={<span style={{ color: 'var(--text-muted)', fontSize: 12 }}>风险偏好</span>}>
                <Select>
                  <Option value="low">低风险</Option>
                  <Option value="medium">中风险</Option>
                  <Option value="high">高风险</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Button type="primary" htmlType="submit" size="large" icon={<SearchOutlined />} loading={loading}>
            开始分析
          </Button>
        </Form>
      </div>

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: 60 }}>
          <Spin size="large" />
          <p style={{ marginTop: 16, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: 13 }}>
            AI 正在分析股票，请稍候...
          </p>
          <div style={{ marginTop: 8, width: 200, height: 3, margin: '8px auto 0', borderRadius: 2, overflow: 'hidden', background: 'var(--bg-surface)' }}>
            <div className="shimmer" style={{ height: '100%', width: '100%' }} />
          </div>
        </div>
      )}

      {error && (
        <div className="card">
          <Result status="error" title="分析失败" subTitle={error}
            icon={<AlertOutlined style={{ color: 'var(--red)' }} />} />
        </div>
      )}

      {result && !loading && (
        <div className="anim-slide-up">
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={8}>
              <div className="card card-glow" style={{ height: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                  <SafetyCertificateOutlined style={{ fontSize: 22, color: 'var(--cyan)' }} />
                  <span style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 600 }}>{result.stock_name}</span>
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
                {result.processing_time && (
                  <div style={{ marginTop: 12, padding: '8px 12px', background: 'var(--bg-surface)', borderRadius: 6, border: '1px solid var(--border-subtle)' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                      分析耗时: {result.processing_time.toFixed(2)}s
                    </span>
                  </div>
                )}
              </div>
            </Col>
            <Col xs={24} lg={16}>
              <div className="card card-glow" style={{ height: '100%' }}>
                <h3 style={{ marginBottom: 16, fontFamily: 'var(--font-body)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <SafetyCertificateOutlined style={{ color: 'var(--cyan)' }} />
                  AI 投资建议
                </h3>
                <div style={{
                  padding: 20, background: 'var(--bg-surface)', borderRadius: 8,
                  border: '1px solid var(--border-subtle)', lineHeight: 1.9, whiteSpace: 'pre-wrap',
                  fontFamily: 'var(--font-body)', fontSize: 14, color: 'var(--text-primary)',
                }}>
                  {result.recommendation}
                </div>
                {result.sources?.length > 0 && (
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
            </Col>
          </Row>
        </div>
      )}
    </div>
  )
}
