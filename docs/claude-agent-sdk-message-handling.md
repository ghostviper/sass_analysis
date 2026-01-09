# Claude Agent SDK 消息处理分析文档

> 本文档详细介绍 Claude Agent SDK 的消息类型、内容块结构，以及如何实现消息分类、封装和美化。

## 目录

- [消息类型概览](#消息类型概览)
- [内容块类型](#内容块类型)
- [ResultMessage 子类型](#resultmessage-子类型)
- [消息处理策略](#消息处理策略)
- [实现示例](#实现示例)
- [最佳实践](#最佳实践)

---

## 消息类型概览

Claude Agent SDK 定义了五种主要消息类型，每种消息类型代表不同的通信阶段和目的：

### 1. UserMessage - 用户消息

**用途**: 表示用户发送给 Claude 的消息，包含用户提示词或工具执行结果。

**数据结构**:
```python
@dataclass
class UserMessage:
    content: str | list[ContentBlock]
    uuid: str | None = None  # 启用 replay-user-messages 时可用
```

**包含内容**:
- 用户的文本提示
- 工具执行结果（ToolResultBlock）
- 可选的消息 UUID（用于多轮对话跟踪）

**处理要点**:
- `content` 可以是简单字符串或内容块列表
- 包含 ToolResultBlock 时表示这是工具执行的返回
- UUID 可用于关联用户输入和 Agent 响应

---

### 2. AssistantMessage - 助手消息

**用途**: 表示 Claude 的响应，包含文本回复、思考过程和工具调用。

**数据结构**:
```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
    error: dict | None = None
    stop_reason: str | None = None
```

**包含内容**:
- TextBlock - Claude 的文本回复
- ThinkingBlock - Claude 的推理过程（需启用 extended_thinking）
- ToolUseBlock - Claude 请求执行的工具调用

**处理要点**:
- `content` 始终是列表，可能包含多个不同类型的内容块
- `error` 字段用于检测 API 错误（如速率限制、认证失败等）
- `model` 字段标识使用的具体模型（如 claude-sonnet-4-5）

---

### 3. SystemMessage - 系统消息

**用途**: Claude Code 内部事件通知，用于传递系统状态和元数据。

**数据结构**:
```python
@dataclass
class SystemMessage:
    subtype: str
    data: dict[str, Any]
```

**常见子类型**:
- `tool_execution_start` - 工具开始执行
- `tool_execution_end` - 工具执行完成
- `permission_request` - 权限请求（需要用户确认）
- `status_update` - 状态更新

**处理要点**:
- 主要用于调试和状态跟踪
- `data` 字段包含具体事件的详细信息
- 不应直接展示给用户，应转换为友好的状态提示

---

### 4. ResultMessage - 结果消息

**用途**: 表示整个会话的最终结果，包含性能指标、成本统计和会话元数据。

**数据结构**:
```python
@dataclass
class ResultMessage:
    subtype: str                      # 结果类型（success 或各种错误类型）
    duration_ms: int                  # 总耗时（毫秒）
    duration_api_ms: int              # API 调用耗时（毫秒）
    is_error: bool                    # 是否发生错误
    num_turns: int                    # 对话轮数
    session_id: str                   # 会话 ID（用于多轮对话恢复）
    total_cost_usd: float | None      # 总成本（美元）
    usage: dict[str, Any] | None      # Token 使用统计
    result: str | None                # 文本结果（仅 success 时）
    errors: list[str] | None          # 错误列表（仅错误时）
```

**处理要点**:
- 始终是流中的最后一条消息
- `session_id` 非常重要，用于实现多轮对话恢复
- `usage` 包含详细的 token 统计（input_tokens, output_tokens）

---

### 5. StreamEvent - 流式事件

**用途**: 实时流式传输过程中的部分更新事件（需启用 `include_partial_messages`）。

**数据结构**:
```python
@dataclass
class StreamEvent:
    event: str
    data: dict[str, Any]
```

**常见事件类型**:
- `content_block_start` - 内容块开始
- `content_block_delta` - 内容块增量更新
- `content_block_stop` - 内容块结束
- `message_start` - 消息开始
- `message_delta` - 消息增量
- `message_stop` - 消息结束

**处理要点**:
- 用于实现打字机效果和实时 UI 更新
- 需要维护状态来累积增量内容
- 不是所有 SDK 使用场景都需要处理 StreamEvent

---

## 内容块类型

内容块（ContentBlock）是消息内容的最小单位，定义了不同类型的信息载体：

### 1. TextBlock - 文本块

**用途**: 纯文本内容，Claude 的最终回复。

```python
@dataclass
class TextBlock:
    text: str
```

**展示方式**:
- 直接展示给用户
- 通常是用户最关心的内容
- 可以使用 Markdown 渲染

---

### 2. ThinkingBlock - 思考块

**用途**: Claude 的推理过程（Extended Thinking），展示 Claude 如何思考问题。

```python
@dataclass
class ThinkingBlock:
    thinking: str
    signature: str
```

**展示方式**:
- 可折叠面板（默认收起）
- 标记为"思考过程"或"推理过程"
- 适合调试和理解 Claude 的决策逻辑
- 可选展示（高级用户功能）

---

### 3. ToolUseBlock - 工具使用块

**用途**: Claude 请求执行的工具调用，包含工具名称和参数。

```python
@dataclass
class ToolUseBlock:
    id: str                    # 工具调用 ID（与 ToolResultBlock 关联）
    name: str                  # 工具名称（如 "Read", "Write", "Bash"）
    input: dict[str, Any]      # 工具参数
```

**展示方式**:
- 转换为用户友好的动作描述
- 示例：`{"name": "Read", "input": {"file_path": "config.py"}}` → "正在读取文件 config.py"
- 时间轴展示（工具调用序列）
- 可展开查看详细参数

---

### 4. ToolResultBlock - 工具结果块

**用途**: 工具执行的结果，包含输出内容或错误信息。

```python
@dataclass
class ToolResultBlock:
    tool_use_id: str                           # 关联的 ToolUseBlock ID
    content: str | list[dict[str, Any]] | None # 工具输出内容
    is_error: bool | None                      # 是否执行失败
```

**展示方式**:
- 折叠展示（避免干扰主要内容）
- 错误时高亮显示（红色边框或图标）
- 关联到对应的 ToolUseBlock（通过 tool_use_id）
- 可选展示（调试模式）

---

## ResultMessage 子类型

ResultMessage 的 `subtype` 字段指示会话的最终状态：

### 成功类型

| 子类型 | 说明 | 处理方式 |
|--------|------|----------|
| `success` | 会话成功完成 | 显示成功提示，展示结果 |

### 错误类型

| 子类型 | 说明 | 处理方式 |
|--------|------|----------|
| `error_max_turns` | 达到最大对话轮数限制 | 提示用户会话已达上限，建议重新开始 |
| `error_during_execution` | 执行过程中发生错误 | 显示错误详情，提供重试选项 |
| `error_max_budget_usd` | 超出预算限制 | 提示成本超限，建议调整预算或重新配置 |
| `error_max_structured_output_retries` | 结构化输出重试次数超限 | 提示格式化失败，建议简化输出要求 |

**示例处理代码**:
```python
def format_result_message(result: ResultMessage) -> str:
    if result.subtype == "success":
        return f"✅ 成功完成 ({result.num_turns} 轮对话，耗时 {result.duration_ms}ms)"
    elif result.subtype == "error_max_turns":
        return f"⚠️ 已达最大对话轮数 ({result.num_turns} 轮)"
    elif result.subtype == "error_during_execution":
        errors = ", ".join(result.errors) if result.errors else "未知错误"
        return f"❌ 执行失败: {errors}"
    elif result.subtype == "error_max_budget_usd":
        return f"💰 超出预算限制 (${result.total_cost_usd:.4f})"
    elif result.subtype == "error_max_structured_output_retries":
        return f"🔄 结构化输出重试失败"
    else:
        return f"❓ 未知结果: {result.subtype}"
```

---

## 消息处理策略

### 1. 消息分类层次

建议将消息处理分为三个层次：

```
┌─────────────────────────────────────────┐
│          Primary Layer (主要层)          │
│  - TextBlock (用户最终关心的回复)        │
│  - ResultMessage (最终结果摘要)          │
└─────────────────────────────────────────┘
           ↑
┌─────────────────────────────────────────┐
│         Process Layer (过程层)           │
│  - ToolUseBlock (工具调用过程)           │
│  - SystemMessage (系统状态)              │
│  - ToolResultBlock (工具执行结果)        │
└─────────────────────────────────────────┘
           ↑
┌─────────────────────────────────────────┐
│          Debug Layer (调试层)            │
│  - ThinkingBlock (推理过程)              │
│  - StreamEvent (流式事件)                │
│  - 详细的元数据和统计信息                │
└─────────────────────────────────────────┘
```

**展示策略**:
- **Primary Layer**: 始终展示，用户主要关注内容
- **Process Layer**: 默认折叠，提供展开选项
- **Debug Layer**: 默认隐藏，仅在开发者模式下显示

---

### 2. 消息序列化与封装

**目标**: 将 SDK 原始消息转换为前端友好的数据结构。

**核心原则**:
1. **信息压缩**: 提取关键信息，隐藏不必要的技术细节
2. **友好描述**: 将技术术语转换为用户可理解的文案
3. **层次分明**: 明确区分主要内容、过程信息和调试数据
4. **可追溯性**: 保留原始消息的引用，便于调试

**示例数据结构**:
```typescript
interface SerializedMessage {
  id: string;                    // 消息 ID
  type: 'user' | 'assistant' | 'system' | 'result';
  timestamp: Date;               // 时间戳

  // Primary content
  text?: string;                 // 主要文本内容

  // Process information
  toolCalls?: ToolCallInfo[];    // 工具调用列表
  toolResults?: ToolResultInfo[]; // 工具结果列表

  // Debug information
  thinking?: string;             // 思考过程
  metadata?: Record<string, any>; // 元数据

  // Result metadata
  duration?: number;             // 耗时
  cost?: number;                 // 成本
  status?: 'success' | 'error';  // 状态
}

interface ToolCallInfo {
  id: string;
  name: string;
  friendlyName: string;          // 友好名称
  description: string;           // 用户可读描述
  input?: Record<string, any>;   // 输入参数（可选展示）
  timestamp: Date;
}

interface ToolResultInfo {
  toolCallId: string;            // 关联的工具调用
  isError: boolean;
  summary: string;               // 结果摘要
  details?: string;              // 详细内容（可选展示）
}
```

---

### 3. 工具调用美化映射

将技术性的工具名称和参数转换为用户友好的描述：

```python
TOOL_FRIENDLY_NAMES = {
    "load_pdf": "📄 加载 PDF 文档",
    "list_all_fields": "🔍 扫描表单字段",
    "search_fields": "🔎 搜索字段",
    "set_field": "✏️ 填写字段",
    "commit_edits": "💾 保存表单",
    "get_pending_edits": "📋 预览更改",
}

def get_friendly_tool_description(tool_name: str, tool_input: dict) -> str:
    """将工具调用转换为用户友好的描述"""

    if tool_name == "load_pdf":
        return "正在加载 PDF 文档..."

    elif tool_name == "list_all_fields":
        return "正在扫描表单中的所有字段..."

    elif tool_name == "search_fields":
        query = tool_input.get("query", "")
        return f"正在搜索 '{query}' 相关字段..."

    elif tool_name == "set_field":
        field_id = tool_input.get("field_id", "")
        value = tool_input.get("value", "")
        field_label = get_field_label(field_id)  # 从 session 获取友好标签

        # 截断过长的值
        value_preview = str(value)[:25] + "..." if len(str(value)) > 25 else str(value)

        if field_label:
            return f"**{field_label}**: '{value_preview}'"
        else:
            return f"正在设置字段为 '{value_preview}'"

    elif tool_name == "commit_edits":
        return "正在保存填写好的表单..."

    elif tool_name == "get_pending_edits":
        return "正在检查待保存的更改..."

    else:
        # 默认处理：格式化工具名称
        formatted_name = tool_name.replace("_", " ").title()
        return f"正在执行: {formatted_name}"
```

---

### 4. 流式更新处理

**挑战**: 流式响应需要维护状态，累积增量内容。

**解决方案**: 使用块 ID（block_id）跟踪和更新内容块。

```python
class StreamProcessor:
    def __init__(self):
        self.blocks = {}  # block_id -> accumulated content
        self.current_message = None

    async def process_stream_event(self, event: StreamEvent):
        event_type = event.event
        data = event.data

        if event_type == "content_block_start":
            block_id = data.get("index")
            block_type = data.get("content_block", {}).get("type")
            self.blocks[block_id] = {
                "type": block_type,
                "content": "",
            }

        elif event_type == "content_block_delta":
            block_id = data.get("index")
            delta = data.get("delta", {})

            if "text" in delta:
                self.blocks[block_id]["content"] += delta["text"]
                yield self._create_text_update(block_id, delta["text"])

            elif "thinking" in delta:
                self.blocks[block_id]["content"] += delta["thinking"]
                yield self._create_thinking_update(block_id, delta["thinking"])

        elif event_type == "content_block_stop":
            block_id = data.get("index")
            yield self._create_block_complete(block_id)

    def _create_text_update(self, block_id: int, delta: str):
        return {
            "type": "block_delta",
            "layer": "primary",
            "block_id": f"block_{block_id}",
            "block_type": "text",
            "content": delta,
        }

    def _create_thinking_update(self, block_id: int, delta: str):
        return {
            "type": "block_delta",
            "layer": "debug",
            "block_id": f"block_{block_id}",
            "block_type": "thinking",
            "content": delta,
        }

    def _create_block_complete(self, block_id: int):
        return {
            "type": "block_end",
            "block_id": f"block_{block_id}",
        }
```

---

## 实现示例

### 示例 1: 基础消息处理循环

```python
from claude_agent_sdk import (
    ClaudeSDKClient,
    AssistantMessage,
    UserMessage,
    SystemMessage,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ToolResultBlock,
)

async def process_agent_conversation(prompt: str):
    async with ClaudeSDKClient() as client:
        await client.query(prompt)

        async for message in client.receive_response():
            # 处理用户消息
            if isinstance(message, UserMessage):
                if isinstance(message.content, str):
                    print(f"[USER] {message.content}")
                else:
                    for block in message.content:
                        if isinstance(block, ToolResultBlock):
                            status = "❌" if block.is_error else "✅"
                            print(f"[TOOL RESULT {status}] {block.tool_use_id}")

            # 处理助手消息
            elif isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"[CLAUDE] {block.text}")

                    elif isinstance(block, ThinkingBlock):
                        print(f"[THINKING] {block.thinking[:100]}...")

                    elif isinstance(block, ToolUseBlock):
                        friendly = get_friendly_tool_description(block.name, block.input)
                        print(f"[TOOL CALL] {friendly}")

            # 处理系统消息
            elif isinstance(message, SystemMessage):
                print(f"[SYSTEM] {message.subtype}: {message.data}")

            # 处理结果消息
            elif isinstance(message, ResultMessage):
                status = "SUCCESS" if not message.is_error else "ERROR"
                print(f"[{status}] {message.num_turns} turns, ${message.total_cost_usd:.4f}")
                if message.result:
                    print(f"Result: {message.result}")
```

---

### 示例 2: 前端友好的日志条目生成

参考 `form-filling-exp/web/src/app/page.tsx` 的实现：

```typescript
interface AgentLogEntry {
  id: string;
  type: 'status' | 'tool_call' | 'tool_result' | 'thinking' | 'complete' | 'error';
  timestamp: Date;
  content: string;
  details?: string;  // 可选的详细信息
}

function createLogEntry(event: StreamEvent): AgentLogEntry | null {
  const id = generateId();
  const timestamp = new Date();

  switch (event.type) {
    case 'init':
      return {
        id,
        type: 'status',
        timestamp,
        content: event.message || '正在初始化 Agent...',
      };

    case 'status':
      return {
        id,
        type: 'status',
        timestamp,
        content: event.message || '处理中...',
      };

    case 'tool_use':
      // 处理工具调用，支持并行调用
      if (event.friendly && event.friendly.length > 0) {
        const cleanedActions = event.friendly.map((f) => f.replace(/\*\*/g, ''));

        if (event.friendly.length > 1) {
          return {
            id,
            type: 'tool_call',
            timestamp,
            content: `正在填写 ${event.friendly.length} 个字段`,
            details: cleanedActions.join(', '),
          };
        } else {
          return {
            id,
            type: 'tool_call',
            timestamp,
            content: cleanedActions[0],
          };
        }
      }
      return null;

    case 'user':
      // 工具结果
      if (event.friendly && event.friendly.length > 0) {
        return {
          id,
          type: 'tool_result',
          timestamp,
          content: event.friendly.join(', '),
        };
      }
      return null;

    case 'assistant':
      if (event.text) {
        return {
          id,
          type: 'thinking',
          timestamp,
          content: 'Agent 正在思考...',
          details: event.text.slice(0, 100) + (event.text.length > 100 ? '...' : ''),
        };
      }
      return null;

    case 'complete':
      return {
        id,
        type: 'complete',
        timestamp,
        content: `已完成 - 填写了 ${event.applied_count || 0} 个字段`,
      };

    case 'error':
      return {
        id,
        type: 'error',
        timestamp,
        content: event.error || '发生错误',
      };

    default:
      return null;
  }
}
```

---

### 示例 3: 后端消息序列化

参考 `form-filling-exp/backend/agent.py` 的实现：

```python
def _serialize_message(message) -> dict:
    """将 Agent 消息转换为 JSON 可序列化的字典，包含用户友好信息"""
    msg_dict = {"type": "unknown"}

    # 检查消息类型
    if isinstance(message, AssistantMessage):
        msg_dict["type"] = "assistant"
        texts = []
        tool_calls = []

        for block in message.content:
            if isinstance(block, TextBlock):
                texts.append(block.text)
            elif isinstance(block, ToolUseBlock):
                tool_name = block.name
                tool_input = block.input

                # 生成用户友好描述
                friendly_desc = get_friendly_tool_description(tool_name, tool_input)

                tool_calls.append({
                    "name": tool_name,
                    "input": tool_input if isinstance(tool_input, dict) else str(tool_input)[:200],
                    "friendly": friendly_desc
                })

        if texts:
            msg_dict["text"] = " ".join(texts)
        if tool_calls:
            msg_dict["tool_calls"] = tool_calls
            msg_dict["type"] = "tool_use"
            # 添加组合的友好消息（用于并行调用）
            friendly_msgs = [tc["friendly"] for tc in tool_calls if tc.get("friendly")]
            if friendly_msgs:
                msg_dict["friendly"] = friendly_msgs

    elif isinstance(message, UserMessage):
        msg_dict["type"] = "user"
        # 尝试解析工具结果，生成友好显示
        if hasattr(message, "content"):
            content = message.content
            msg_dict["content"] = str(content)[:500]
            # 检查是否为工具结果
            friendly = parse_tool_result_friendly(content)
            if friendly:
                msg_dict["friendly"] = friendly

    elif isinstance(message, SystemMessage):
        msg_dict["type"] = "system"
        msg_dict["subtype"] = message.subtype
        if hasattr(message, "content"):
            msg_dict["content"] = str(message.content)[:500]

    elif isinstance(message, ResultMessage):
        msg_dict["type"] = "result"
        msg_dict["subtype"] = message.subtype
        msg_dict["is_error"] = message.is_error
        msg_dict["session_id"] = message.session_id
        msg_dict["duration_ms"] = message.duration_ms
        msg_dict["num_turns"] = message.num_turns
        if message.total_cost_usd:
            msg_dict["total_cost_usd"] = message.total_cost_usd
        if message.usage:
            msg_dict["usage"] = message.usage

    return msg_dict


def parse_tool_result_friendly(content) -> str | None:
    """从工具结果中提取用户友好信息"""
    try:
        # content 可能是列表或字符串
        if isinstance(content, list):
            for item in content:
                if hasattr(item, "content"):
                    text = item.content
                    if isinstance(text, str):
                        data = json.loads(text)
                        return format_tool_result(data)
        elif isinstance(content, str):
            data = json.loads(content)
            return format_tool_result(data)
    except:
        pass
    return None


def format_tool_result(data: dict) -> str | None:
    """将工具结果数据格式化为用户友好文本"""
    if not isinstance(data, dict):
        return None

    # PDF 加载成功
    if "field_count" in data and "success" in data:
        count = data.get("field_count", 0)
        return f"找到 {count} 个表单字段"

    # 字段设置成功
    if "field_id" in data and "value" in data and "pending_count" in data:
        value = str(data.get("value", ""))[:30]
        pending = data.get("pending_count", 0)
        return f"已暂存: '{value}' ({pending} 个更改待保存)"

    # 提交编辑成功
    if "applied_count" in data:
        count = data.get("applied_count", 0)
        total = data.get("total_fields_filled", count)
        if total > count:
            return f"已应用 {count} 个更改 (共 {total} 个字段已填写)"
        return f"已应用 {count} 个字段更改"

    # 待提交编辑预览
    if "pending_edits" in data:
        edits = data.get("pending_edits", [])
        if edits:
            return f"准备应用 {len(edits)} 个更改"

    return None
```

---

### 示例 4: 实时流式更新（前端）

```typescript
async function streamFromBackend(params: StreamParams) {
  const response = await fetch('/api/agent/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();

  // 维护内容块状态
  const blocks: Record<string, { type: string; content: string }> = {};

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;

      const data = JSON.parse(line.slice(6));

      if (data.type === 'block_start') {
        blocks[data.block_id] = {
          type: data.block_type,
          content: '',
        };
      } else if (data.type === 'block_delta') {
        blocks[data.block_id].content += data.content;

        // 根据层次分类更新
        if (data.layer === 'primary') {
          updatePrimaryContent(blocks[data.block_id].content);
        } else if (data.layer === 'process') {
          updateProcessLog(data.block_id, blocks[data.block_id].content);
        } else if (data.layer === 'debug') {
          updateDebugPanel(data.block_id, blocks[data.block_id].content);
        }
      } else if (data.type === 'block_end') {
        finalizeBlock(data.block_id, blocks[data.block_id]);
      }
    }
  }
}
```

---

## 最佳实践

### 1. 消息处理原则

- **分层展示**: 区分主要内容、过程信息和调试数据
- **渐进披露**: 默认显示最重要的信息，提供展开选项查看详情
- **友好转换**: 将技术术语转换为用户可理解的描述
- **实时反馈**: 使用流式更新提供即时反馈

### 2. 性能优化

- **增量更新**: 只更新变化的部分，避免重新渲染整个消息列表
- **虚拟滚动**: 对于长对话，使用虚拟滚动提升性能
- **状态管理**: 使用高效的状态管理（如 React Context 或 Zustand）
- **内容截断**: 对于过长的内容（如工具输出），提供折叠和截断

### 3. 错误处理

- **优雅降级**: 如果消息格式异常，显示原始消息而不是崩溃
- **错误高亮**: 对错误消息使用醒目的视觉提示
- **重试机制**: 提供重试选项，而不是让用户从头开始
- **详细日志**: 在调试模式下保留完整的原始消息

### 4. 用户体验

- **进度指示**: 显示当前执行到哪一步
- **时间估计**: 对于耗时操作，提供大致的时间估计
- **可中断性**: 允许用户中止长时间运行的操作
- **历史记录**: 保存对话历史，支持会话恢复

### 5. 多轮对话支持

- **Session ID 管理**: 保存 ResultMessage 中的 `session_id`
- **状态持久化**: 将重要状态（如已填写字段）持久化到后端
- **上下文保持**: 在多轮对话中保持上下文连贯性
- **增量更新**: 只修改用户明确要求改变的内容

---

## 总结

Claude Agent SDK 提供了丰富而灵活的消息类型系统，合理的处理和封装可以极大提升用户体验：

1. **理解消息层次**: 区分主要内容、过程信息和调试数据
2. **友好化转换**: 将技术信息转换为用户可理解的描述
3. **流式优化**: 利用增量更新提供实时反馈
4. **状态管理**: 正确处理会话 ID 和状态持久化
5. **错误处理**: 优雅处理各种错误情况

通过遵循这些最佳实践，可以构建出既强大又易用的 AI Agent 应用。
