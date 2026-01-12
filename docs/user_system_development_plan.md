# 用户体系开发计划

## 1. 项目概述

### 1.1 目标
为 BuildWhat 项目构建完整的用户体系，包括：
- 用户注册与登录（邮箱密码 + 第三方登录）
- 用户基础信息管理
- 用户与 AI 会话关联
- 用户权限与会员体系

### 1.2 技术选型

| 模块 | 技术方案 |
|------|----------|
| 认证框架 | FastAPI + JWT (后端实现) |
| 前端框架 | Next.js (仅负责 UI) |
| UI组件 | shadcn/ui |
| 数据库 | Supabase (PostgreSQL) |
| 会话存储 | Redis + SQLite (现有架构) |
| 邮件服务 | Resend / Nodemailer (待实现) |
| 头像服务 | unavatar.io / Google 头像 |

### 1.3 架构说明

**认证流程完全由后端处理：**
- 后端 FastAPI 提供所有认证 API (`/api/auth/*`)
- 使用 JWT token 进行会话管理
- Token 存储在 HttpOnly Cookie 中
- 前端 Next.js 仅负责 UI 展示和调用后端 API

### 1.4 参考文档
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- Google OAuth 2.0: https://developers.google.com/identity/protocols/oauth2
- JWT: https://jwt.io/

---

## 2. 数据库设计

### 2.1 用户表 (user)

```sql
CREATE TABLE "user" (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    "emailVerified" BOOLEAN DEFAULT FALSE,
    name VARCHAR(255),
    image VARCHAR(512),  -- 头像URL
    
    -- 会员信息
    plan VARCHAR(20) DEFAULT 'free',  -- free / pro / enterprise
    
    -- 时间戳
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_user_plan ON "user"(plan);
```

### 2.2 账户表 (account)

```sql
-- 存储登录凭证和第三方账户信息
CREATE TABLE account (
    id VARCHAR(255) PRIMARY KEY,
    "userId" VARCHAR(255) NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    "accountId" VARCHAR(255) NOT NULL,
    "providerId" VARCHAR(255) NOT NULL,  -- credential / google / github
    password TEXT,  -- 仅 credential 类型使用
    "accessToken" TEXT,
    "refreshToken" TEXT,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW(),
    
    UNIQUE("providerId", "accountId")
);

CREATE INDEX idx_account_user_id ON account("userId");
```


### 2.3 会话表 (session) - 可选

```sql
-- 如需服务端会话管理可使用此表
CREATE TABLE session (
    id VARCHAR(255) PRIMARY KEY,
    "userId" VARCHAR(255) NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    "expiresAt" TIMESTAMP NOT NULL,
    "ipAddress" VARCHAR(45),
    "userAgent" TEXT,
    "createdAt" TIMESTAMP DEFAULT NOW(),
    "updatedAt" TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_session_user_id ON session("userId");
CREATE INDEX idx_session_token ON session(token);
```

### 2.4 修改现有 chat_sessions 表

```sql
-- 添加用户关联字段
ALTER TABLE chat_sessions 
ADD COLUMN user_id VARCHAR(255) REFERENCES "user"(id) ON DELETE SET NULL;

-- 添加索引
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
```

---

## 3. 后端 API 设计

### 3.1 认证 API (FastAPI 实现)

| 路由 | 方法 | 描述 | 状态 |
|------|------|------|------|
| `/api/auth/sign-up` | POST | 邮箱注册 | ✅ 已完成 |
| `/api/auth/sign-in` | POST | 邮箱登录 | ✅ 已完成 |
| `/api/auth/sign-out` | POST | 退出登录 | ✅ 已完成 |
| `/api/auth/session` | GET | 获取当前会话 | ✅ 已完成 |
| `/api/auth/me` | GET | 获取当前用户信息 | ✅ 已完成 |
| `/api/auth/google` | GET | 发起 Google OAuth | ✅ 已完成 |
| `/api/auth/callback/google` | GET | Google OAuth 回调 | ✅ 已完成 |
| `/api/auth/verify-email` | POST | 验证邮箱 | ✅ 已完成 |
| `/api/auth/send-verification` | POST | 发送验证邮件 | ✅ 已完成 |
| `/api/auth/forgot-password` | POST | 忘记密码 | ✅ 已完成 |
| `/api/auth/reset-password` | POST | 重置密码 | ✅ 已完成 |

