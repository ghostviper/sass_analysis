"""
认证路由

提供用户注册、登录、登出等功能
使用 JWT token 进行会话管理
支持 Google OAuth 登录
"""

from datetime import datetime, timedelta
from typing import Optional
import os
import secrets
import hashlib

from fastapi import APIRouter, HTTPException, Depends, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from database.db import get_db
import jwt

router = APIRouter(prefix="/auth", tags=["Auth"])

# JWT 配置
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7

# Google OAuth 配置
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/api/auth/callback/google")

security = HTTPBearer(auto_error=False)


# ============================================================================
# Pydantic Models
# ============================================================================

class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    image: Optional[str]
    plan: str
    createdAt: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse
    token: str


class SessionResponse(BaseModel):
    user: Optional[UserResponse]
    isAuthenticated: bool


# ============================================================================
# Helper Functions
# ============================================================================

def hash_password(password: str) -> str:
    """使用 SHA256 + salt 哈希密码"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    try:
        salt, hash_value = hashed.split(":")
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
    except:
        return False


def create_token(user_id: str) -> str:
    """创建 JWT token"""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """解码 JWT token，返回 user_id"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[dict]:
    """获取当前登录用户"""
    token = None
    
    # 优先从 Authorization header 获取
    if credentials:
        token = credentials.credentials
    
    # 其次从 cookie 获取
    if not token:
        token = request.cookies.get("auth_token")
    
    if not token:
        return None
    
    user_id = decode_token(token)
    if not user_id:
        return None
    
    # 查询用户
    result = await db.execute(
        text('SELECT * FROM "user" WHERE id = :id'),
        {"id": user_id}
    )
    row = result.fetchone()
    
    if not row:
        return None
    
    return dict(row._mapping)


# ============================================================================
# Routes
# ============================================================================

@router.post("/sign-up", response_model=AuthResponse)
async def sign_up(data: SignUpRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查邮箱是否已存在
    result = await db.execute(
        text('SELECT id FROM "user" WHERE email = :email'),
        {"email": data.email}
    )
    if result.fetchone():
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 创建用户
    user_id = secrets.token_urlsafe(16)
    hashed_password = hash_password(data.password)
    name = data.name or data.email.split("@")[0]
    now = datetime.utcnow()
    
    await db.execute(
        text('''
            INSERT INTO "user" (id, email, name, "createdAt", "updatedAt", plan)
            VALUES (:id, :email, :name, :created_at, :updated_at, 'free')
        '''),
        {
            "id": user_id,
            "email": data.email,
            "name": name,
            "created_at": now,
            "updated_at": now,
        }
    )
    
    # 存储密码到 account 表
    account_id = secrets.token_urlsafe(16)
    await db.execute(
        text('''
            INSERT INTO account (id, "userId", "accountId", "providerId", password, "createdAt", "updatedAt")
            VALUES (:id, :user_id, :account_id, 'credential', :password, :created_at, :updated_at)
        '''),
        {
            "id": account_id,
            "user_id": user_id,
            "account_id": data.email,
            "password": hashed_password,
            "created_at": now,
            "updated_at": now,
        }
    )
    
    await db.commit()
    
    # 创建 token
    token = create_token(user_id)
    
    # 设置 cookie
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=False,  # 开发环境设为 False
        samesite="lax",
        max_age=JWT_EXPIRE_DAYS * 24 * 60 * 60,
    )
    
    return AuthResponse(
        user=UserResponse(
            id=user_id,
            email=data.email,
            name=name,
            image=None,
            plan="free",
            createdAt=now,
        ),
        token=token,
    )


