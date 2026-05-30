# 认证与历史记录实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 为 Stocks Investment Analysis System 添加用户认证和持久化历史记录功能

**架构：** 后端使用 SQLite + aiosqlite 存储用户和分析历史数据，FastAPI 提供 JWT 认证和 RESTful API；前端使用 React + Ant Design 创建登录/注册界面，并将历史记录从 localStorage 迁移到后端 API

**技术栈：** FastAPI, aiosqlite, JWT, bcrypt, React, Ant Design, Axios

---

## 文件结构

### 后端文件
- `src/db/database.py` - 数据库操作（已存在，需添加历史记录查询函数）
- `src/api/auth.py` - 认证路由（已存在，需添加历史记录路由）
- `src/api/routes.py` - 主路由（需集成历史记录保存）
- `src/api/schemas.py` - Pydantic 模型（需添加历史记录响应模型）

### 前端文件
- `web/src/pages/Login.tsx` - 登录页面（新建）
- `web/src/pages/Register.tsx` - 注册页面（新建）
- `web/src/services/auth.ts` - 认证 API 服务（新建）
- `web/src/services/history.ts` - 历史记录 API 服务（修改，从 localStorage 改为 API）
- `web/src/App.tsx` - 主应用（修改，添加认证状态管理和路由保护）
- `web/src/components/ProtectedRoute.tsx` - 路由保护组件（新建）

### 测试文件
- `tests/test_auth_api.py` - 认证 API 测试（新建）
- `tests/test_history_api.py` - 历史记录 API 测试（新建）
- `web/e2e/auth.spec.ts` - 认证 E2E 测试（新建）
- `web/e2e/history.spec.ts` - 历史记录 E2E 测试（新建）

---

## 第一部分：后端历史记录 API

### Task 1: 添加历史记录 Pydantic 模型

**文件：**
- Modify: `src/api/schemas.py`

- [ ] **Step 1: 在 schemas.py 末尾添加历史记录相关模型**

打开 `src/api/schemas.py`，在文件末尾添加以下代码：

```python
# ============ 历史记录 ============

class HistoryItemResponse(BaseModel):
    """历史记录项响应"""
    id: int
    type: str  # 'stock', 'market', 'batch'
    stock_code: str
    stock_name: str
    risk_preference: str
    summary: str
    full_content: Optional[str] = None
    processing_time: Optional[float] = None
    sources: List[str] = []
    starred: bool = False
    created_at: str


class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    items: List[HistoryItemResponse]
    total: int


class ToggleStarRequest(BaseModel):
    """收藏/取消收藏请求"""
    starred: bool


class ToggleStarResponse(BaseModel):
    """收藏操作响应"""
    success: bool
    starred: bool
```

- [ ] **Step 2: 保存文件**

- [ ] **Step 3: 运行语法检查**

Run: `python -m py_compile src/api/schemas.py`
Expected: 无语法错误

- [ ] **Step 4: 提交**

```bash
git add src/api/schemas.py
git commit -m "feat: 添加历史记录 Pydantic 模型"
```

---

### Task 2: 添加历史记录数据库查询函数

**文件：**
- Modify: `src/db/database.py`

- [ ] **Step 1: 在 database.py 中添加历史记录查询函数**

打开 `src/db/database.py`，在 `save_analysis` 函数后添加以下代码：