### 3.2 用户管理 API (自定义)

```
GET    /api/user/profile          # 获取用户信息
PUT    /api/user/profile          # 更新用户信息
PUT    /api/user/preferences      # 更新偏好设置
GET    /api/user/usage            # 获取使用统计
DELETE /api/user/account          # 删除账户
```

### 3.3 会话关联 API

```
GET    /api/user/sessions         # 获取用户的所有会话
POST   /api/user/sessions/claim   # 认领匿名会话（登录后）
```

---

## 4. 前端实现

### 4.1 认证客户端 (`frontend/src/lib/auth-client.ts`)

前端认证客户端封装了对后端 API 的调用：

```typescript
// 已实现的功能
signUp(email, password, name)     // 注册
signIn(email, password)           // 登录
signOut()                         // 登出
getSession()                      // 获取会话
getMe()                           // 获取用户信息
signInWithGoogle(callbackUrl)     // Google 登录
```

### 4.2 登录/注册页面 (`/auth/[path]`)

**布局设计：**
- 左右分栏布局（响应式：移动端单栏）
- 左侧：品牌展示区
- 右侧：认证表单区

**组件结构：**
```
frontend/src/app/auth/
├── [path]/
│   └── page.tsx           # 动态路由处理所有认证页面
├── layout.tsx             # 认证页面布局
└── components/
    ├── AuthBranding.tsx   # 左侧品牌展示
    └── AuthForm.tsx       # 右侧表单
```

### 4.3 用户设置页面 (`/settings`)

**页面结构：**
```
frontend/src/app/settings/
├── page.tsx               # 设置主页
├── layout.tsx             # 设置页面布局
├── profile/
│   └── page.tsx           # 个人资料设置
├── account/
│   └── page.tsx           # 账户安全设置
└── preferences/
    └── page.tsx           # 偏好设置
```

---

## 5. 实现进度

### Phase 1: 基础认证 ✅ 已完成

#### 1.1 数据库
- [x] 创建 user 表
- [x] 创建 account 表
- [x] 数据库迁移脚本

#### 1.2 后端认证 API
- [x] 邮箱密码注册 (`/api/auth/sign-up`)
- [x] 邮箱密码登录 (`/api/auth/sign-in`)
- [x] 退出登录 (`/api/auth/sign-out`)
- [x] 获取会话 (`/api/auth/session`)
- [x] 获取用户信息 (`/api/auth/me`)
- [x] JWT Token 生成与验证
- [x] HttpOnly Cookie 管理

#### 1.3 Google OAuth ✅ 已完成
- [x] Google OAuth 发起 (`/api/auth/google`)
- [x] Google OAuth 回调 (`/api/auth/callback/google`)
- [x] 用户创建/更新逻辑
- [x] 回调 URL 支持

#### 1.4 前端认证客户端
- [x] 创建 auth-client.ts
- [x] 封装所有认证 API 调用
- [x] Google 登录跳转


### Phase 2: 用户界面 ✅ 已完成

#### 2.1 认证页面
- [x] 设计左侧品牌展示区
- [x] 实现登录/注册表单
- [x] 实现响应式布局
- [x] Google 登录按钮
- [ ] 添加加载状态和错误处理优化

#### 2.2 用户设置页面
- [x] 创建设置页面布局
- [x] 实现个人资料页面
- [x] 实现账户安全页面
- [x] 实现偏好设置页面

#### 2.3 侧边栏更新
- [x] 更新用户状态显示
- [x] 实现登录/未登录状态切换
- [x] 更新用户菜单功能

### Phase 3: 会话关联 ✅ 已完成

#### 3.1 后端实现
- [x] 创建用户会话关联 API (`/api/user/sessions`)
- [x] 实现匿名会话认领逻辑 (`/api/user/sessions/claim`)
- [x] 更新聊天 API 支持用户关联 (chat.py 已更新)
- [x] 会话转移 API (`/api/user/sessions/{id}/transfer`)