@router.post("/sign-in", response_model=AuthResponse)
async def sign_in(data: SignInRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    # 查询用户
    result = await db.execute(
        text('SELECT * FROM "user" WHERE email = :email'),
        {"email": data.email}
    )
    user = result.fetchone()
    
    if not user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    
    user_dict = dict(user._mapping)
    
    # 查询密码
    result = await db.execute(
        text('SELECT password FROM account WHERE "userId" = :user_id AND "providerId" = \'credential\''),
        {"user_id": user_dict["id"]}
    )
    account = result.fetchone()
    
    if not account or not verify_password(data.password, account.password):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    
    # 创建 token
    token = create_token(user_dict["id"])
    
    # 设置 cookie
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=JWT_EXPIRE_DAYS * 24 * 60 * 60,
    )
    
    return AuthResponse(
        user=UserResponse(
            id=user_dict["id"],
            email=user_dict["email"],
            name=user_dict.get("name"),
            image=user_dict.get("image"),
            plan=user_dict.get("plan", "free"),
            createdAt=user_dict.get("createdAt", datetime.utcnow()),
        ),
        token=token,
    )


@router.post("/sign-out")
async def sign_out(response: Response):
    """用户登出"""
    response.delete_cookie("auth_token")
    return {"success": True}


@router.get("/session", response_model=SessionResponse)
async def get_session(user: Optional[dict] = Depends(get_current_user)):
    """获取当前会话"""
    if not user:
        return SessionResponse(user=None, isAuthenticated=False)
    
    return SessionResponse(
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user.get("name"),
            image=user.get("image"),
            plan=user.get("plan", "free"),
            createdAt=user.get("createdAt", datetime.utcnow()),
        ),
        isAuthenticated=True,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: Optional[dict] = Depends(get_current_user)):
    """获取当前用户信息"""
    if not user:
        raise HTTPException(status_code=401, detail="未登录")
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user.get("name"),
        image=user.get("image"),
        plan=user.get("plan", "free"),
        createdAt=user.get("createdAt", datetime.utcnow()),
    )


# ============================================================================
# Google OAuth
# ============================================================================

@router.get("/google")
async def google_login(request: Request):
    """发起 Google OAuth 登录"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth 未配置")
    
    # 获取 callbackUrl 参数
    callback_url = request.query_params.get("callbackUrl", "/")
    
    # 生成 state 参数（包含 callbackUrl）
    state = secrets.token_urlsafe(32) + "|" + callback_url
    
    # 构建 Google OAuth URL
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    
    return RedirectResponse(url=google_auth_url)


@router.get("/callback/google")
async def google_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Google OAuth 回调"""
    if error:
        return RedirectResponse(url=f"/auth/sign-in?error={error}")
    
    if not code:
        return RedirectResponse(url="/auth/sign-in?error=no_code")
    
    # 解析 state 获取 callbackUrl
    callback_url = "/"
    if state and "|" in state:
        _, callback_url = state.split("|", 1)
    
    try:
        # 用 code 换取 access_token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                },
            )
            
            if token_response.status_code != 200:
                return RedirectResponse(url="/auth/sign-in?error=token_exchange_failed")
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # 获取用户信息
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            
            if userinfo_response.status_code != 200:
                return RedirectResponse(url="/auth/sign-in?error=userinfo_failed")
            
            google_user = userinfo_response.json()
    
    except Exception as e:
        print(f"[Auth] Google OAuth error: {e}")
        return RedirectResponse(url="/auth/sign-in?error=oauth_failed")
    
    email = google_user.get("email")
    name = google_user.get("name")
    picture = google_user.get("picture")
    google_id = google_user.get("id")
    
    if not email:
        return RedirectResponse(url="/auth/sign-in?error=no_email")
    
    now = datetime.utcnow()
    
    # 检查用户是否已存在
    result = await db.execute(
        text('SELECT * FROM "user" WHERE email = :email'),
        {"email": email}
    )
    user = result.fetchone()
    
    if user:
        # 用户已存在，更新信息
        user_dict = dict(user._mapping)
        user_id = user_dict["id"]
        
        # 更新用户头像和名称（如果之前没有）
        await db.execute(
            text('''
                UPDATE "user" 
                SET image = COALESCE(image, :image), 
                    name = COALESCE(name, :name),
                    "updatedAt" = :updated_at
                WHERE id = :id
            '''),
            {"id": user_id, "image": picture, "name": name, "updated_at": now}
        )
    else:
        # 创建新用户
        user_id = secrets.token_urlsafe(16)
        
        await db.execute(
            text('''
                INSERT INTO "user" (id, email, name, image, "emailVerified", "createdAt", "updatedAt", plan)
                VALUES (:id, :email, :name, :image, true, :created_at, :updated_at, 'free')
            '''),
            {
                "id": user_id,
                "email": email,
                "name": name,
                "image": picture,
                "created_at": now,
                "updated_at": now,
            }
        )
    
    # 检查是否已有 Google account 记录
    result = await db.execute(
        text('SELECT id FROM account WHERE "userId" = :user_id AND "providerId" = \'google\''),
        {"user_id": user_id}
    )
    existing_account = result.fetchone()
    
    if not existing_account:
        # 创建 account 记录
        account_id = secrets.token_urlsafe(16)
        await db.execute(
            text('''
                INSERT INTO account (id, "userId", "accountId", "providerId", "accessToken", "createdAt", "updatedAt")
                VALUES (:id, :user_id, :account_id, 'google', :access_token, :created_at, :updated_at)
            '''),
            {
                "id": account_id,
                "user_id": user_id,
                "account_id": google_id,
                "access_token": access_token,
                "created_at": now,
                "updated_at": now,
            }
        )
    
    await db.commit()
    
    # 创建 JWT token
    token = create_token(user_id)
    
    # 创建响应并设置 cookie
    response = RedirectResponse(url=callback_url, status_code=302)
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=False,  # 开发环境
        samesite="lax",
        max_age=JWT_EXPIRE_DAYS * 24 * 60 * 60,
    )
    
    return response


