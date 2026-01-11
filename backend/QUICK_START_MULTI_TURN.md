# 多轮对话功能 - 快速开始

## 1. 运行数据库迁移

首先需要添加 `checkpoint_id` 字段到数据库：

```bash
cd backend
python migrations/add_checkpoint_id.py
```

预期输出：
```
开始数据库迁移: 添加 checkpoint_id 字段
正在添加 checkpoint_id 列...
✓ checkpoint_id 列添加成功
迁移完成
```

## 2. 启动后端服务

```bash
cd backend
python run_server.py
```

## 3. 测试多轮对话

### 方式 1: 使用 curl

**第一轮对话**:
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "有哪些高收入的 AI 产品？"
  }'
```

从响应中找到 `session_id`（在 `done` 事件中）。

**第二轮对话**（使用相同的 session_id）:
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "这些产品的技术复杂度如何？",
    "session_id": "<第一轮返回的 session_id>"
  }'
```

Agent 应该能理解"这些产品"指的是第一轮提到的"AI 产品"。

### 方式 2: 使用前端

1. 启动前端：
```bash
cd frontend
pnpm dev
```

2. 打开浏览器访问 `http://localhost:3000`

3. 在聊天界面进行多轮对话：
   - 第一轮: "有哪些高收入的 AI 产品？"
   - 第二轮: "这些产品的技术复杂度如何？"
   - 第三轮: "还有其他推荐吗？"

## 4. 验证多轮对话是否工作

### 检查数据库

```bash
cd backend
python -c "
import asyncio
from services.chat_history import ChatHistoryService

async def check():
    # 替换为你的 session_id
    session_id = 'your-session-id'
    
    # 获取消息
    messages = await ChatHistoryService.get_messages(session_id)
    
    print(f'会话消息数: {len(messages)}')
    for msg in messages:
        print(f'- {msg[\"role\"]}: {msg[\"content\"][:50]}...')
        if msg.get('checkpoint_id'):
            print(f'  checkpoint_id: {msg[\"checkpoint_id\"]}')
    
    # 获取最后一个 checkpoint
    checkpoint = await ChatHistoryService.get_last_checkpoint_id(session_id)
    print(f'\\n最后一个 checkpoint: {checkpoint}')

asyncio.run(check())
"
```

### 检查日志

在服务器日志中查找：
```
[DEBUG] Resuming session with checkpoint: <checkpoint_id>
[DEBUG] Captured checkpoint ID: <new_checkpoint_id>
[DEBUG] New checkpoint ID: <new_checkpoint_id>
```

## 5. 常见问题

### Q: Agent 还是没有记忆？

**检查清单**:
1. ✅ 数据库迁移是否成功？
2. ✅ 是否传入了正确的 `session_id`？
3. ✅ 日志中是否显示 "Resuming session with checkpoint"？
4. ✅ 数据库中是否保存了 `checkpoint_id`？

**调试步骤**:
```bash
# 1. 检查数据库表结构
cd backend
python -c "
import asyncio
from database.db import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text('PRAGMA table_info(chat_messages)'))
        columns = result.fetchall()
        print('chat_messages 表字段:')
        for col in columns:
            print(f'  - {col[1]} ({col[2]})')

asyncio.run(check())
"

# 2. 查看最近的消息
python -c "
import asyncio
from services.chat_history import ChatHistoryService

async def check():
    sessions = await ChatHistoryService.list_sessions(limit=5)
    print(f'最近的 {len(sessions)} 个会话:')
    for s in sessions:
        print(f'- {s[\"session_id\"]}: {s[\"title\"]} ({s[\"message_count\"]} 条消息)')

asyncio.run(check())
"
```

### Q: Checkpoint ID 为空？

可能原因：
1. `extra_args={"replay-user-messages": None}` 配置未生效
2. Claude Agent SDK 版本过旧

**解决方案**:
```bash
# 更新 SDK
pip install --upgrade claude-agent-sdk
```

### Q: 会话过期？

Checkpoint 可能有时效性（默认 30 分钟）。如果会话过期：
- 系统会自动创建新会话
- 用户会看到提示："会话已过期，开始新会话..."

## 6. 性能优化建议

### 限制历史消息数量

如果对话轮数很多，可以限制恢复的历史：

```python
# 在 agent/client.py 中
self.max_turns = int(os.getenv("CLAUDE_MAX_TURNS", "10"))  # 最多10轮
```

### 清理过期会话

定期清理过期的会话和 checkpoint：

```bash
cd backend
python -c "
import asyncio
from datetime import datetime, timedelta
from database.db import AsyncSessionLocal
from database.models import ChatSession
from sqlalchemy import select, delete

async def cleanup():
    async with AsyncSessionLocal() as db:
        # 删除 7 天前的会话
        cutoff = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            delete(ChatSession).where(ChatSession.updated_at < cutoff)
        )
        await db.commit()
        print(f'清理了 {result.rowcount} 个过期会话')

asyncio.run(cleanup())
"
```

## 7. 下一步

- ✅ 多轮对话已实现
- 📝 可以添加会话管理界面（查看/删除历史会话）
- 📝 可以添加会话导出功能
- 📝 可以添加会话分享功能

## 相关文档

- [详细实现方案](./agent/MULTI_TURN_IMPLEMENTATION.md)
- [完整总结](./MULTI_TURN_CHAT_SUMMARY.md)
- [MCP 工具优化](./agent/OPTIMIZATION_SUMMARY.md)
