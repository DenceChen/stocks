import { useState } from 'react'
import { Card, Row, Col, Form, Input, Select, Button, Result, Spin, Tag, Descriptions } from 'antd'
import { SearchOutlined, SafetyCertificateOutlined, AlertOutlined } from '@ant-design/icons'
import { api } from '../services/api'

const { Option } = Select

interface AnalysisResult {
  stock_code: string
  stock_name: string
  recommendation: string
  quote: {
    current_price: number
    change_percent: number
    volume: number
  }
  financials: {
    pe_ratio: number
    pb_ratio: number
    roe: number
  }
  processing_time: number
  sources: string[]
}

export default function StockAnalysis() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [form] = Form.useForm()

  const handleAnalyze = async (values: { stockCode: string; stockName?: string; risk: string }) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await api.analyzeStock({
        stock_code: values.stockCode,
        stock_name: values.stockName,
        risk_preference: values.risk
      })

      if (response.success) {
        setResult(response.data)
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
          个股分析
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          输入股票代码，获取 AI 驱动的投资分析
        </p>
      </div>

      <Card className="dashboard-card" style={{ marginBottom: '24px' }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleAnalyze}
          initialValues={{ risk: 'medium' }}
        >
          <Row gutter={16}>
            <Col xs={24} sm={8}>
              <Form.Item
                name="stockCode"
                label={<span style={{ color: 'var(--text-secondary)' }}>股票代码</span>}
                rules={[{ required: true, message: '请输入股票代码' }]}
              >
                <Input
                  placeholder="如: 600519"
                  size="large"
                  style={{ background: 'var(--bg-tertiary)' }}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item
                name="stockName"
                label={<span style={{ color: 'var(--text-secondary)' }}>股票名称(可选)</span>}
              >
                <Input
                  placeholder="如: 贵州茅台"
                  size="large"
                  style={{ background: 'var(--bg-tertiary)' }}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={8}>
              <Form.Item
                name="risk"
                label={<span style={{ color: 'var(--text-secondary)' }}>风险偏好</span>}
              >
                <Select size="large">
                  <Option value="low">低风险</Option>
                  <Option value="medium">中风险</Option>
                  <Option value="high">高风险</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>
          <Button
            type="primary"
            htmlType="submit"
            size="large"
            icon={<SearchOutlined />}
            loading={loading}
            style={{
              background: 'var(--accent-green)',
              borderColor: 'var(--accent-green)'
            }}
          >
            开始分析
          </Button>
        </Form>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', padding: '60px 0' }}>
          <Spin size="large" />
          <p style={{ marginTop: '16px', color: 'var(--text-secondary)' }}>
            AI 正在分析股票，请稍候...
          </p>
        </div>
      )}

      {error && (
        <Result
          status="error"
          title="分析失败"
          subTitle={error}
          icon={<AlertOutlined style={{ color: 'var(--accent-red)' }} />}
        />
      )}

      {result && !loading && (
        <div className="animate-slide-in">
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={8}>
              <div className="dashboard-card" style={{ height: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                  <SafetyCertificateOutlined style={{ fontSize: '24px', color: 'var(--accent-green)' }} />
                  <span style={{ fontSize: '18px', fontWeight: 600 }}>{result.stock_name}</span>
                  <Tag color="blue">{result.stock_code}</Tag>
                </div>
                <Descriptions column={1} size="small">
                  <Descriptions.Item label="当前价">
                    <span style={{ fontSize: '20px', fontWeight: 600, color: 'var(--accent-green)' }}>
                      ¥{result.quote?.current_price?.toFixed(2) || '-'}
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="涨跌幅">
                    <span className={result.quote?.change_percent >= 0 ? 'price-up' : 'price-down'}>
                      {result.quote?.change_percent?.toFixed(2) || '-'}%
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="PE 比率">
                    {result.financials?.pe_ratio?.toFixed(2) || '-'}
                  </Descriptions.Item>
                  <Descriptions.Item label="PB 比率">
                    {result.financials?.pb_ratio?.toFixed(2) || '-'}
                  </Descriptions.Item>
                  <Descriptions.Item label="ROE">
                    {result.financials?.roe?.toFixed(2) || '-'}%
                  </Descriptions.Item>
                </Descriptions>
                <div style={{ marginTop: '16px', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    分析耗时: {result.processing_time?.toFixed(2) || '-'}s
                  </p>
                </div>
              </div>
            </Col>
            <Col xs={24} lg={16}>
              <div className="dashboard-card" style={{ height: '100%' }}>
                <h3 style={{ marginBottom: '16px' }}>
                  <SafetyCertificateOutlined style={{ color: 'var(--accent-green)', marginRight: '8px' }} />
                  AI 投资建议
                </h3>
                <div style={{
                  padding: '20px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: '8px',
                  lineHeight: 1.8,
                  whiteSpace: 'pre-wrap'
                }}>
                  {result.recommendation}
                </div>
                {result.sources && result.sources.length > 0 && (
                  <div style={{ marginTop: '16px' }}>
                    <h4 style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                      参考来源 ({result.sources.length})
                    </h4>
                    <div style={{ maxHeight: '120px', overflow: 'auto' }}>
                      {result.sources.map((source, index) => (
                        <a
                          key={index}
                          href={source}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            display: 'block',
                            fontSize: '12px',
                            color: 'var(--accent-blue)',
                            marginBottom: '4px',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {index + 1}. {source}
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