# ============================================================================
# Email Verification & Password Reset
# ============================================================================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


class VerifyEmailRequest(BaseModel):
    token: str


class SendVerificationRequest(BaseModel):
    email: EmailStr


def generate_verification_token() -> str:
    """生成验证令牌"""
    return secrets.token_urlsafe(32)


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    忘记密码 - 发送密码重置邮件
    
    无论邮箱是否存在，都返回成功（防止邮箱枚举攻击）
    """
    from services.email import email_service
    
    # 查询用户
    result = await db.execute(
        text('SELECT id, email FROM "user" WHERE email = :email'),
        {"email": data.email}
    )
    user = result.fetchone()
    
    if user:
        # 生成重置令牌
        token = generate_verification_token()
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=1)  # 1小时有效期
        
        # 删除旧的重置令牌
        await db.execute(
            text('DELETE FROM verification WHERE identifier = :email AND value LIKE \'reset:%\''),
            {"email": data.email}
        )
        
        # 创建新的重置令牌
        verification_id = secrets.token_urlsafe(16)
        await db.execute(
            text('''
                INSERT INTO verification (id, identifier, value, "expiresAt", "createdAt", "updatedAt")
                VALUES (:id, :identifier, :value, :expires_at, :created_at, :updated_at)
            '''),
            {
                "id": verification_id,
                "identifier": data.email,
                "value": f"reset:{token}",
                "expires_at": expires_at,
                "created_at": now,
                "updated_at": now,
            }
        )
        await db.commit()
        
        # 发送邮件
        await email_service.send_password_reset_email(data.email, token)
    
    # 无论是否找到用户，都返回成功
    return {"success": True, "message": "如果该邮箱已注册，您将收到密码重置邮件"}


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    重置密码
    
    使用邮件中的令牌重置密码
    """
    # 查找有效的重置令牌
    result = await db.execute(
        text('''
            SELECT identifier, "expiresAt" FROM verification 
            WHERE value = :value AND "expiresAt" > :now
        '''),
        {"value": f"reset:{data.token}", "now": datetime.utcnow()}
    )
    verification = result.fetchone()
    
    if not verification:
        raise HTTPException(status_code=400, detail="无效或已过期的重置链接")
    
    email = verification.identifier
    
    # 查找用户
    result = await db.execute(
        text('SELECT id FROM "user" WHERE email = :email'),
        {"email": email}
    )
    user = result.fetchone()
    
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    
    user_id = user.id
    now = datetime.utcnow()
    
    # 更新密码
    hashed_password = hash_password(data.password)
    
    # 检查是否有 credential 账户
    result = await db.execute(
        text('SELECT id FROM account WHERE "userId" = :user_id AND "providerId" = \'credential\''),
        {"user_id": user_id}
    )
    existing_account = result.fetchone()
    
    if existing_account:
        # 更新密码
        await db.execute(
            text('''
                UPDATE account SET password = :password, "updatedAt" = :now
                WHERE "userId" = :user_id AND "providerId" = 'credential'
            '''),
            {"password": hashed_password, "user_id": user_id, "now": now}
        )
    else:
        # 创建 credential 账户
        account_id = secrets.token_urlsafe(16)
        await db.execute(
            text('''
                INSERT INTO account (id, "userId", "accountId", "providerId", password, "createdAt", "updatedAt")
                VALUES (:id, :user_id, :account_id, 'credential', :password, :created_at, :updated_at)
            '''),
            {
                "id": account_id,
                "user_id": user_id,
                "account_id": email,
                "password": hashed_password,
                "created_at": now,
                "updated_at": now,
            }
        )
    
    # 删除使用过的令牌
    await db.execute(
        text('DELETE FROM verification WHERE value = :value'),
        {"value": f"reset:{data.token}"}
    )
    
    await db.commit()
    
    return {"success": True, "message": "密码已重置，请使用新密码登录"}


