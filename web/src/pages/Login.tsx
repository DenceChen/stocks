import { useState } from 'react'
import { Form, Input, Button, message } from 'antd'
import { UserOutlined, LockOutlined, LoginOutlined, UserAddOutlined } from '@ant-design/icons'
import { useAuth } from '../contexts/AuthContext'

export default function Login() {
  const { login, register } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (values: { username: string; password: string }) => {
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(values.username, values.password)
        message.success('登录成功')
      } else {
        await register(values.username, values.password)
        message.success('注册成功')
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail || (mode === 'login' ? '登录失败' : '注册失败')
      message.error(detail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg-abyss)',
    }}>
      <div style={{
        width: 380,
        padding: 40,
        background: 'var(--bg-deep)',
        borderRadius: 12,
        border: '1px solid var(--border-default)',
        boxShadow: '0 0 60px rgba(0, 229, 204, 0.05)',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <h1 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 28,
            fontWeight: 700,
            color: 'var(--cyan)',
            letterSpacing: 2,
          }}>
            STOCK AI
          </h1>
          <p style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 11,
            color: 'var(--text-dim)',
            letterSpacing: 3,
            marginTop: 4,
          }}>
            INVESTMENT ANALYZER
          </p>
        </div>

        <div style={{
          display: 'flex',
          marginBottom: 24,
          borderRadius: 6,
          overflow: 'hidden',
          border: '1px solid var(--border-subtle)',
        }}>
          <button
            onClick={() => setMode('login')}
            style={{
              flex: 1,
              padding: '8px 0',
              border: 'none',
              cursor: 'pointer',
              fontFamily: 'var(--font-body)',
              fontSize: 13,
              fontWeight: 500,
              background: mode === 'login' ? 'var(--cyan-dim)' : 'transparent',
              color: mode === 'login' ? 'var(--cyan)' : 'var(--text-muted)',
              transition: 'all 0.2s',
            }}
          >
            登录
          </button>
          <button
            onClick={() => setMode('register')}
            style={{
              flex: 1,
              padding: '8px 0',
              border: 'none',
              borderLeft: '1px solid var(--border-subtle)',
              cursor: 'pointer',
              fontFamily: 'var(--font-body)',
              fontSize: 13,
              fontWeight: 500,
              background: mode === 'register' ? 'var(--cyan-dim)' : 'transparent',
              color: mode === 'register' ? 'var(--cyan)' : 'var(--text-muted)',
              transition: 'all 0.2s',
            }}
          >
            注册
          </button>
        </div>

        <Form onFinish={handleSubmit} size="large">
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input
              prefix={<UserOutlined style={{ color: 'var(--text-dim)' }} />}
              placeholder="用户名"
              style={{
                background: 'var(--bg-surface)',
                borderColor: 'var(--border-subtle)',
                color: 'var(--text-primary)',
              }}
            />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }, { min: 6, message: '密码至少 6 位' }]}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: 'var(--text-dim)' }} />}
              placeholder="密码"
              style={{
                background: 'var(--bg-surface)',
                borderColor: 'var(--border-subtle)',
                color: 'var(--text-primary)',
              }}
            />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              icon={mode === 'login' ? <LoginOutlined /> : <UserAddOutlined />}
              block
              style={{
                height: 44,
                fontWeight: 600,
                fontFamily: 'var(--font-body)',
              }}
            >
              {mode === 'login' ? '登录' : '注册'}
            </Button>
          </Form.Item>
        </Form>

        <div style={{
          textAlign: 'center',
          fontFamily: 'var(--font-mono)',
          fontSize: 10,
          color: 'var(--text-dim)',
          marginTop: 8,
        }}>
          Powered by MiniMax AI
        </div>
      </div>
    </div>
  )
}
