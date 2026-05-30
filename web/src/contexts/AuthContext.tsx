import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import * as auth from '../services/auth'

interface AuthState {
  user: auth.AuthUser | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState>(null!)

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<auth.AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = auth.getToken()
    if (token) {
      auth.getMe()
        .then(setUser)
        .catch(() => auth.removeToken())
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const handleLogin = async (username: string, password: string) => {
    await auth.login(username, password)
    const me = await auth.getMe()
    setUser(me)
  }

  const handleRegister = async (username: string, password: string) => {
    await auth.register(username, password)
    const me = await auth.getMe()
    setUser(me)
  }

  const handleLogout = () => {
    auth.logout()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{
      user, loading,
      login: handleLogin,
      register: handleRegister,
      logout: handleLogout,
    }}>
      {children}
    </AuthContext.Provider>
  )
}
