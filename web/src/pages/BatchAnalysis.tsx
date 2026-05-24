import { useState } from 'react'
import { Card, Input, Button, Progress, Table, Tag, Alert } from 'antd'
import { AppstoreOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons'
import { api } from '../services/api'

const { TextArea } = Input

interface BatchResult {
  stock_code: string
  stock_name: string
  recommendation: string | null
  status: 'success' | 'error'
  error?: string
}

export default function BatchAnalysis() {
  const [stockInput, setStockInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<BatchResult[]>([])
  const [taskId, setTaskId] = useState<string | null>(null)
  const [status, setStatus] = useState<string | null>(null)

  const handleBatchAnalyze = async () => {
    // 解析输入
    const lines = stockInput.trim().split('\n').filter(line => line.trim())
    const stocks = lines.map(line => {
      const parts = line.split(/[,\s]+/)
      return { code: parts[0], name: parts[1] || '' }
    }).filter(s => s.code)

    if (stocks.length === 0) {
      return
    }

    setLoading(true)
    setProgress(0)
    setResults([])
    setTaskId(null)
    setStatus('pending')

    try {
      // 提交批量分析任务
      const response = await api.analyzeBatch({
        stocks,
        risk_preference: 'medium'
      })

      if (response.success) {
        setTaskId(response.data.task_id)
        setStatus('processing')
        pollTaskStatus(response.data.task_id)
      } else {
        setStatus('error')
        setLoading(false)
      }
    } catch (err) {
      setStatus('error')
      setLoading(false)
    }
  }

  const pollTaskStatus = async (taskId: string) => {
    const poll = async () => {
      try {
        const response = await api.getTaskStatus(taskId)
        if (response.success) {
          const data = response.data
          setStatus(data.status)

          if (data.status === 'completed') {
            setProgress(100)
            setResults(data.results || [])
            setLoading(false)
          } else if (data.status === 'processing') {
            const p = data.progress || 0
            setProgress(p)
            setResults(data.results || [])
            setTimeout(poll, 2000)
          } else if (data.status === 'error') {
            setLoading(false)
          } else {
            setTimeout(poll, 2000)
          }
        }
      } catch (err) {
        setLoading(false)
      }
    }
    poll()
  }

  const columns = [
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'code',
      render: (code: string) => <span className="stock-code">{code}</span>
    },
    {
      title: '名称',
      dataIndex: 'stock_name',
      key: 'name'
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'success' ? 'green' : 'red'}>
          {status === 'success' ? '成功' : '失败'}
        </Tag>
      )
    },
    {
      title: '建议摘要',
      dataIndex: 'recommendation',
      key: 'recommendation',
      render: (text: string | null) => text ? (
        <span style={{
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden'
        }}>
          {text}
        </span>
      ) : '-'
    }
  ]

  return (
    <div className="animate-slide-in">
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>
          批量分析
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          一次分析多只股票，每行一个，格式: 代码,名称
        </p>
      </div>

      <Card className="dashboard-card" style={{ marginBottom: '24px' }}>
        <TextArea
          rows={6}
          placeholder={`600519,贵州茅台
000858,五粮液
601318,中国平安
600036,招商银行
300750,宁德时代`}
          value={stockInput}
          onChange={e => setStockInput(e.target.value)}
          style={{
            background: 'var(--bg-tertiary)',
            fontFamily: 'monospace'
          }}
        />
        <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            loading={loading}
            onClick={handleBatchAnalyze}
            style={{
              background: 'var(--accent-green)',
              borderColor: 'var(--accent-green)'
            }}
          >
            开始批量分析
          </Button>
          <Button
            icon={<DeleteOutlined />}
            onClick={() => setStockInput('')}
          >
            清空
          </Button>
        </div>
      </Card>

      {loading && (
        <Card className="dashboard-card" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
            <AppstoreOutlined style={{ fontSize: '24px', color: 'var(--accent-green)' }} />
            <span>批量分析进行中...</span>
          </div>
          <Progress percent={progress} status="active" />
          <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
            状态: {status}
          </p>
        </Card>
      )}

      {results.length > 0 && (
        <Card className="dashboard-card animate-slide-in">
          <h3 style={{ marginBottom: '16px' }}>分析结果</h3>
          <Table
            dataSource={results}
            columns={columns}
            rowKey="stock_code"
            pagination={false}
            size="small"
          />
        </Card>
      )}
    </div>
  )
}
