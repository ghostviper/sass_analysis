"""
Tool decorator - 兼容 claude_agent_sdk
"""

try:
    from claude_agent_sdk import tool
    HAS_CLAUDE_SDK = True
except ImportError:
    HAS_CLAUDE_SDK = False
    # Dummy decorator if SDK not installed
    def tool(name, description, input_schema):
        def decorator(func):
            func._tool_name = name
            func._tool_description = description
            func._tool_schema = input_schema
            return func
        return decorator
