# 数据库设计审查报告

## 审查日期: 2026-01-12

## 一、发现的问题

### 1. 用户认证表缺少 SQLAlchemy 模型定义 ⚠️ 严重

**问题描述**: `user`, `account`, `session`, `verification` 四张表通过迁移脚本创建，但在 `models.py` 中没有对应的 SQLAlchemy 模型定义。

**影响**:
- 无法使用 ORM 进行类型安全的查询
- 代码中使用原始 SQL 字符串，容易出错
- 无法利用 SQLAlchemy 的关系映射功能

**当前代码示例** (`auth.py`):
```python
# 使用原始 SQL
result = await db.execute(
    text('SELECT * FROM "user" WHERE email = :email'),
    {"email": data.email}
)
```

**建议**: 在 `models.py` 中添加 User, Account, Session, Verification 模型定义。

---

### 2. 列命名不一致 ⚠️ 中等

**问题描述**: 两个迁移脚本使用了不同的命名风格：

| 文件 | 风格 | 示例 |
|------|------|------|
| `fix_auth_tables.py` | camelCase | `"userId"`, `"createdAt"`, `"emailVerified"` |
| `add_user_tables.py` | snake_case | `user_id`, `created_at`, `email_verified` |

**当前实际使用**: `fix_auth_tables.py` 的 camelCase 风格（因为它会 DROP 并重建表）

**影响**:
- 代码中需要使用引号包裹列名 `"userId"` 而非 `user_id`
- 与 Python/SQLAlchemy 的 snake_case 惯例不一致
- 增加维护复杂度

**建议**: 统一使用 snake_case，这是 Python 和 SQLAlchemy 的标准惯例。

---

### 3. ChatSession.user_id 缺少外键约束 ⚠️ 中等

**问题描述**: `ChatSession` 模型中的 `user_id` 字段没有定义外键约束：

```python
class ChatSession(Base):
    # ...
    user_id = Column(String(64), nullable=True, index=True)  # 没有 ForeignKey
```

**影响**:
- 数据库层面无法保证引用完整性
- 可能存在孤立的会话记录（指向不存在的用户）
- 无法使用 ORM 的关系导航

**建议**: 添加外键约束 `ForeignKey("user.id")`

---

### 4. LeaderboardEntry.startup_slug 使用字符串而非外键 ⚠️ 低

**问题描述**: `LeaderboardEntry` 通过 `startup_slug` 字符串关联 `Startup`，而非使用外键：

```python
class LeaderboardEntry(Base):
    startup_slug = Column(String(255), nullable=False, index=True)  # 字符串关联
```

**影响**:
- 无法保证引用完整性
- 如果 Startup 的 slug 变更，需要手动同步
- 查询时需要额外 JOIN

**建议**: 考虑添加 `startup_id` 外键字段，或保留 slug 但添加外键约束。

---

### 5. Founder 表与 Startup 表数据冗余 ⚠️ 低

**问题描述**: `Startup` 表已包含创始人信息字段：
```python
class Startup(Base):
    founder_name = Column(String(255), nullable=True)
    founder_username = Column(String(255), nullable=True, index=True)
    founder_followers = Column(Integer, nullable=True)
    founder_social_platform = Column(String(50), nullable=True)
    founder_avatar_url = Column(String(512), nullable=True)
```

同时存在独立的 `Founder` 表：
```python
class Founder(Base):
    name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False, index=True)
    followers = Column(Integer, nullable=True)
    social_platform = Column(String(50), nullable=True)
```

**影响**:
- 数据可能不同步
- 更新时需要维护两处
- 存储空间浪费

**建议**: 
- 如果一个创始人可能有多个产品，保留 Founder 表并在 Startup 中使用外键
- 如果是一对一关系，考虑移除冗余字段

---

### 6. 缺少 SQLAlchemy relationship() 定义 ⚠️ 中等

**问题描述**: 虽然定义了 ForeignKey，但没有定义 `relationship()`：

```python
class ProductSelectionAnalysis(Base):
    startup_id = Column(Integer, ForeignKey("startups.id"), ...)
    # 缺少: startup = relationship("Startup", back_populates="selection_analysis")
```

