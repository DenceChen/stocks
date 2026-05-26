import { useLocation, useNavigate } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  SearchOutlined,
  LineChartOutlined,
  AppstoreOutlined,
  HistoryOutlined,
  TableOutlined,
} from '@ant-design/icons'
import Dashboard from './pages/Dashboard'
import StockAnalysis from './pages/StockAnalysis'
import MarketAnalysis from './pages/MarketAnalysis'
import BatchAnalysis from './pages/BatchAnalysis'
import Quotes from './pages/Quotes'
import History from './pages/History'
import './index.css'

const { Sider, Header, Content } = Layout

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '首页' },
  { key: '/stock', icon: <SearchOutlined />, label: '个股分析' },
  { key: '/market', icon: <LineChartOutlined />, label: '市场分析' },
  { key: '/batch', icon: <AppstoreOutlined />, label: '批量分析' },
  { key: '/quotes', icon: <TableOutlined />, label: '实时行情' },
  { key: '/history', icon: <HistoryOutlined />, label: '分析历史' },
]

function App() {
  const location = useLocation()
  const navigate = useNavigate()

  return (
    <Layout className="app-layout">
      <Sider width={220} className="sidebar">
        <div className="sidebar-brand">
          <h1>STOCK AI</h1>
          <p>Investment Analyzer</p>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
        <div className="market-status">
          <span className="status-dot" />
          市场已休市
        </div>
      </Sider>
      <Layout>
        <Header className="header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
              color: 'var(--text-dim)',
              letterSpacing: 1,
            }}>
              STOCK INVESTMENT ANALYSIS
            </span>
            <span className="pulse-dot" />
          </div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 11,
            color: 'var(--text-dim)',
          }}>
            {new Date().toLocaleDateString('zh-CN', {
              year: 'numeric', month: '2-digit', day: '2-digit'
            })}
          </div>
        </Header>
        <Content className="content-area">
          <div style={{ display: location.pathname === '/' ? 'block' : 'none' }}><Dashboard /></div>
          <div style={{ display: location.pathname === '/stock' ? 'block' : 'none' }}><StockAnalysis /></div>
          <div style={{ display: location.pathname === '/market' ? 'block' : 'none' }}><MarketAnalysis /></div>
          <div style={{ display: location.pathname === '/batch' ? 'block' : 'none' }}><BatchAnalysis /></div>
          <div style={{ display: location.pathname === '/quotes' ? 'block' : 'none' }}><Quotes /></div>
          <div style={{ display: location.pathname === '/history' ? 'block' : 'none' }}><History /></div>
        </Content>
      </Layout>
    </Layout>
  )
}

export default App
