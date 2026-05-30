import axios from 'axios'

const BASE_URL = '/api/v1/auth'

const TOKEN_KEY = 'stocks_jwt_token'

const authClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

export interface AuthUser {
  id: number
  username: string
  created_at: string
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export async function login(username: string, password: string): Promise<string> {
  const res = await authClient.post('/login', { username, password })
  const token = res.data.access_token
  setToken(token)
  return token
}

export async function register(username: string, password: string): Promise<string> {
  const res = await authClient.post('/register', { username, password })
  const token = res.data.access_token
  setToken(token)
  return token
}

export async function getMe(): Promise<AuthUser> {
  const token = getToken()
  if (!token) throw new Error('No token')
  const res = await authClient.get('/me', {
    headers: { Authorization: `Bearer ${token}` },
  })
  return res.data
}

export function logout() {
  removeToken()
}