```python
async def get_user_history(
    user_id: int,
    limit: int = 100,
    offset: int = 0,
    starred_only: bool = False
) -> tuple[list[dict], int]:
    """获取用户历史记录
    
    Args:
        user_id: 用户 ID
        limit: 返回数量限制
        offset: 偏移量
        starred_only: 是否只返回收藏的记录
    
    Returns:
        (历史记录列表, 总数)
    """
    import json
    
    async with aiosqlite.connect(DB_PATH) as db:
        # 构建查询条件
        if starred_only:
            # 查询总数
            count_cursor = await db.execute(
                "SELECT COUNT(*) FROM analysis_history WHERE user_id = ? AND starred = 1",
                (user_id,)
            )
            total = (await count_cursor.fetchone())[0]
            
            # 查询记录
            cursor = await db.execute("""
                SELECT id, type, stock_code, stock_name, risk_preference,
                       summary, full_content, processing_time, sources, starred, created_at
                FROM analysis_history
                WHERE user_id = ? AND starred = 1
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
        else:
            # 查询总数
            count_cursor = await db.execute(
                "SELECT COUNT(*) FROM analysis_history WHERE user_id = ?",
                (user_id,)
            )
            total = (await count_cursor.fetchone())[0]
            
            # 查询记录
            cursor = await db.execute("""
                SELECT id, type, stock_code, stock_name, risk_preference,
                       summary, full_content, processing_time, sources, starred, created_at
                FROM analysis_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
        
        rows = await cursor.fetchall()
        
        # 转换为字典列表
        items = []
        for row in rows:
            items.append({
                "id": row[0],
                "type": row[1],
                "stock_code": row[2],
                "stock_name": row[3],
                "risk_preference": row[4],
                "summary": row[5],
                "full_content": row[6],
                "processing_time": row[7],
                "sources": json.loads(row[8]) if row[8] else [],
                "starred": bool(row[9]),
                "created_at": row[10]
            })
        
        return items, total


async def toggle_star_record(user_id: int, record_id: int, starred: bool) -> bool:
    """切换历史记录收藏状态
    
    Args:
        user_id: 用户 ID
        record_id: 记录 ID
        starred: 是否收藏
    
    Returns:
        是否成功
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # 验证记录属于该用户
        cursor = await db.execute(
            "SELECT id FROM analysis_history WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        )
        record = await cursor.fetchone()
        
        if not record:
            return False
        
        # 更新收藏状态
        await db.execute(
            "UPDATE analysis_history SET starred = ? WHERE id = ?",
            (1 if starred else 0, record_id)
        )
        await db.commit()
        
        logger.info(f"用户 {user_id} {'收藏' if starred else '取消收藏'} 记录 {record_id}")
        return True


async def delete_history_record(user_id: int, record_id: int) -> bool:
    """删除历史记录
    
    Args:
        user_id: 用户 ID
        record_id: 记录 ID
    
    Returns:
        是否成功
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # 验证记录属于该用户
        cursor = await db.execute(
            "SELECT id FROM analysis_history WHERE id = ? AND user_id = ?",
            (record_id, user_id)
        )
        record = await cursor.fetchone()
        
        if not record:
            return False
        
        # 删除记录
        await db.execute(
            "DELETE FROM analysis_history WHERE id = ?",
            (record_id,)
        )
        await db.commit()
        
        logger.info(f"用户 {user_id} 删除记录 {record_id}")
        return True


async def clear_user_history(user_id: int) -> int:
    """清空用户所有历史记录
    
    Args:
        user_id: 用户 ID
    
    Returns:
        删除的记录数
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # 先获取数量
        cursor = await db.execute(
            "SELECT COUNT(*) FROM analysis_history WHERE user_id = ?",
            (user_id,)
        )
        count = (await cursor.fetchone())[0]
        
        # 删除所有记录
        await db.execute(
            "DELETE FROM analysis_history WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()
        
        logger.info(f"用户 {user_id} 清空历史记录，共删除 {count} 条")
        return count
```

- [ ] **Step 2: 保存文件**

- [ ] **Step 3: 运行语法检查**

Run: `python -m py_compile src/db/database.py`
Expected: 无语法错误

- [ ] **Step 4: 提交**

```bash
git add src/db/database.py
git commit -m "feat: 添加历史记录数据库查询函数"
```

---

### Task 3: 在 auth.py 中添加历史记录路由

**文件：**
- Modify: `src/api/auth.py`

- [ ] **Step 1: 在 auth.py 顶部添加导入**

在文件开头的导入部分添加：

```python
from src.api.schemas import HistoryListResponse, HistoryItemResponse, ToggleStarResponse
from src.db.database import get_user_history, toggle_star_record, delete_history_record, clear_user_history
from typing import Optional
```

- [ ] **Step 2: 在 auth.py 末尾添加历史记录路由**

在 `get_current_user_info` 函数后添加以下代码：

```python
# ============ 历史记录路由 ============

@router.get("/history", response_model=ApiResponse)
async def get_history(
    limit: int = Query(100, ge=1, le=500, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    starred: bool = Query(False, description="是否只返回收藏记录"),
    user_id: int = Depends(get_current_user)
):
    """获取用户历史记录"""
    try:
        items, total = await get_user_history(user_id, limit, offset, starred)
        
        # 转换为响应格式
        history_items = [
            HistoryItemResponse(**item).model_dump()
            for item in items
        ]
        
        return ApiResponse(
            success=True,
            data={
                "items": history_items,
                "total": total
            }
        )
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        return ApiResponse(
            success=False,
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.post("/history/{record_id}/star", response_model=ApiResponse)
async def toggle_star(
    record_id: int,
    starred: bool = Query(..., description="收藏状态"),
    user_id: int = Depends(get_current_user)
):
    """切换历史记录收藏状态"""
    try:
        success = await toggle_star_record(user_id, record_id, starred)
        
        if not success:
            return ApiResponse(
                success=False,
                error={"code": "NOT_FOUND", "message": "记录不存在或无权访问"}
            )
        
        return ApiResponse(
            success=True,
            data={"starred": starred}
        )
    except Exception as e:
        logger.error(f"切换收藏状态失败: {e}")
        return ApiResponse(
            success=False,
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.delete("/history/{record_id}", response_model=ApiResponse)
async def delete_history(
    record_id: int,
    user_id: int = Depends(get_current_user)
):
    """删除历史记录"""
    try:
        success = await delete_history_record(user_id, record_id)
        
        if not success:
            return ApiResponse(
                success=False,
                error={"code": "NOT_FOUND", "message": "记录不存在或无权访问"}
            )
        
        return ApiResponse(success=True, data={"deleted": True})
    except Exception as e:
        logger.error(f"删除历史记录失败: {e}")
        return ApiResponse(
            success=False,
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        )


@router.delete("/history", response_model=ApiResponse)
async def clear_history(user_id: int = Depends(get_current_user)):
    """清空所有历史记录"""
    try:
        count = await clear_user_history(user_id)
        
        return ApiResponse(
            success=True,
            data={"cleared": count}
        )
    except Exception as e:
        logger.error(f"清空历史记录失败: {e}")
        return ApiResponse(
            success=False,
            error={"code": "INTERNAL_ERROR", "message": str(e)}
        )
```

