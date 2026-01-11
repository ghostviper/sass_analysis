# 多轮对话功能实现总结

## 问题描述

之前的实现中，Agent 在第二次对话时没有记忆，每次都是全新的对话。

## 根本原因

Claude Agent SDK 的多轮对话需要使用 **checkpoint 机制**来恢复会话上下文。每次对话后，SDK 会返回一个 `UserMessage.uuid` 作为 checkpoint ID，下次对话时传入这个 ID 就可以恢复之前的对话上下文。

## 解决方案

### 1. 数据库层面

**新增字段**: 在 `ChatMessage` 表中添加 `checkpoint_id` 字段

```python
checkpoint_id = Column(String(64), nullable=True, index=True)
```

**迁移脚本**: `backend/migrations/add_checkpoint_id.py`

运行迁移：
```bash
cd backend
python migrations/add_checkpoint_id.py
```

### 2. Agent Client 层面

**修改 `query_stream_events` 方法**:
- 新增 `checkpoint_id` 参数用于恢复会话
- 捕获 `UserMessage.uuid` 作为新的 checkpoint ID
- 在 `done` 事件中返回新的 checkpoint ID

**关键代码**:
```python
# 捕获 checkpoint ID
if isinstance(msg, UserMessage):
    if hasattr(msg, 'uuid') and msg.uuid:
        new_checkpoint_id = msg.uuid

# 返回 checkpoint ID
yield StreamEvent(
    type="done",
    checkpoint_id=new_checkpoint_id
)
```

### 3. Service 层面

**新增方法**: `ChatHistoryService.get_last_checkpoint_id()`

用于获取会话的最后一个 checkpoint ID，以便恢复会话。

**修改方法**: `ChatHistoryService.add_message()`

新增 `checkpoint_id` 参数，保存 checkpoint ID 到数据库。

### 4. API 层面

**修改流式端点** (`/chat/stream`):

1. **获取 checkpoint**: 从数据库获取最后一个 checkpoint ID
2. **传入 checkpoint**: 调用 agent 时传入 checkpoint ID
3. **捕获新 checkpoint**: 从 `done` 事件中获取新的 checkpoint ID
4. **保存 checkpoint**: 持久化时保存新的 checkpoint ID

**关键流程**:
```python
# 1. 获取最后一个 checkpoint
last_checkpoint = await ChatHistoryService.get_last_checkpoint_id(session_id)

# 2. 传入 checkpoint 恢复会话
async for event in agent.query_stream_events(
    message,
    session_id=session_id,
    checkpoint_id=last_checkpoint  # 恢复会话
):
    if event.type == "done":
        new_checkpoint_id = event.checkpoint_id  # 捕获新 checkpoint

# 3. 保存新 checkpoint
await ChatHistoryService.add_message(
    session_id=session_id,
    role="assistant",
    content=content,
    checkpoint_id=new_checkpoint_id  # 保存
)
```

## 工作原理

### 第一轮对话

```
用户: "有哪些高收入的 SaaS 产品？"
  ↓
Agent: 查询数据库，返回结果
  ↓
SDK: 生成 checkpoint_id = "abc123"
  ↓
数据库: 保存消息 + checkpoint_id
```

### 第二轮对话

```
用户: "还有其他的吗？"
  ↓
数据库: 获取 last_checkpoint_id = "abc123"
  ↓
Agent: 使用 checkpoint_id 恢复会话
  ↓
SDK: 恢复上下文，理解"其他的"指的是"SaaS 产品"
  ↓
Agent: 返回更多结果
  ↓
SDK: 生成新的 checkpoint_id = "def456"
  ↓
数据库: 保存消息 + 新的 checkpoint_id
```

## 关键配置

在 `_create_options` 中启用 `replay-user-messages`:

```python
options = {
    "extra_args": {"replay-user-messages": None},  # 启用 UserMessage UUID
    # ... 其他配置
}
```

这个配置让 SDK 返回 `UserMessage.uuid`，作为 checkpoint ID。

## 测试方法

### 1. 运行迁移

```bash
cd backend
python migrations/add_checkpoint_id.py
```

### 2. 启动服务

```bash
cd backend
python run_server.py
```

### 3. 测试多轮对话

**第一轮**:
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "有哪些高收入的 SaaS 产品？"}'
```

记录返回的 `session_id` 和 `checkpoint_id`。

**第二轮**:
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "还有其他的吗？",
    "session_id": "<第一轮返回的 session_id>"
  }'
```

Agent 应该能理解"其他的"指的是"SaaS 产品"。

## 优势

1. **性能优化**: 使用 checkpoint 恢复会话，无需重放历史消息
2. **SDK 原生支持**: 利用 Claude Agent SDK 的原生功能
3. **持久化**: checkpoint ID 保存在数据库中，会话可以跨请求恢复
4. **可扩展**: 支持长对话，不受内存限制

## 注意事项

1. **Checkpoint 有效期**: SDK 的 checkpoint 可能有时效性，过期后需要降级到其他方案
2. **数据库迁移**: 需要运行迁移脚本添加 `checkpoint_id` 字段
3. **向后兼容**: 旧的会话没有 checkpoint ID，会自动创建新会话

## 备选方案

如果 checkpoint 机制失效，可以降级到**手动重建历史**:

```python
# 从数据库获取历史消息
history = await ChatHistoryService.get_recent_messages(session_id, count=10)

# 重放历史消息
async with ClaudeSDKClient(options=options) as client:
    for msg in history:
        if msg["role"] == "user":
            await client.query(msg["content"])
            async for _ in client.receive_response():
                pass  # 等待响应完成
    
    # 发送新消息
    await client.query(new_message)
```

## 相关文件

- `backend/agent/client.py` - Agent Client 实现
- `backend/api/routes/chat.py` - API 路由
- `backend/services/chat_history.py` - 历史记录服务
- `backend/database/models.py` - 数据库模型
- `backend/migrations/add_checkpoint_id.py` - 数据库迁移
- `backend/agent/MULTI_TURN_IMPLEMENTATION.md` - 详细实现方案

## 总结

通过引入 Claude Agent SDK 的 checkpoint 机制，成功实现了多轮对话功能。Agent 现在可以记住之前的对话内容，理解上下文，提供更自然的对话体验。
