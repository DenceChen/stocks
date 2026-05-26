import { useState } from 'react'
import { Table, Tag, Empty, Button } from 'antd'
import { HistoryOutlined, StarOutlined, StarFilled, ExpandOutlined, ShrinkOutlined, ClockCircleOutlined } from '@ant-design/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api } from '../services/api'

interface HistoryItem {
  id: string
  stock_code: string
  stock_name: string
  type: 'stock' | 'market' | 'batch'
  risk_preference: string
  timestamp: string
  summary: string
  full_content?: string
  processing_time?: number
  sources?: string[]
  starred?: boolean
}

const mockHistory: HistoryItem[] = [
  {
    id: '1', stock_code: '600519', stock_name: '贵州茅台', type: 'stock', risk_preference: 'low',
    timestamp: '2026-05-24 14:30:00', summary: '建议持有，当前估值偏高但业绩稳定...',
    full_content: `## 贵州茅台 (600519) 投资分析报告

### 一、公司概况
贵州茅台酒股份有限公司是中国最知名的白酒企业，也是A股市场市值最大的消费类公司。公司主要生产和销售茅台酒及系列产品。

### 二、财务数据分析
- **市盈率 (PE)**: 32.5x，高于行业平均水平，反映市场对其品牌溢价的认可
- **市净率 (PB)**: 10.2x，显示资产质量优异
- **ROE**: 31.5%，盈利能力极强
- **营收增长**: 同比增长 16.2%
- **净利润增长**: 同比增长 18.7%

### 三、行业分析
白酒行业整体进入存量竞争阶段，高端白酒市场仍保持稳健增长。茅台作为"酱香龙头"，品牌护城河深厚，定价权极强。

### 四、投资建议
**评级: 谨慎推荐持有**

1. **短期** (1-3个月): 股价可能在估值压力下震荡，建议观望
2. **中期** (3-12个月): 业绩确定性高，若估值回调至30x以下可加仓
3. **长期** (1年以上): 品牌价值持续提升，适合长期配置

> 风险提示：消费降级风险、政策调控风险、估值回调风险`,
    processing_time: 45.2, sources: ['https://example.com/maotai-report', 'https://example.com/baijiu-industry'],
  },
  {
    id: '2', stock_code: '-', stock_name: '市场分析', type: 'market', risk_preference: 'medium',
    timestamp: '2026-05-24 12:15:00', summary: '市场情绪偏向谨慎，建议关注防御性板块...',
    full_content: `## 市场分析报告 (2026-05-24)

### 市场概览
今日A股三大指数集体收跌，上证指数下跌0.85%，深证成指下跌1.12%，创业板指下跌1.35%。两市成交额约9800亿元，较前一交易日缩量明显。

### 热点板块
1. **银行板块** - 逆势上涨0.3%，防御性特征凸显
2. **煤炭板块** - 受益于能源价格反弹
3. **军工板块** - 政策面利好持续释放

### 风险提示
- 外围市场波动加大
- 人民币汇率承压
- 北向资金持续净流出

### 投资策略
建议投资者保持谨慎，适当增加防御性配置，关注低估值蓝筹股的配置机会。`,
    processing_time: 62.8, sources: ['https://example.com/market-daily', 'https://example.com/sector-analysis'],
  },
  {
    id: '3', stock_code: '000858', stock_name: '五粮液', type: 'stock', risk_preference: 'medium',
    timestamp: '2026-05-23 16:45:00', summary: '白酒板块短期承压，建议观望...',
    full_content: `## 五粮液 (000858) 投资分析报告

### 财务概况
五粮液作为浓香型白酒的龙头企业，近年积极推进品牌高端化战略。当前PE约22x，处于历史中位数水平。

### 核心观点
- 品牌升级成效显著，第八代五粮液市场份额持续扩大
- 渠道改革稳步推进，经销商利润空间改善
- 短期受行业景气度下行影响，增速放缓

### 建议
**评级: 中性**

短期观望为主，等待行业景气度企稳信号。若PE回落至20x以下，可考虑逐步建仓。`,
    processing_time: 38.5, sources: ['https://example.com/wuliangye-report'],
  },
]

const typeLabels: Record<string, string> = { stock: '个股', market: '市场', batch: '批量' }
const riskLabels: Record<string, string> = { low: '低', medium: '中', high: '高' }
const riskColors: Record<string, string> = { low: 'tag-risk-low', medium: 'tag-risk-medium', high: 'tag-risk-high' }