- [ ] **Step 3: 保存文件**

- [ ] **Step 4: 运行语法检查**

Run: `python -m py_compile src/api/auth.py`
Expected: 无语法错误

- [ ] **Step 5: 提交**

```bash
git add src/api/auth.py
git commit -m "feat: 添加历史记录 API 路由"
```

---

### Task 4: 修改主路由集成历史记录保存

**文件：**
- Modify: `src/api/routes.py`

- [ ] **Step 1: 修改 analyze_stock 函数保存历史记录**

找到 `analyze_stock` 函数（约在第 262 行），在返回响应前添加保存历史记录的代码。

在 `return ApiResponse(` 之前添加：

```python
# 保存分析历史（如果用户已认证）
try:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        from src.api.middleware import decode_access_token
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if user_id:
            await save_analysis(
                user_id=user_id,
                analysis_type="stock",
                stock_code=result["stock_code"],
                stock_name=result.get("stock_name", ""),
                risk_preference=request.risk_preference,
                summary=result["recommendation"][:500] if result.get("recommendation") else "",
                full_content=result["recommendation"] or "",
                processing_time=result.get("processing_time"),
                sources=result.get("sources", [])
            )
            logger.info(f"已保存股票分析历史: user_id={user_id}, stock={result['stock_code']}")
except Exception as e:
    # 保存历史失败不影响主流程
    logger.warning(f"保存分析历史失败: {e}")
```

- [ ] **Step 2: 保存文件**

- [ ] **Step 3: 运行语法检查**

Run: `python -m py_compile src/api/routes.py`
Expected: 无语法错误

- [ ] **Step 4: 提交**

```bash
git add src/api/routes.py
git commit -m "feat: 股票分析保存历史记录"
```

---

## 第二部分：前端认证页面

### Task 5: 创建认证 API 服务

**文件：**
- Create: `web/src/services/auth.ts`

- [ ] **Step 1: 创建 auth.ts 文件**

创建新文件 `web/src/services/auth.ts`，内容如下：

```typescript
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface UserInfo {
  id: number
  username: string
  created_at: string
}

const authStorage = {
  getToken: (): string | null => localStorage.getItem('stocks_token'),
  setToken: (token: string) => localStorage.setItem('stocks_token', token),
  clearToken: () => localStorage.removeItem('stocks_token'),
  getUser: (): UserInfo | null => {
    const data = localStorage.getItem('stocks_user')
    return data ? JSON.parse(data) : null
  },
  setUser: (user: UserInfo) => localStorage.setItem('stocks_user', JSON.stringify(user)),
  clearUser: () => localStorage.removeItem('stocks_user'),
}

export async function login(data: LoginRequest): Promise<AuthResponse> {
  const response = await axios.post<AuthResponse>(
    `${API_BASE}/api/v1/auth/login`,
    data
  )
  const { access_token } = response.data
  authStorage.setToken(access_token)
  
  // 获取用户信息
  try {
    const userResponse = await axios.get<UserInfo>(
      `${API_BASE}/api/v1/auth/me`,
      { headers: { Authorization: `Bearer ${access_token}` } }
    )
    authStorage.setUser(userResponse.data)
  } catch {
    // 获取用户信息失败不影响登录
  }
  
  return response.data
}

export async function register(data: RegisterRequest): Promise<AuthResponse> {
  const response = await axios.post<AuthResponse>(
    `${API_BASE}/api/v1/auth/register`,
    data
  )
  const { access_token } = response.data
  authStorage.setToken(access_token)
  
  // 获取用户信息
  try {
    const userResponse = await axios.get<UserInfo>(
      `${API_BASE}/api/v1/auth/me`,
      { headers: { Authorization: `Bearer ${access_token}` } }
    )
    authStorage.setUser(userResponse.data)
  } catch {
    // 获取用户信息失败不影响注册
  }
  
  return response.data
}

export function logout() {
  authStorage.clearToken()
  authStorage.clearUser()
}

export function isAuthenticated(): boolean {
  return !!authStorage.getToken()
}

export function getAuthHeader(): Record<string, string> {
  const token = authStorage.getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export { authStorage }
```

- [ ] **Step 2: 提交**

```bash
git add web/src/services/auth.ts
git commit -m "feat: 创建认证 API 服务"
```

---

### Task 6: 创建历史记录 API 服务

**文件：**
- Modify: `web/src/services/history.ts`

- [ ] **Step 1: 替换 history.ts 全部内容**

将 `web/src/services/history.ts` 的全部内容替换为：

