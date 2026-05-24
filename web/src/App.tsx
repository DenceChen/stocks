import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  SearchOutlined,
  LineChartOutlined,
  AppstoreOutlined,
  HistoryOutlined
} from '@ant-design/icons'
import Dashboard from './pages/Dashboard'
import StockAnalysis from './pages/StockAnalysis'
import MarketAnalysis from './pages/MarketAnalysis'
import BatchAnalysis from './pages/BatchAnalysis'
import History from './pages/History'
import './index.css'

const { Header, Sider, Content } = Layout

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '首页' },
  { key: '/stock', icon: <SearchOutlined />, label: '个股分析' },
  { key: '/market', icon: <LineChartOutlined />, label: '市场分析' },
  { key: '/batch', icon: <AppstoreOutlined />, label: '批量分析' },
  { key: '/history', icon: <HistoryOutlined />, label: '分析历史' },
]

function App() {
  return (
    <Layout className="app-layout">
      <Sider width={240} className="sidebar">
        <div style={{
          padding: '20px',
          borderBottom: '1px solid var(--border-color)',
          textAlign: 'center'
        }}>
          <h1 style={{
            fontSize: '18px',
            color: 'var(--accent-green)',
            fontWeight: 700,
            letterSpacing: '2px'
          }}>
            STOCK AI
          </h1>
          <p style={{
            fontSize: '10px',
            color: 'var(--text-secondary)',
            marginTop: '4px',
            letterSpacing: '1px'
          }}>
            INVESTMENT ANALYZER
          </p>
        </div>
        <Menu
          mode="inline"
          defaultSelectedKeys={['/']}
          items={menuItems}
          style={{
            background: 'transparent',
            border: 'none',
            marginTop: '16px'
          }}
        />
      </Sider>
      <Layout>
        <Header className="header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{
              fontSize: '12px',
              color: 'var(--text-secondary)'
            }}>
              股票投资分析系统
            </span>
            <span className="animate-pulse" style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: 'var(--accent-green)',
              display: 'inline-block'
            }} />
          </div>
        </Header>
        <Content className="content-area">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/stock" element={<StockAnalysis />} />
            <Route path="/market" element={<MarketAnalysis />} />
            <Route path="/batch" element={<BatchAnalysis />} />
            <Route path="/history" element={<History />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

export default App