**影响**:
- 无法使用 ORM 的关系导航 (如 `analysis.startup.name`)
- 需要手动编写 JOIN 查询
- 代码可读性降低

**建议**: 为所有外键关系添加 `relationship()` 定义。

---

### 7. User 表扩展字段在迁移中定义但未在代码中使用 ⚠️ 低

**问题描述**: `fix_auth_tables.py` 定义了扩展字段：
```sql
plan TEXT DEFAULT 'free',
locale TEXT DEFAULT 'zh-CN',
"dailyChatLimit" INTEGER DEFAULT 10,
"dailyChatUsed" INTEGER DEFAULT 0
```

但这些字段在 `auth.py` 中的使用不完整。

**建议**: 确保所有定义的字段都有对应的业务逻辑。

---

## 二、建议的修复方案

### 方案 A: 添加用户认证模型 (推荐)

在 `models.py` 中添加：

```python
class User(Base):
    """用户表"""
    __tablename__ = "user"
    
    id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    name = Column(String(255), nullable=True)
    image = Column(String(512), nullable=True)
    plan = Column(String(20), default="free")
    locale = Column(String(10), default="zh-CN")
    daily_chat_limit = Column(Integer, default=10)
    daily_chat_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user")


class Account(Base):
    """第三方账户关联表"""
    __tablename__ = "account"
    
    id = Column(String(255), primary_key=True)
    user_id = Column(String(255), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(255), nullable=False)
    provider_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    password = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    
    __table_args__ = (
        Index('ix_account_provider_account', 'provider_id', 'account_id', unique=True),
    )
```

**注意**: `Session` 和 `Verification` 表已移除，当前使用 JWT 无状态认证不需要这些表。

### 方案 B: 统一列命名风格

创建新迁移脚本，将 camelCase 列名改为 snake_case：

```sql
ALTER TABLE "user" RENAME COLUMN "emailVerified" TO email_verified;
ALTER TABLE "user" RENAME COLUMN "createdAt" TO created_at;
-- ... 其他列
```

### 方案 C: 添加缺失的外键约束

```python
class ChatSession(Base):
    user_id = Column(String(64), ForeignKey("user.id"), nullable=True, index=True)
    user = relationship("User", back_populates="chat_sessions")
```

---

## 三、优先级建议

| 优先级 | 问题 | 原因 |
|--------|------|------|
| P0 | 添加 User 等模型定义 | 影响代码质量和类型安全 |
| P1 | ChatSession.user_id 添加外键 | 影响数据完整性 |
| P1 | 添加 relationship() 定义 | 提升开发效率 |
| P2 | 统一列命名风格 | 需要数据迁移，风险较高 |
| P3 | 处理 Founder 数据冗余 | 影响较小 |
| P3 | LeaderboardEntry 外键 | 影响较小 |

---

## 四、当前表结构总览

### 业务数据表 (在 models.py 中定义)
- `startups` - 产品/创业公司信息
- `leaderboard_entries` - 排行榜记录
- `founders` - 创始人信息
- `category_analysis` - 赛道分析
- `product_selection_analysis` - 选品分析
- `landing_page_snapshots` - 落地页快照
- `landing_page_analysis` - 落地页分析
- `comprehensive_analysis` - 综合分析
- `revenue_history` - 收入历史
- `chat_sessions` - 聊天会话
- `chat_messages` - 聊天消息

### 认证表 (在 models.py 中定义)
- `user` - 用户表
- `account` - 账户关联表

### 已移除的表 (JWT 认证不需要)
- `session` - 登录会话表 (使用 JWT 无状态认证)
- `verification` - 验证令牌表 (邮箱验证/密码重置时再添加)

---

## 五、下一步行动

1. **立即**: 在 `models.py` 中添加 User, Account 模型定义
2. **短期**: 为 ChatSession.user_id 添加外键约束
3. **短期**: 添加 relationship() 定义
4. **中期**: 评估是否需要统一列命名风格
5. **长期**: 清理 Founder 数据冗余