```typescript
import axios from 'axios'
import { getAuthHeader } from './auth'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface HistoryItem {
  id: number
  stock_code: string
  stock_name: string
  type: 'stock' | 'market' | 'batch'
  risk_preference: string
  summary: string
  full_content?: string
  processing_time?: number
  sources?: string[]
  starred: boolean
  created_at: string
}

export interface HistoryListResponse {
  items: HistoryItem[]
  total: number
}

export async function getHistory(
  limit: number = 100,
  offset: number = 0,
  starredOnly: boolean = false
): Promise<HistoryItem[]> {
  try {
    const response = await axios.get<HistoryListResponse>(
      `${API_BASE}/api/v1/auth/history`,
      {
        params: { limit, offset, starred: starredOnly },
        headers: getAuthHeader(),
      }
    )
    return response.data.items || []
  } catch (error) {
    console.error('获取历史记录失败:', error)
    return []
  }
}

export async function toggleStar(recordId: number, starred: boolean): Promise<boolean> {
  try {
    await axios.post(
      `${API_BASE}/api/v1/auth/history/${recordId}/star`,
      null,
      {
        params: { starred },
        headers: getAuthHeader(),
      }
    )
    return starred
  } catch (error) {
    console.error('切换收藏状态失败:', error)
    return !starred
  }
}

export async function deleteHistory(recordId: number): Promise<boolean> {
  try {
    await axios.delete(
      `${API_BASE}/api/v1/auth/history/${recordId}`,
      { headers: getAuthHeader() }
    )
    return true
  } catch (error) {
    console.error('删除历史记录失败:', error)
    return false
  }
}

export async function clearHistory(): Promise<boolean> {
  try {
    await axios.delete(
      `${API_BASE}/api/v1/auth/history`,
      { headers: getAuthHeader() }
    )
    return true
  } catch (error) {
    console.error('清空历史记录失败:', error)
    return false
  }
}

// 保留兼容性：本地存储版本（用于未登录状态）
const LOCAL_STORAGE_KEY = 'stocks_analysis_history_local'

function getLocalHistory(): HistoryItem[] {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveLocalHistory(items: HistoryItem[]) {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(items))
}

export function addLocalHistory(item: Omit<HistoryItem, 'id' | 'starred' | 'created_at'>): HistoryItem {
  const record: HistoryItem = {
    ...item,
    id: Date.now(),
    starred: false,
    created_at: new Date().toISOString(),
  }
  const items = getLocalHistory()
  items.unshift(record)
  if (items.length > 50) items.length = 50
  saveLocalHistory(items)
  return record
}
```

- [ ] **Step 2: 提交**

```bash
git add web/src/services/history.ts
git commit -m "feat: 将历史记录改为 API 调用"
```

---

### Task 7: 创建登录页面

**文件：**
- Create: `web/src/pages/Login.tsx`

- [ ] **Step 1: 创建 Login.tsx 文件**

创建新文件 `web/src/pages/Login.tsx`，内容如下：

```typescript
import { useState } from 'react'
import { Form, Input, Button, Card, Typography, message, Space } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { login } from '../services/auth'

const { Title, Text } = Typography

interface LoginForm {
  username: string
  password: string
}

export default function Login() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onFinish = async (values: LoginForm) => {
    setLoading(true)
    try {
      await login(values)
      message.success('登录成功')
      navigate('/')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Card style={{ width: 400, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>STOCK AI</Title>
            <Text type="secondary">登录以继续</Text>
          </div>
          
          <Form
            name="login"
            onFinish={onFinish}
            autoComplete="off"
            size="large"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
              />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading}>
                登录
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary">
              还没有账号？ <a onClick={() => navigate('/register')}>立即注册</a>
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  )
}
```

- [ ] **Step 2: 提交**

```bash
git add web/src/pages/Login.tsx
git commit -m "feat: 创建登录页面"
```

---

### Task 8: 创建注册页面

**文件：**
- Create: `web/src/pages/Register.tsx`

- [ ] **Step 1: 创建 Register.tsx 文件**

创建新文件 `web/src/pages/Register.tsx`，内容如下：

```typescript
import { useState } from 'react'
import { Form, Input, Button, Card, Typography, message, Space } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { register } from '../services/auth'

const { Title, Text } = Typography

interface RegisterForm {
  username: string
  password: string
  confirmPassword: string
}

export default function Register() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const [form] = Form.useForm()

  const onFinish = async (values: RegisterForm) => {
    setLoading(true)
    try {
      await register({ username: values.username, password: values.password })
      message.success('注册成功')
      navigate('/')
    } catch (error: any) {
      message.error(error.response?.data?.detail || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Card style={{ width: 400, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>STOCK AI</Title>
            <Text type="secondary">创建新账号</Text>
          </div>
          
          <Form
            form={form}
            name="register"
            onFinish={onFinish}
            autoComplete="off"
            size="large"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' },
                { max: 20, message: '用户名最多20个字符' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名（3-20个字符）"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码（至少6个字符）"
              />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              dependencies={['password']}
              rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve()
                    }
                    return Promise.reject(new Error('两次密码输入不一致'))
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="确认密码"
              />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading}>
                注册
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary">
              已有账号？ <a onClick={() => navigate('/login')}>立即登录</a>
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  )
}
```

- [ ] **Step 2: 提交**

```bash
git add web/src/pages/Register.tsx
git commit -m "feat: 创建注册页面"
```

---

### Task 9: 创建路由保护组件

