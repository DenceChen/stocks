import { useState } from 'react'
import { Card, Input, Button, Progress, Table, Tag } from 'antd'
import { AppstoreOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons'
import { api } from '../services/api'

const { TextArea } = Input

interface BatchResult {
  stock_code: string; stock_name: string; recommendation: string | null
  status: 'success' | 'error'; error?: string
}

export default function BatchAnalysis() {
  const [stockInput, setStockInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<BatchResult[]>([])
  const [status, setStatus] = useState<string | null>(null)

  const handleBatchAnalyze = async () => {
    const stocks = stockInput.trim().split('\n').filter(l => l.trim()).map(l => {
      const parts = l.split(/[,\s]+/)
      return { code: parts[0], name: parts[1] || '' }
    }).filter(s => s.code)
    if (!stocks.length) return

    setLoading(true); setProgress(0); setResults([]); setStatus('pending')

    try {
      const res = await api.analyzeBatch({ stocks, risk_preference: 'medium' })
      if (res.success) { setStatus('processing'); pollTask(res.data.task_id) }
      else { setStatus('error'); setLoading(false) }
    } catch (err: any) {
      setStatus('error'); setLoading(false)
    }
  }

  const pollTask = (taskId: string) => {
    const poll = async () => {
      try {
        const res = await api.getTaskStatus(taskId)
        if (res.success) {
          const d = res.data
          setStatus(d.status)
          if (d.status === 'completed') { setProgress(100); setResults(d.results || []); setLoading(false) }
          else if (d.status === 'processing') { setProgress(d.progress || 0); setResults(d.results || []); setTimeout(poll, 2000) }
          else if (d.status === 'error') setLoading(false)
          else setTimeout(poll, 2000)
        }
      } catch { setLoading(false) }
    }
    poll()
  }

  const columns = [
    { title: '股票代码', dataIndex: 'stock_code', key: 'code', render: (v: string) => <span className="stock-code">{v}</span> },
    { title: '名称', dataIndex: 'stock_name', key: 'name' },
    {
      title: '状态', dataIndex: 'status', key: 'status',
      render: (v: string) => <Tag color={v === 'success' ? 'green' : 'red'}>{v === 'success' ? '成功' : '失败'}</Tag>
    },
    {
      title: '建议摘要', dataIndex: 'recommendation', key: 'rec',
      render: (v: string | null) => v ? (
        <span style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', fontSize: 12, color: 'var(--text-muted)' }}>{v}</span>
      ) : '-'
    },
  ]

  return (
    <div className="anim-slide-up">
      <div className="section-header">
        <h2>批量分析</h2>
        <p>同时分析多只股票，每行一个，格式: 代码,名称</p>
      </div>

      <div className="card card-glow" style={{ marginBottom: 24 }}>
        <TextArea rows={6} placeholder={`600519,贵州茅台\n000858,五粮液\n601318,中国平安`}
          value={stockInput} onChange={e => setStockInput(e.target.value)}
          style={{ background: 'var(--bg-surface)', fontFamily: 'var(--font-mono)', fontSize: 13, marginBottom: 12 }} />
        <div style={{ display: 'flex', gap: 12 }}>
          <Button type="primary" icon={<PlayCircleOutlined />} loading={loading} onClick={handleBatchAnalyze}>
            开始批量分析
          </Button>
          <Button icon={<DeleteOutlined />} onClick={() => setStockInput('')}>清空</Button>
        </div>
      </div>

      {loading && (
        <div className="card card-glow" style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
            <AppstoreOutlined style={{ fontSize: 18, color: 'var(--cyan)' }} />
            <span style={{ fontFamily: 'var(--font-body)', fontWeight: 500 }}>批量分析进行中...</span>
          </div>
          <Progress percent={progress} status="active" />
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)', marginTop: 4 }}>
            状态: {status}
          </span>
        </div>
      )}

      {results.length > 0 && (
        <div className="card card-glow anim-slide-up" style={{ padding: 0 }}>
          <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border-subtle)' }}>
            <span style={{ fontFamily: 'var(--font-body)', fontWeight: 600, fontSize: 14, color: 'var(--text-bright)' }}>
              分析结果
            </span>
          </div>
          <Table dataSource={results} columns={columns} rowKey="stock_code" pagination={false} size="small" />
        </div>
      )}
    </div>
  )
}
