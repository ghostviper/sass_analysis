"""
Chat History Service - 会话历史存储服务

提供会话和消息的持久化存储功能。
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import AsyncSessionLocal
from database.models import ChatSession, ChatMessage


class ChatHistoryService:
    """会话历史存储服务"""

    @staticmethod
    async def create_session(
        session_id: str,
        title: Optional[str] = None,
        user_id: Optional[str] = None,
        enable_web_search: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """
        创建新会话

        Args:
            session_id: 会话ID
            title: 会话标题
            user_id: 用户ID（可选）
            enable_web_search: 是否启用联网搜索
            context: 上下文信息

        Returns:
            创建的会话对象
        """
        async with AsyncSessionLocal() as db:
            session = ChatSession(
                session_id=session_id,
                title=title,
                user_id=user_id,
                enable_web_search=enable_web_search,
                context_type=context.get("type") if context else None,
                context_value=context.get("value") if context else None,
                context_products=context.get("products") if context else None,
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            return session

    @staticmethod
    async def get_session(session_id: str) -> Optional[ChatSession]:
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            会话对象或None
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.session_id == session_id,
                    ChatSession.is_deleted == False
                )
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def get_session_dict(session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息（字典格式）"""
        session = await ChatHistoryService.get_session(session_id)
        return session.to_dict() if session else None

    @staticmethod
    async def update_session(
        session_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        is_archived: Optional[bool] = None,
        **kwargs
    ) -> bool:
        """
        更新会话信息

        Args:
            session_id: 会话ID
            title: 新标题
            summary: 新摘要
            is_archived: 是否归档
            **kwargs: 其他更新字段

        Returns:
            是否更新成功
        """
        async with AsyncSessionLocal() as db:
            update_data = {"updated_at": datetime.utcnow()}

            if title is not None:
                update_data["title"] = title
            if summary is not None:
                update_data["summary"] = summary
            if is_archived is not None:
                update_data["is_archived"] = is_archived

            # 添加其他字段
            for key, value in kwargs.items():
                if value is not None:
                    update_data[key] = value

            result = await db.execute(
                update(ChatSession)
                .where(ChatSession.session_id == session_id)
                .values(**update_data)
            )
            await db.commit()
            return result.rowcount > 0

    @staticmethod
    async def delete_session(session_id: str, hard_delete: bool = False) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID
            hard_delete: 是否硬删除（默认软删除）

        Returns:
            是否删除成功
        """
        async with AsyncSessionLocal() as db:
            if hard_delete:
                # 先删除消息
                await db.execute(
                    delete(ChatMessage).where(ChatMessage.session_id == session_id)
                )
                # 再删除会话
                result = await db.execute(
                    delete(ChatSession).where(ChatSession.session_id == session_id)
                )
            else:
                # 软删除
                result = await db.execute(
                    update(ChatSession)
                    .where(ChatSession.session_id == session_id)
                    .values(is_deleted=True, updated_at=datetime.utcnow())
                )
            await db.commit()
            return result.rowcount > 0

    @staticmethod
    async def list_sessions(
        user_id: Optional[str] = None,
        include_archived: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取会话列表

        Args:
            user_id: 用户ID（可选，用于过滤）
            include_archived: 是否包含已归档会话
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            会话列表
        """
        async with AsyncSessionLocal() as db:
            query = select(ChatSession).where(ChatSession.is_deleted == False)

            if user_id:
                query = query.where(ChatSession.user_id == user_id)

            if not include_archived:
                query = query.where(ChatSession.is_archived == False)

            query = query.order_by(desc(ChatSession.updated_at)).limit(limit).offset(offset)

            result = await db.execute(query)
            sessions = result.scalars().all()

            return [s.to_list_dict() for s in sessions]

    @staticmethod
    async def add_message(
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cost: Optional[float] = None,
        model: Optional[str] = None,
        duration_ms: Optional[int] = None,
        checkpoint_id: Optional[str] = None  # 新增：checkpoint ID
    ) -> ChatMessage:
        """
        添加消息到会话

        Args:
            session_id: 会话ID
            role: 角色 (user/assistant/system)
            content: 消息内容
            tool_calls: 工具调用记录
            input_tokens: 输入token数
            output_tokens: 输出token数
            cost: 消耗费用
            model: 使用的模型
            duration_ms: 响应耗时
            checkpoint_id: Claude Agent SDK checkpoint ID (用于多轮对话恢复)

        Returns:
            创建的消息对象
        """
        async with AsyncSessionLocal() as db:
            # 获取当前最大序号
            result = await db.execute(
                select(func.max(ChatMessage.sequence))
                .where(ChatMessage.session_id == session_id)
            )
            max_seq = result.scalar() or 0

            # 创建消息
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                sequence=max_seq + 1,
                tool_calls=tool_calls,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                model=model,
                duration_ms=duration_ms,
                checkpoint_id=checkpoint_id,  # 保存 checkpoint ID
            )
            db.add(message)

            # 更新会话统计
            update_data = {
                "updated_at": datetime.utcnow(),
                "last_message_at": datetime.utcnow(),
                "message_count": ChatSession.message_count + 1,
            }

            # 如果是用户消息，增加轮数
            if role == "user":
                update_data["turn_count"] = ChatSession.turn_count + 1

            # 如果有token统计，累加
            if input_tokens:
                update_data["total_input_tokens"] = ChatSession.total_input_tokens + input_tokens
            if output_tokens:
                update_data["total_output_tokens"] = ChatSession.total_output_tokens + output_tokens
            if cost:
                update_data["total_cost"] = ChatSession.total_cost + cost

            await db.execute(
                update(ChatSession)
                .where(ChatSession.session_id == session_id)
                .values(**update_data)
            )

            await db.commit()
            await db.refresh(message)
            return message

    @staticmethod
    async def get_last_checkpoint_id(session_id: str) -> Optional[str]:
        """
        获取会话的最后一个 checkpoint ID
        
        Args:
            session_id: 会话ID
            
        Returns:
            最后一个 checkpoint ID 或 None
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ChatMessage.checkpoint_id)
                .where(ChatMessage.session_id == session_id)
                .where(ChatMessage.checkpoint_id.isnot(None))
                .order_by(desc(ChatMessage.sequence))
                .limit(1)
            )
            checkpoint_id = result.scalar_one_or_none()
            return checkpoint_id

    @staticmethod
    async def get_messages(
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取会话的所有消息

        Args:
            session_id: 会话ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            消息列表
        """
        async with AsyncSessionLocal() as db:
            query = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.sequence)
            )

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = await db.execute(query)
            messages = result.scalars().all()

            return [m.to_dict() for m in messages]

    @staticmethod
    async def get_recent_messages(
        session_id: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取最近的N条消息

        Args:
            session_id: 会话ID
            count: 消息数量

        Returns:
            消息列表（按时间正序）
        """
        async with AsyncSessionLocal() as db:
            # 先获取最新的N条（倒序）
            subquery = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(desc(ChatMessage.sequence))
                .limit(count)
            ).subquery()

            # 再按正序返回
            result = await db.execute(
                select(ChatMessage)
                .where(ChatMessage.id.in_(select(subquery.c.id)))
                .order_by(ChatMessage.sequence)
            )
            messages = result.scalars().all()

            return [m.to_dict() for m in messages]

    @staticmethod
    async def generate_title_from_message(content: str, max_length: int = 50) -> str:
        """
        从消息内容生成会话标题

        Args:
            content: 消息内容
            max_length: 最大长度

        Returns:
            生成的标题
        """
        # 移除换行符，取第一行
        title = content.replace("\n", " ").strip()

        # 截断
        if len(title) > max_length:
            title = title[:max_length - 3] + "..."

        return title or "新对话"

    @staticmethod
    async def ensure_session_exists(
        session_id: str,
        user_id: Optional[str] = None,
        enable_web_search: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """
        确保会话存在，不存在则创建

        Args:
            session_id: 会话ID
            user_id: 用户ID
            enable_web_search: 是否启用联网搜索
            context: 上下文信息

        Returns:
            会话对象
        """
        session = await ChatHistoryService.get_session(session_id)
        if not session:
            session = await ChatHistoryService.create_session(
                session_id=session_id,
                user_id=user_id,
                enable_web_search=enable_web_search,
                context=context
            )
        return session

    @staticmethod
    async def get_session_stats() -> Dict[str, Any]:
        """
        获取会话统计信息

        Returns:
            统计信息字典
        """
        async with AsyncSessionLocal() as db:
            # 总会话数
            total_result = await db.execute(
                select(func.count(ChatSession.id))
                .where(ChatSession.is_deleted == False)
            )
            total_sessions = total_result.scalar() or 0

            # 总消息数
            msg_result = await db.execute(select(func.count(ChatMessage.id)))
            total_messages = msg_result.scalar() or 0

            # 总消耗
            cost_result = await db.execute(
                select(func.sum(ChatSession.total_cost))
                .where(ChatSession.is_deleted == False)
            )
            total_cost = cost_result.scalar() or 0.0

            return {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "total_cost": round(total_cost, 4),
            }