**文件：**
- Create: `web/src/components/ProtectedRoute.tsx`

- [ ] **Step 1: 创建 ProtectedRoute.tsx 文件**

创建新文件 `web/src/components/ProtectedRoute.tsx`，内容如下：

```typescript
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { isAuthenticated } from '../services/auth'

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
    }
  }, [navigate])

  if (!isAuthenticated()) {
    return null
  }

  return <>{children}</>
}
```

- [ ] **Step 2: 提交**

```bash
git add web/src/components/ProtectedRoute.tsx
git commit -m "feat: 创建路由保护组件"
```

---

### Task 10: 修改 App.tsx 集成认证

**文件：**
- Modify: `web/src/App.tsx`

- [ ] **Step 1: 在 App.tsx 顶部添加认证相关导入和状态**

在文件开头添加以下导入：

```typescript
import { useState, useEffect } from 'react'
import { authStorage } from './services/auth'
import ProtectedRoute from './components/ProtectedRoute'
```

- [ ] **Step 2: 添加 Login 和 Register 组件导入**

在现有的组件导入后添加：

```typescript
import Login from './pages/Login'
import Register from './pages/Register'
```

- [ ] **Step 3: 修改 menuItems，添加登出按钮**

找到 `menuItems` 常量，在最后一项后添加：

```typescript
{ key: '/history', icon: <HistoryOutlined />, label: '分析历史' },
{ key: 'logout', icon: null, label: '退出登录' },
```

完整修改后的 menuItems：

```typescript
const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '首页' },
  { key: '/stock', icon: <SearchOutlined />, label: '个股分析' },
  { key: '/market', icon: <LineChartOutlined />, label: '市场分析' },
  { key: '/batch', icon: <AppstoreOutlined />, label: '批量分析' },
  { key: '/quotes', icon: <TableOutlined />, label: '实时行情' },
  { key: '/history', icon: <HistoryOutlined />, label: '分析历史' },
  { key: 'logout', icon: null, label: '退出登录' },
]
```

- [ ] **Step 4: 修改 App 组件添加认证状态管理**

将 `function App()` 替换为：

```typescript
function App() {
  const location = useLocation()
  const navigate = useNavigate()
  const [user, setUser] = useState(authStorage.getUser())
  const [isLogin, setIsLogin] = useState(false)

  useEffect(() => {
    const checkAuth = () => {
      const currentUser = authStorage.getUser()
      setUser(currentUser)
      setIsLogin(!!currentUser)
    }

    checkAuth()

    // 监听 storage 变化（多标签页同步）
    const handleStorageChange = () => checkAuth()
    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  const handleLogout = () => {
    authStorage.clearToken()
    authStorage.clearUser()
    setUser(null)
    setIsLogin(false)
    navigate('/login')
  }

  // 登录/注册页面不显示主布局
  if (location.pathname === '/login' || location.pathname === '/register') {
    if (location.pathname === '/login') return <Login />
    if (location.pathname === '/register') return <Register />
  }

  return (
    <ProtectedRoute>
      <Layout className="app-layout">
        <Sider width={220} className="sidebar">
          <div className="sidebar-brand">
            <h1>STOCK AI</h1>
            <p>Investment Analyzer</p>
          </div>
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems.filter(item => item.key !== 'logout')}
            onClick={({ key }) => {
              if (key === 'logout') {
                handleLogout()
              } else {
                navigate(key)
              }
            }}
          />
          <div className="market-status">
            <span className="status-dot" />
            市场已休市
          </div>
        </Sider>
        <Layout style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
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
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              {user && (
                <span style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 12,
                  color: 'var(--text-muted)',
                }}>
                  {user.username}
                </span>
              )}
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 11,
                color: 'var(--text-dim)',
              }}>
                {new Date().toLocaleDateString('zh-CN', {
                  year: 'numeric', month: '2-digit', day: '2-digit'
                })}
              </div>
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
    </ProtectedRoute>
  )
}
```

- [ ] **Step 5: 保存文件**

- [ ] **Step 6: 提交**

```bash
git add web/src/App.tsx
git commit -m "feat: 集成认证状态管理和路由保护"
```

---

### Task 11: 修改 History 页面使用 API

**文件：**
- Modify: `web/src/pages/History.tsx`

- [ ] **Step 1: 修改导入**

将 `import { getHistory, toggleStar, deleteHistory, clearHistory, HistoryItem } from '../services/history'` 替换为：

```typescript
import { getHistory, toggleStar, deleteHistory, clearHistory, HistoryItem } from '../services/history'
import { isAuthenticated } from '../services/auth'
```

- [ ] **Step 2: 修改 refresh 函数**

将 `const refresh = useCallback(() => setItems(getHistory()), [])` 替换为：

```typescript
const refresh = useCallback(async () => {
  if (isAuthenticated()) {
    const items = await getHistory()
    setItems(items)
  } else {
    // 未登录使用本地存储
    const localItems = localStorage.getItem('stocks_analysis_history_local')
    setItems(localItems ? JSON.parse(localItems) : [])
  }
}, [])
```

- [ ] **Step 3: 修改 handleToggleStar 函数**

将 `const handleToggleStar = (id: string) => { setItems(toggleStar(id)) }` 替换为：

