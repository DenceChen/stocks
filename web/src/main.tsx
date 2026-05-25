import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider, theme } from 'antd'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ConfigProvider
        theme={{
          algorithm: theme.darkAlgorithm,
          token: {
            colorPrimary: '#00e5cc',
            colorBgContainer: '#111a2e',
            colorBgElevated: '#162036',
            colorBorder: 'rgba(0, 229, 204, 0.12)',
            colorText: '#c9d6e3',
            colorTextSecondary: '#5a6f8a',
            fontFamily: "'Outfit', 'Noto Sans SC', sans-serif",
            borderRadius: 8,
          }
        }}
      >
        <App />
      </ConfigProvider>
    </BrowserRouter>
  </React.StrictMode>
)
