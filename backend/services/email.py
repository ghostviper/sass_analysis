"""
邮件服务

使用 Resend API 发送邮件
支持邮箱验证、密码重置等功能
"""

import os
from typing import Optional
import httpx

# Resend API 配置
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@buildwhat.app")
APP_NAME = os.getenv("APP_NAME", "BuildWhat")
APP_URL = os.getenv("APP_URL", "http://localhost:3000")


class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.api_key = RESEND_API_KEY
        self.from_email = EMAIL_FROM
        self.app_name = APP_NAME
        self.app_url = APP_URL
    
    @property
    def is_configured(self) -> bool:
        """检查邮件服务是否已配置"""
        return bool(self.api_key)
    
    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        text: Optional[str] = None
    ) -> dict:
        """
        发送邮件
        
        Args:
            to: 收件人邮箱
            subject: 邮件主题
            html: HTML 内容
            text: 纯文本内容（可选）
            
        Returns:
            {"success": True, "id": "email_id"} 或 {"success": False, "error": "..."}
        """
        if not self.is_configured:
            print(f"[Email] Service not configured, would send to {to}: {subject}")
            return {"success": False, "error": "Email service not configured"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": f"{self.app_name} <{self.from_email}>",
                        "to": [to],
                        "subject": subject,
                        "html": html,
                        "text": text or ""
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"[Email] Sent to {to}: {subject}")
                    return {"success": True, "id": data.get("id")}
                else:
                    error = response.text
                    print(f"[Email] Failed to send to {to}: {error}")
                    return {"success": False, "error": error}
                    
        except Exception as e:
            print(f"[Email] Error sending to {to}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_verification_email(self, to: str, token: str) -> dict:
        """
        发送邮箱验证邮件
        
        Args:
            to: 收件人邮箱
            token: 验证令牌
        """
        verify_url = f"{self.app_url}/auth/verify-email?token={token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #6366f1; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #6366f1; color: white; text-decoration: none; border-radius: 8px; font-weight: 500; }}
                .button:hover {{ background: #4f46e5; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{self.app_name}</div>
                </div>
                
                <h2>验证您的邮箱</h2>
                <p>感谢您注册 {self.app_name}！请点击下方按钮验证您的邮箱地址：</p>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{verify_url}" class="button">验证邮箱</a>
                </p>
                
                <p>或者复制以下链接到浏览器：</p>
                <p style="word-break: break-all; color: #666;">{verify_url}</p>
                
                <p>此链接将在 24 小时后失效。</p>
                
                <div class="footer">
                    <p>如果您没有注册 {self.app_name}，请忽略此邮件。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject=f"验证您的 {self.app_name} 邮箱",
            html=html,
            text=f"请访问以下链接验证您的邮箱：{verify_url}"
        )
    
    async def send_password_reset_email(self, to: str, token: str) -> dict:
        """
        发送密码重置邮件
        
        Args:
            to: 收件人邮箱
            token: 重置令牌
        """
        reset_url = f"{self.app_url}/auth/reset-password?token={token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 24px; font-weight: bold; color: #6366f1; }}
                .button {{ display: inline-block; padding: 12px 24px; background: #6366f1; color: white; text-decoration: none; border-radius: 8px; font-weight: 500; }}
                .button:hover {{ background: #4f46e5; }}
                .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 14px; }}
                .warning {{ background: #fef3c7; border: 1px solid #f59e0b; padding: 12px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">{self.app_name}</div>
                </div>
                
                <h2>重置您的密码</h2>
                <p>我们收到了重置您 {self.app_name} 账户密码的请求。点击下方按钮设置新密码：</p>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" class="button">重置密码</a>
                </p>
                
                <p>或者复制以下链接到浏览器：</p>
                <p style="word-break: break-all; color: #666;">{reset_url}</p>
                
                <div class="warning">
                    <strong>⚠️ 安全提示：</strong>此链接将在 1 小时后失效。如果您没有请求重置密码，请忽略此邮件，您的账户是安全的。
                </div>
                
                <div class="footer">
                    <p>如有任何问题，请联系我们的支持团队。</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject=f"重置您的 {self.app_name} 密码",
            html=html,
            text=f"请访问以下链接重置您的密码：{reset_url}"
        )


# 全局邮件服务实例
email_service = EmailService()