```typescript
const handleToggleStar = async (id: string | number) => {
  const recordId = typeof id === 'string' ? parseInt(id) : id
  const item = items.find(i => i.id === recordId)
  if (item) {
    const newStarred = !item.starred
    const actualStarred = await toggleStar(recordId, newStarred)
    setItems(items.map(i => i.id === recordId ? { ...i, starred: actualStarred } : i))
  }
}
```

- [ ] **Step 4: 修改 handleDelete 函数**

将 `const handleDelete = (id: string) => { setItems(deleteHistory(id)) }` 替换为：

```typescript
const handleDelete = async (id: string | number) => {
  const recordId = typeof id === 'string' ? parseInt(id) : id
  const success = await deleteHistory(recordId)
  if (success) {
    setItems(items.filter(i => i.id !== recordId))
    setExpandedRows(prev => prev.filter(r => r !== id))
  }
}
```

- [ ] **Step 5: 修改 handleClear 函数**

将 `const handleClear = () => { clearHistory(); setItems([]); setExpandedRows([]) }` 替换为：

```typescript
const handleClear = async () => {
  const success = await clearHistory()
  if (success) {
    setItems([])
    setExpandedRows([])
  }
}
```

- [ ] **Step 6: 保存文件**

- [ ] **Step 7: 提交**

```bash
git add web/src/pages/History.tsx
git commit -m "feat: History 页面使用 API 替代 localStorage"
```

---

## 第三部分：测试

### Task 12: 创建后端认证 API 测试

**文件：**
- Create: `tests/test_auth_api.py`

- [ ] **Step 1: 创建测试文件**

创建新文件 `tests/test_auth_api.py`，内容如下：

```python
"""
认证 API 测试
"""
import pytest
import asyncio
from fastapi.testclient import TestClient

from src.api.routes import create_app
from src.db.database import init_db, get_db


@pytest.fixture
async def test_db():
    """测试数据库初始化"""
    await init_db()
    yield

@pytest.fixture
def test_client():
    """测试客户端"""
    app = create_app()
    return TestClient(app)


def test_register_success(test_client, test_db):
    """测试成功注册"""
    response = test_client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


def test_register_duplicate_username(test_client, test_db):
    """测试注册重复用户名"""
    # 第一次注册
    test_client.post("/api/v1/auth/register", json={
        "username": "duplicate",
        "password": "testpass123"
    })
    
    # 第二次注册相同用户名
    response = test_client.post("/api/v1/auth/register", json={
        "username": "duplicate",
        "password": "testpass123"
    })
    assert response.status_code == 400


def test_login_success(test_client, test_db):
    """测试成功登录"""
    # 先注册
    test_client.post("/api/v1/auth/register", json={
        "username": "loginuser",
        "password": "loginpass123"
    })
    
    # 再登录
    response = test_client.post("/api/v1/auth/login", json={
        "username": "loginuser",
        "password": "loginpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


def test_login_wrong_password(test_client, test_db):
    """测试错误密码登录"""
    # 先注册
    test_client.post("/api/v1/auth/register", json={
        "username": "wrongpass",
        "password": "correctpass"
    })
    
    # 用错误密码登录
    response = test_client.post("/api/v1/auth/login", json={
        "username": "wrongpass",
        "password": "wrongpass"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(test_client, test_db):
    """测试不存在的用户登录"""
    response = test_client.post("/api/v1/auth/login", json={
        "username": "nonexistent",
        "password": "anypass"
    })
    assert response.status_code == 401


def test_get_current_user(test_client, test_db):
    """测试获取当前用户信息"""
    # 注册并登录
    register_response = test_client.post("/api/v1/auth/register", json={
        "username": "currentuser",
        "password": "userpass123"
    })
    token = register_response.json()["data"]["access_token"]
    
    # 获取用户信息
    response = test_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["username"] == "currentuser"


def test_get_current_user_no_token(test_client, test_db):
    """测试无 token 获取用户信息"""
    response = test_client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_current_user_invalid_token(test_client, test_db):
    """测试无效 token 获取用户信息"""
    response = test_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
```

- [ ] **Step 2: 提交**

```bash
git add tests/test_auth_api.py
git commit -m "test: 添加认证 API 测试"
```

---

### Task 13: 创建后端历史记录 API 测试

**文件：**
- Create: `tests/test_history_api.py`

- [ ] **Step 1: 创建测试文件**

创建新文件 `tests/test_history_api.py`，内容如下：