export default function History() {
  const [expandedRows, setExpandedRows] = useState<string[]>([])
  const [starredItems, setStarredItems] = useState<Set<string>>(new Set())

  const toggleExpand = (id: string) => {
    setExpandedRows(prev =>
      prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id]
    )
  }

  const toggleStar = (id: string) => {
    setStarredItems(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const columns = [
    {
      title: '时间', dataIndex: 'timestamp', key: 'ts', width: 170,
      render: (v: string) => (
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-muted)' }}>
          <ClockCircleOutlined style={{ marginRight: 6, fontSize: 10 }} />{v}
        </span>
      ),
    },
    {
      title: '类型', dataIndex: 'type', key: 'type', width: 80,
      render: (v: string) => <span className={`tag tag-risk-${v === 'stock' ? 'low' : v === 'market' ? 'medium' : 'high'}`}>{typeLabels[v]}</span>,
    },
    {
      title: '股票', dataIndex: 'stock_name', key: 'name',
      render: (v: string, r: HistoryItem) => r.type === 'stock' ? (
        <span><span className="stock-code">{r.stock_code}</span> <span style={{ color: 'var(--text-muted)', marginLeft: 6 }}>{v}</span></span>
      ) : <span>{v}</span>,
    },
    {
      title: '风险偏好', dataIndex: 'risk_preference', key: 'risk', width: 80,
      render: (v: string) => <span className={`tag ${riskColors[v]}`}>{riskLabels[v]}</span>,
    },
    {
      title: '摘要', dataIndex: 'summary', key: 'summary',
      render: (v: string) => (
        <span style={{
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
          overflow: 'hidden', color: 'var(--text-muted)', fontSize: 12,
        }}>
          {v}
        </span>
      ),
    },
    {
      title: '', key: 'actions', width: 90,
      render: (_: unknown, r: HistoryItem) => (
        <div style={{ display: 'flex', gap: 8 }}>
          <Button
            type="text" size="small"
            icon={expandedRows.includes(r.id) ? <ShrinkOutlined /> : <ExpandOutlined />}
            onClick={(e) => { e.stopPropagation(); toggleExpand(r.id) }}
            style={{ color: 'var(--cyan)', fontSize: 13 }}
          />
          <Button
            type="text" size="small"
            icon={starredItems.has(r.id) ? <StarFilled /> : <StarOutlined />}
            onClick={(e) => { e.stopPropagation(); toggleStar(r.id) }}
            style={{ color: starredItems.has(r.id) ? 'var(--amber)' : 'var(--text-dim)', fontSize: 13 }}
          />
        </div>
      ),
    },
  ]

  return (
    <div className="anim-slide-up">
      <div className="section-header">
        <h2>分析历史</h2>
        <p>查看历史分析记录和收藏</p>
      </div>

      <div className="card" style={{ padding: 0 }}>
        {mockHistory.length > 0 ? (
          <Table
            dataSource={mockHistory}
            columns={columns}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            expandable={{
              expandedRowKeys: expandedRows,
              onExpandedRowsChange: (keys) => setExpandedRows(keys as string[]),
              expandIcon: () => null,
              expandedRowRender: (record: HistoryItem) => (
                <div style={{
                  margin: '4px 0',
                  padding: 20,
                  background: 'var(--bg-surface)',
                  borderRadius: 8,
                  border: '1px solid var(--border-subtle)',
                }}>
                  <div style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    marginBottom: 16, paddingBottom: 12, borderBottom: '1px solid var(--border-subtle)',
                  }}>
                    <span style={{
                      fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 600,
                      color: 'var(--text-bright)',
                    }}>
                      {record.type === 'stock' ? `${record.stock_name} (${record.stock_code})` : record.stock_name} — 完整分析
                    </span>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                      {record.processing_time && (
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                          耗时 {record.processing_time.toFixed(1)}s
                        </span>
                      )}
                      <span className={`tag ${riskColors[record.risk_preference]}`}>
                        {riskLabels[record.risk_preference]}风险
                      </span>
                    </div>
                  </div>
                  <div className="markdown-body" style={{ fontSize: 14, lineHeight: 1.9 }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {record.full_content || record.summary}
                    </ReactMarkdown>
                  </div>
                  {record.sources && record.sources.length > 0 && (
                    <div style={{
                      marginTop: 16, paddingTop: 12, borderTop: '1px solid var(--border-subtle)',
                    }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-dim)' }}>
                        参考来源 ({record.sources.length})
                      </span>
                      <div style={{ marginTop: 4 }}>
                        {record.sources.map((s, i) => (
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
              ),
            }}
          />
        ) : (
          <div style={{ padding: 60, textAlign: 'center' }}>
            <Empty image={<HistoryOutlined style={{ fontSize: 48, color: 'var(--text-dim)' }} />} description={<span style={{ color: 'var(--text-muted)' }}>暂无历史记录</span>} />
          </div>
        )}
      </div>
    </div>
  )
}