@router.post("/send-verification")
async def send_verification_email(
    data: SendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    发送邮箱验证邮件
    """
    from services.email import email_service
    
    # 查询用户
    result = await db.execute(
        text('SELECT id, "emailVerified" FROM "user" WHERE email = :email'),
        {"email": data.email}
    )
    user = result.fetchone()
    
    if not user:
        # 不透露用户是否存在
        return {"success": True, "message": "如果该邮箱已注册，您将收到验证邮件"}
    
    if user.emailVerified:
        return {"success": True, "message": "邮箱已验证"}
    
    # 生成验证令牌
    token = generate_verification_token()
    now = datetime.utcnow()
    expires_at = now + timedelta(hours=24)  # 24小时有效期
    
    # 删除旧的验证令牌
    await db.execute(
        text('DELETE FROM verification WHERE identifier = :email AND value LIKE \'verify:%\''),
        {"email": data.email}
    )
    
    # 创建新的验证令牌
    verification_id = secrets.token_urlsafe(16)
    await db.execute(
        text('''
            INSERT INTO verification (id, identifier, value, "expiresAt", "createdAt", "updatedAt")
            VALUES (:id, :identifier, :value, :expires_at, :created_at, :updated_at)
        '''),
        {
            "id": verification_id,
            "identifier": data.email,
            "value": f"verify:{token}",
            "expires_at": expires_at,
            "created_at": now,
            "updated_at": now,
        }
    )
    await db.commit()
    
    # 发送邮件
    await email_service.send_verification_email(data.email, token)
    
    return {"success": True, "message": "验证邮件已发送"}


@router.post("/verify-email")
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    验证邮箱
    
    使用邮件中的令牌验证邮箱
    """
    # 查找有效的验证令牌
    result = await db.execute(
        text('''
            SELECT identifier, "expiresAt" FROM verification 
            WHERE value = :value AND "expiresAt" > :now
        '''),
        {"value": f"verify:{data.token}", "now": datetime.utcnow()}
    )
    verification = result.fetchone()
    
    if not verification:
        raise HTTPException(status_code=400, detail="无效或已过期的验证链接")
    
    email = verification.identifier
    now = datetime.utcnow()
    
    # 更新用户邮箱验证状态
    await db.execute(
        text('''
            UPDATE "user" SET "emailVerified" = true, "updatedAt" = :now
            WHERE email = :email
        '''),
        {"email": email, "now": now}
    )
    
    # 删除使用过的令牌
    await db.execute(
        text('DELETE FROM verification WHERE value = :value'),
        {"value": f"verify:{data.token}"}
    )
    
    await db.commit()
    
    return {"success": True, "message": "邮箱验证成功"}