#### 3.2 前端实现
- [x] 创建 user-client.ts 封装用户 API
- [x] 侧边栏显示真实用户状态
- [x] 用户菜单功能实现（设置、登出等）
- [ ] 更新会话列表显示用户归属
- [ ] 实现登录后会话同步提示

### Phase 4: 会员体系 ✅ 已完成

#### 4.1 配额管理
- [x] 实现使用统计 API (`/api/user/usage`)
- [x] 订阅页面显示配额使用情况
- [x] 创建配额检查中间件（`backend/api/middleware/quota.py`）

#### 4.2 会员功能
- [x] 设计会员等级权益（Free/Pro/Enterprise）
- [x] 实现会员状态显示
- [x] 订阅页面套餐对比
- [ ] 预留支付集成接口（Stripe）

### Phase 5: 邮箱验证与密码重置 ✅ 已完成

- [x] 邮箱验证功能 (`/api/auth/verify-email`, `/api/auth/send-verification`)
- [x] 忘记密码功能 (`/api/auth/forgot-password`)
- [x] 重置密码功能 (`/api/auth/reset-password`)
- [x] 邮件服务集成 (`backend/services/email.py` - Resend API)
- [x] 前端页面：忘记密码、重置密码、邮箱验证

---

## 6. 文件结构

### 6.1 后端文件

```
backend/
├── api/
│   ├── routes/
│   │   ├── auth.py          # ✅ 认证 API (含邮箱验证、密码重置)
│   │   ├── user.py          # ✅ 用户管理 API
│   │   └── chat.py          # ✅ 聊天 API (支持用户关联)
│   └── middleware/
│       └── quota.py         # ✅ 配额检查中间件 (新增)
├── database/
│   └── db.py                # 数据库连接
├── services/
│   ├── chat_history.py      # ✅ 会话历史服务
│   └── email.py             # ✅ 邮件服务 (新增)
├── migrations/
│   ├── fix_auth_tables.py   # ✅ 认证表迁移
│   └── add_verification_table.py  # ✅ 验证表迁移 (新增)
└── .env                     # 环境变量配置
```

### 6.2 前端文件

```
frontend/src/
├── app/
│   ├── auth/
│   │   ├── sign-in/
│   │   │   └── page.tsx     # ✅ 登录页面
│   │   ├── sign-up/
│   │   │   └── page.tsx     # ✅ 注册页面
│   │   ├── forgot-password/
│   │   │   └── page.tsx     # ✅ 忘记密码页面 (已更新)
│   │   ├── reset-password/
│   │   │   └── page.tsx     # ✅ 重置密码页面 (新增)
│   │   ├── verify-email/
│   │   │   └── page.tsx     # ✅ 邮箱验证页面 (新增)
│   │   └── layout.tsx       # ✅ 认证布局
│   └── (dashboard)/settings/
│       ├── page.tsx         # ✅ 设置主页
│       ├── layout.tsx       # ✅ 设置布局
│       ├── profile/         # ✅ 个人资料
│       ├── account/         # ✅ 账户安全
│       ├── preferences/     # ✅ 偏好设置
│       └── billing/         # ✅ 订阅与账单
├── lib/
│   ├── auth-client.ts       # ✅ 认证客户端 (含密码重置、邮箱验证)
│   └── user-client.ts       # ✅ 用户 API 客户端
├── hooks/
│   └── useAuth.ts           # ✅ 认证 Hook
└── components/
    ├── layout/
    │   └── Sidebar.tsx      # ✅ 侧边栏 (用户状态)
    └── user/
        └── UserAvatar.tsx   # ✅ 用户头像组件
```

---

## 7. 环境变量配置

### 7.1 后端 (.env)

```bash
# JWT 配置
JWT_SECRET=your-secret-key-min-32-chars

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google

# 数据库
DATABASE_URL=postgresql://postgres:password@localhost:54322/postgres

# 邮件服务 (待配置)
# RESEND_API_KEY=your-resend-api-key
# EMAIL_FROM=noreply@yourdomain.com
```