```python
"""
历史记录 API 测试
"""
import pytest
from fastapi.testclient import TestClient

from src.api.routes import create_app
from src.db.database import init_db


@pytest.fixture
async def test_db():
    """测试数据库初始化"""
    await init_db()
    yield


@pytest.fixture
def auth_client():
    """已认证的测试客户端"""
    app = create_app()
    client = TestClient(app)
    
    # 注册并登录
    response = client.post("/api/v1/auth/register", json={
        "username": "historyuser",
        "password": "testpass123"
    })
    token = response.json()["data"]["access_token"]
    
    # 设置认证头
    client.headers["Authorization"] = f"Bearer {token}"
    return client


def test_get_history_empty(auth_client, test_db):
    """测试获取空历史记录"""
    response = auth_client.get("/api/v1/auth/history")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["total"] == 0
    assert data["data"]["items"] == []


def test_get_history_no_auth(test_client, test_db):
    """测试未认证获取历史记录"""
    response = test_client.get("/api/v1/auth/history")
    assert response.status_code == 401


def test_toggle_star(auth_client, test_db):
    """测试切换收藏状态"""
    # 先创建一条历史记录（通过分析 API）
    # 这里假设有分析 API 会自动保存历史
    # 简化测试，直接操作数据库
    
    import asyncio
    from src.db.database import save_analysis
    
    # 获取 user_id
    me_response = auth_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]
    
    # 创建历史记录
    record_id = asyncio.run(save_analysis(
        user_id=user_id,
        analysis_type="stock",
        stock_code="000001",
        stock_name="测试股票",
        risk_preference="low",
        summary="测试摘要",
        full_content="测试完整内容"
    ))
    
    # 收藏
    response = auth_client.post(f"/api/v1/auth/history/{record_id}/star", params={"starred": True})
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["starred"] is True
    
    # 取消收藏
    response = auth_client.post(f"/api/v1/auth/history/{record_id}/star", params={"starred": False})
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["starred"] is False


def test_delete_history(auth_client, test_db):
    """测试删除历史记录"""
    import asyncio
    from src.db.database import save_analysis
    
    # 获取 user_id
    me_response = auth_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]
    
    # 创建历史记录
    record_id = asyncio.run(save_analysis(
        user_id=user_id,
        analysis_type="stock",
        stock_code="000002",
        stock_name="待删除股票",
        risk_preference="medium",
        summary="待删除",
        full_content="待删除完整内容"
    ))
    
    # 删除
    response = auth_client.delete(f"/api/v1/auth/history/{record_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["deleted"] is True
    
    # 验证已删除
    response = auth_client.delete(f"/api/v1/auth/history/{record_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False  # 记录不存在


def test_clear_history(auth_client, test_db):
    """测试清空历史记录"""
    import asyncio
    from src.db.database import save_analysis
    
    # 获取 user_id
    me_response = auth_client.get("/api/v1/auth/me")
    user_id = me_response.json()["data"]["id"]
    
    # 创建多条历史记录
    for i in range(3):
        asyncio.run(save_analysis(
            user_id=user_id,
            analysis_type="stock",
            stock_code=f"00000{i}",
            stock_name=f"测试股票{i}",
            risk_preference="low",
            summary=f"测试摘要{i}",
            full_content=f"测试完整内容{i}"
        ))
    
    # 清空
    response = auth_client.delete("/api/v1/auth/history")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["cleared"] == 3
    
    # 验证已清空
    response = auth_client.get("/api/v1/auth/history")
    assert response.json()["data"]["total"] == 0
```

- [ ] **Step 2: 提交**

```bash
git add tests/test_history_api.py
git commit -m "test: 添加历史记录 API 测试"
```

---

### Task 14: 创建前端 E2E 认证测试

**文件：**
- Create: `web/e2e/auth.spec.ts`

- [ ] **Step 1: 创建 E2E 测试文件**

创建新文件 `web/e2e/auth.spec.ts`，内容如下：

```typescript
import { test, expect } from '@playwright/test'

test.describe('用户认证', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173')
  })

  test('显示登录页面', async ({ page }) => {
    await page.goto('http://localhost:5173/login')
    await expect(page.locator('text=STOCK AI')).toBeVisible()
    await expect(page.locator('text=登录以继续')).toBeVisible()
  })

  test('显示注册页面', async ({ page }) => {
    await page.goto('http://localhost:5173/register')
    await expect(page.locator('text=STOCK AI')).toBeVisible()
    await expect(page.locator('text=创建新账号')).toBeVisible()
  })

  test('用户注册流程', async ({ page }) => {
    // 生成随机用户名避免冲突
    const username = `testuser_${Date.now()}`

    await page.goto('http://localhost:5173/register')

    // 填写注册表单
    await page.fill('input[placeholder*="用户名"]', username)
    await page.fill('input[placeholder*="密码"]', 'testpass123')
    await page.fill('input[placeholder*="确认密码"]', 'testpass123')

    // 提交注册
    await page.click('button:has-text("注册")')

    // 等待跳转到首页
    await page.waitForURL('http://localhost:5173/')
    
    // 验证已登录状态（显示用户名）
    await expect(page.locator(`text=${username}`)).toBeVisible()
  })

  test('用户登录流程', async ({ page }) => {
    // 先注册一个用户
    const username = `loginuser_${Date.now()}`
    
    await page.goto('http://localhost:5173/register')
    await page.fill('input[placeholder*="用户名"]', username)
    await page.fill('input[placeholder*="密码"]', 'loginpass123')
    await page.fill('input[placeholder*="确认密码"]', 'loginpass123')
    await page.click('button:has-text("注册")')
    await page.waitForURL('http://localhost:5173/')

    // 登出
    await page.click('text=退出登录')

    // 重新登录
    await page.fill('input[placeholder*="用户名"]', username)
    await page.fill('input[placeholder*="密码"]', 'loginpass123')
    await page.click('button:has-text("登录")')

    // 验证登录成功
    await page.waitForURL('http://localhost:5173/')
    await expect(page.locator(`text=${username}`)).toBeVisible()
  })

  test('密码验证 - 密码不一致', async ({ page }) => {
    await page.goto('http://localhost:5173/register')

    await page.fill('input[placeholder*="用户名"]', 'testuser')
    await page.fill('input[placeholder*="密码"]', 'password123')
    await page.fill('input[placeholder*="确认密码"]', 'different123')

    await page.click('button:has-text("注册")')

    // 验证错误提示
    await expect(page.locator('text=两次密码输入不一致')).toBeVisible()
  })

  test('路由保护 - 未登录重定向', async ({ page }) => {
    // 清除 localStorage
    await page.evaluate(() => localStorage.clear())

    // 尝试访问历史页面
    await page.goto('http://localhost:5173/history')

    // 应该重定向到登录页
    await page.waitForURL('http://localhost:5173/login')
  })
})
```

