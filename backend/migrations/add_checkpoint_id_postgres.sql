-- 添加 checkpoint_id 字段到 chat_messages 表
-- 用于支持 Claude Agent SDK 的多轮对话恢复功能

-- 检查字段是否已存在
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'chat_messages' 
        AND column_name = 'checkpoint_id'
    ) THEN
        -- 添加字段
        ALTER TABLE chat_messages ADD COLUMN checkpoint_id VARCHAR(64);
        RAISE NOTICE '✓ checkpoint_id 字段已添加';
        
        -- 添加索引
        CREATE INDEX ix_chat_messages_checkpoint_id ON chat_messages(checkpoint_id);
        RAISE NOTICE '✓ 索引已创建';
    ELSE
        RAISE NOTICE '✓ checkpoint_id 字段已存在，跳过';
    END IF;
END $$;

-- 验证
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'chat_messages' 
AND column_name = 'checkpoint_id';
