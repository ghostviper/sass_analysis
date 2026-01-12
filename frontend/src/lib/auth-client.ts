"use client";

/**
 * Auth Client
 * 
 * 调用后端 Python API 进行认证
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

// ============================================================================
// Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  name: string | null;
  image: string | null;
  plan: string;
  createdAt: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface SessionResponse {
  user: User | null;
  isAuthenticated: boolean;
}

// ============================================================================
// API Functions
// ============================================================================

export async function signUp(email: string, password: string, name?: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/sign-up`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password, name }),
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "注册失败");
  }
  
  return res.json();
}

export async function signIn(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/api/auth/sign-in`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "登录失败");
  }
  
  return res.json();
}

export async function signOut(): Promise<void> {
  await fetch(`${API_BASE}/api/auth/sign-out`, {
    method: "POST",
    credentials: "include",
  });
}

export async function getSession(): Promise<SessionResponse> {
  const res = await fetch(`${API_BASE}/api/auth/session`, {
    credentials: "include",
  });
  
  if (!res.ok) {
    return { user: null, isAuthenticated: false };
  }
  
  return res.json();
}

export async function getMe(): Promise<User | null> {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    credentials: "include",
  });
  
  if (!res.ok) {
    return null;
  }
  
  return res.json();
}

export function signInWithGoogle(callbackUrl: string = "/"): void {
  // 直接跳转到后端 Google OAuth 入口
  window.location.href = `${API_BASE}/api/auth/google?callbackUrl=${encodeURIComponent(callbackUrl)}`;
}

// ============================================================================
// Password Reset & Email Verification
// ============================================================================

export async function forgotPassword(email: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/api/auth/forgot-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "发送失败");
  }
  
  return res.json();
}

export async function resetPassword(token: string, password: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, password }),
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "重置失败");
  }
  
  return res.json();
}

export async function sendVerificationEmail(email: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/api/auth/send-verification`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "发送失败");
  }
  
  return res.json();
}

export async function verifyEmail(token: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/api/auth/verify-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });
  
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "验证失败");
  }
  
  return res.json();
}