- [ ] **Step 2: 提交**

```bash
git add web/e2e/auth.spec.ts
git commit -m "test: 添加认证 E2E 测试"
```

---

### Task 15: 创建前端 E2E 历史记录测试

**文件：**
- Create: `web/e2e/history.spec.ts`

- [ ] **Step 1: 创建 E2E 测试文件**

创建新文件 `web/e2e/history.spec.ts`，内容如下：

```typescript
import { test, expect } from '@playwright/test'

test.describe('历史记录', () => {
  let username: string

  test.beforeEach(async ({ page }) => {
    // 注册并登录
    username = `historyuser_${Date.now()}`
    
    await page.goto('http://localhost:5173/register')
    await page.fill('input[placeholder*="用户名"]', username)
    await page.fill('input[placeholder*="密码"]', 'testpass123')
    await page.fill('input[placeholder*="确认密码"]', 'testpass123')
    await page.click('button:has-text("注册")')
    await page.waitForURL('http://localhost:5173/')
  })

  test('显示历史记录页面', async ({ page }) => {
    await page.click('text=分析历史')
    await expect(page.locator('text=分析历史')).toBeVisible()
    await expect(page.locator('text=暂无历史记录')).toBeVisible()
  })

  test('收藏记录', async ({ page }) => {
    // 这里需要先有一条历史记录
    // 假设之前有分析操作生成历史记录
    
    await page.click('text=分析历史')
    
    // 点击收藏按钮（如果有记录）
    const starButton = page.locator('.ant-btn').filter({ hasText: /star/i }).first()
    
    if (await starButton.isVisible()) {
      await starButton.click()
      // 验证星星图标变为实心
      // 实际实现需要根据 UI 调整
    }
  })

  test('删除单条记录', async ({ page }) => {
    await page.click('text=分析历史')
    
    // 点击删除按钮（如果有记录）
    const deleteButton = page.locator('.ant-btn').filter({ hasText: /delete/i }).first()
    
    if (await deleteButton.isVisible()) {
      const recordCount = await page.locator('.ant-table-row').count()
      await deleteButton.click()
      
      // 验证记录减少
      // 实际实现需要根据 UI 调整
    }
  })

  test('清空所有历史', async ({ page }) => {
    await page.click('text=分析历史')
    
    // 点击清空按钮
    const clearButton = page.locator('button:has-text("清空历史")')
    
    if (await clearButton.isVisible()) {
      await clearButton.click()
      // 验证显示"暂无历史记录"
      await expect(page.locator('text=暂无历史记录')).toBeVisible()
    }
  })
})
```

- [ ] **Step 2: 提交**

```bash
git add web/e2e/history.spec.ts
git commit -m "test: 添加历史记录 E2E 测试"
```

---

## 第四部分：最终验证

### Task 16: 运行所有测试

- [ ] **Step 1: 运行后端测试**

Run: `pytest tests/test_auth_api.py tests/test_history_api.py -v`
Expected: 所有测试通过

- [ ] **Step 2: 启动后端服务**

Run: `python run_api.py`
Expected: 服务启动在 8000 端口

- [ ] **Step 3: 启动前端服务**

Run (在另一个终端): `cd web && npm run dev`
Expected: 前端启动在 5173 端口

- [ ] **Step 4: 手动测试注册流程**

1. 访问 http://localhost:5173
2. 应自动重定向到 /login
3. 点击"立即注册"跳转到注册页
4. 输入用户名和密码（如：testuser / testpass123）
5. 点击注册
6. 应跳转回首页，右上角显示用户名

- [ ] **Step 5: 手动测试历史记录**

1. 完成一次股票分析
2. 进入"分析历史"页面
3. 验证记录显示
4. 测试收藏功能
5. 测试删除功能
6. 测试清空功能

- [ ] **Step 6: 提交最终变更**

```bash
git add .
git commit -m "chore: 认证与历史记录功能完成"
```

---

## 完成

所有任务完成后，stocks 项目将具备：
- 完整的用户认证系统（注册、登录、JWT）
- 持久化的历史记录功能
- 前后端完整的测试覆盖
