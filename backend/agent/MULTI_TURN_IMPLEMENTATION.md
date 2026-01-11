# 多轮对话实现方案

## 问题分析

当前实现的问题：
1. 每次请求都创建新的 `ClaudeSDKClient` 实例
2. 虽然传入了 `session_id`，但 SDK 无法恢复之前的对话上下文
3. Agent 没有"记忆"，每次都是全新的对话

## Claude Agent SDK 的多轮对话机制

根据官方文档，有两种方式实现多轮对话：

### 方式 1: 在同一个 Client 实例中连续查询

```python
async with ClaudeSDKClient() as client:
    # 第一轮
    await client.query("What's the capital of France?")
    async for msg in client.receive_response():
        # 处理响应
        pass
    
    # 第二轮 - 在同一个 client 中，自动有上下文
    await client.query("What's the population of that city?")
    async for msg in client.receive_response():
        # 处理响应
        pass
```

**优点**: 简单直接，SDK 自动管理上下文
**缺点**: 需要保持 client 实例存活，不适合 HTTP 请求/响应模式

### 方式 2: 使用 resume 参数恢复会话

```python
# 第一次对话
options1 = ClaudeAgentOptions(
    extra_args={"replay-user-messages": None}  # 启用 UserMessage UUID
)
async with ClaudeSDKClient(options=options1) as client:
    await client.query("First question")
    checkpoint_id = None
    async for msg in client.receive_response():
        if isinstance(msg, UserMessage) and msg.uuid:
            checkpoint_id = msg.uuid  # 保存 checkpoint

# 第二次对话 - 恢复到 checkpoint
options2 = ClaudeAgentOptions(
    resume=checkpoint_id,  # 使用 checkpoint 恢复
    extra_args={"replay-user-messages": None}
)
async with ClaudeSDKClient(options=options2) as client:
    await client.query("Follow-up question")
    async for msg in client.receive_response():
        # 处理响应
        pass
```

**优点**: 适合 HTTP 请求/响应模式
**缺点**: 需要保存和管理 checkpoint ID

## 推荐方案：混合方式

结合数据库历史记录和 SDK 的 resume 功能：

1. **保存 checkpoint**: 每次对话后保存 UserMessage UUID 作为 checkpoint
2. **恢复会话**: 使用最后一个 checkpoint 恢复会话
3. **历史回退**: 如果 checkpoint 失效，从数据库重建对话历史

## 实现步骤

### 1. 修改数据库模型

在 `ChatMessage` 表中添加 `checkpoint_id` 字段：

```python
class ChatMessage(Base):
    # ... 现有字段 ...
    checkpoint_id = Column(String(64), nullable=True, index=True)  # UserMessage UUID
```

### 2. 修改 Agent Client

```python
async def query_stream_events(
    self,
    message: str,
    session_id: Optional[str] = None,
    checkpoint_id: Optional[str] = None,  # 新增：checkpoint ID
    enable_web_search: bool = False,
    context: Optional[Dict[str, Any]] = None
) -> AsyncIterator[StreamEvent]:
    # 使用 checkpoint_id 作为 resume 参数
    options = self._create_options(resume=checkpoint_id)
    
    async with ClaudeSDKClient(options=options) as client:
        await client.query(message)
        
        new_checkpoint_id = None
        async for msg in client.receive_response():
            # 捕获新的 checkpoint ID
            if isinstance(msg, UserMessage) and msg.uuid:
                new_checkpoint_id = msg.uuid
            
            # ... 处理其他消息 ...
        
        # 返回新的 checkpoint ID
        yield StreamEvent(
            type="done",
            session_id=session_id,
            checkpoint_id=new_checkpoint_id
        )
```

### 3. 修改 API 路由

```python
@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        session_id = request.session_id or str(uuid.uuid4())
        
        # 获取最后一个 checkpoint
        last_checkpoint = None
        if request.session_id:
            messages = await ChatHistoryService.get_recent_messages(session_id, count=1)
            if messages:
                last_checkpoint = messages[-1].get("checkpoint_id")
        
        # 使用 checkpoint 恢复会话
        async for event in agent.query_stream_events(
            request.message,
            session_id=session_id,
            checkpoint_id=last_checkpoint,  # 传入 checkpoint
            enable_web_search=request.enable_web_search,
            context=request.context
        ):
            # 保存新的 checkpoint
            if event.type == "done" and event.checkpoint_id:
                # 保存到数据库
                pass
            
            yield f"data: {json.dumps(event.to_dict())}\n\n"
```

## 备选方案：手动重建历史

如果 checkpoint 机制不稳定，可以手动重建对话历史：

```python
async def query_with_history(
    self,
    message: str,
    history: List[Dict[str, str]],  # [{"role": "user", "content": "..."}, ...]
) -> AsyncIterator[StreamEvent]:
    options = self._create_options()
    
    async with ClaudeSDKClient(options=options) as client:
        # 重放历史消息（仅最近几轮）
        for msg in history[-10:]:  # 只重放最近10条
            if msg["role"] == "user":
                await client.query(msg["content"])
                # 等待响应完成
                async for _ in client.receive_response():
                    pass
        
        # 发送新消息
        await client.query(message)
        async for msg in client.receive_response():
            # 处理响应
            yield ...
```

**优点**: 不依赖 checkpoint，完全可控
**缺点**: 性能开销大，每次都要重放历史

## 最终推荐

使用 **checkpoint 方式**，原因：
1. 性能最优，SDK 原生支持
2. 适合 HTTP 请求/响应模式
3. 可以结合数据库实现持久化

如果 checkpoint 失效（过期、丢失），可以降级到手动重建历史。