### 7.2 前端 (.env.local)

```bash
# API 地址
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 8. 安全考虑

### 8.1 认证安全
- [x] 使用 HTTPS 传输 (生产环境)
- [x] 密码使用 SHA256 + salt 哈希
- [x] JWT token 使用安全密钥签名
- [x] Token 存储在 HttpOnly Cookie
- [x] 配置合理的 session 过期时间 (7天)
- [ ] 实现 CSRF 保护

### 8.2 OAuth 安全
- [x] 使用 state 参数防止 CSRF
- [x] 验证 OAuth 回调参数
- [ ] 使用 PKCE 流程 (可选增强)

### 8.3 数据安全
- [x] 敏感数据不返回给前端
- [ ] API 请求速率限制
- [x] 输入验证 (Pydantic)
- [x] SQL 注入防护 (参数化查询)

---

## 9. 后续扩展

### 9.1 短期计划
- [ ] 支持更多第三方登录（GitHub）
- [ ] 实现邮箱验证
- [ ] 实现密码重置
- [ ] 添加登录通知

### 9.2 长期计划
- [ ] 实现双因素认证 (2FA)
- [ ] 团队/组织功能
- [ ] API Key 管理
- [ ] 审计日志
- [ ] 支付集成（Stripe）

---

## 10. 变更记录

| 日期 | 变更内容 |
|------|----------|
| 2025-01-12 | 移除 better-auth，改为后端 FastAPI 实现认证 |
| 2025-01-12 | 完成 Google OAuth 登录实现 |
| 2025-01-12 | 更新文档反映当前架构 |
| 2025-01-12 | 实现 Phase 3 会话关联功能 |
| 2025-01-12 | 实现 Phase 4 部分会员体系功能 |
| 2025-01-12 | 更新侧边栏显示真实用户状态 |
| 2025-01-12 | 更新设置页面使用真实 API |
| 2026-01-12 | 完成数据库设计审查，详见 `docs/database_design_review.md` |
| 2026-01-12 | 在 models.py 中添加 User, Account, Session, Verification 模型定义 |
| 2026-01-12 | 为 ChatSession.user_id 添加外键约束和关系定义 |
| 2026-01-12 | 为 ChatMessage 添加 session 关系定义 |
| 2026-01-12 | 创建外键约束迁移脚本 `migrations/add_foreign_key_constraints.py` |
| 2026-01-12 | 实现联网搜索功能 (Tavily API) |
| 2026-01-12 | 实现配额检查中间件 `backend/api/middleware/quota.py` |
| 2026-01-12 | 实现邮件服务 `backend/services/email.py` (Resend API) |
| 2026-01-12 | 实现邮箱验证和密码重置 API |
| 2026-01-12 | 创建前端页面：重置密码、邮箱验证 |

---

## 11. 数据库设计审查结果

详细审查报告见：`docs/database_design_review.md`

### 11.1 已修复的问题

| 问题 | 状态 | 说明 |
|------|------|------|
| 用户认证表缺少 SQLAlchemy 模型 | ✅ 已修复 | 在 models.py 中添加了 User, Account, Session, Verification 模型 |
| ChatSession.user_id 缺少外键约束 | ✅ 已修复 | 添加了 ForeignKey 和 relationship 定义 |
| ChatMessage 缺少 session 关系 | ✅ 已修复 | 添加了 relationship 定义 |

### 11.2 待处理的问题

| 问题 | 优先级 | 说明 |
|------|--------|------|
| 列命名不一致 (camelCase vs snake_case) | P2 | 需要数据迁移，风险较高 |
| LeaderboardEntry.startup_slug 使用字符串关联 | P3 | 影响较小 |
| Founder 表与 Startup 表数据冗余 | P3 | 影响较小 |

### 11.3 模型关系图

```
User (用户表)
├── accounts: Account[] (一对多)
└── chat_sessions: ChatSession[] (一对多)

ChatSession (聊天会话)
├── user: User (多对一)
└── messages: ChatMessage[] (一对多)

ChatMessage (聊天消息)
└── session: ChatSession (多对一)
```
