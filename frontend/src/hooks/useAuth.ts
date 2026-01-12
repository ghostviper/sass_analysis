"use client";

/**
 * 认证 Hook
 * 
 * 提供认证状态和操作方法
 */

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { 
  User, 
  signIn as apiSignIn, 
  signUp as apiSignUp, 
  signOut as apiSignOut, 
  getSession 
} from "@/lib/auth-client";

// 扩展 User 类型以包含所有字段
export interface ExtendedUser extends User {
  emailVerified?: boolean;
}

export function useAuth() {
  const router = useRouter();
  const [user, setUser] = useState<ExtendedUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 获取当前会话
  const fetchSession = useCallback(async () => {
    try {
      const session = await getSession();
      setUser(session.user as ExtendedUser);
    } catch (err) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSession();
  }, [fetchSession]);

  // 登录
  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    try {
      const result = await apiSignIn(email, password);
      setUser(result.user as ExtendedUser);
      router.push("/");
      router.refresh();
      return result;
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  }, [router]);

  // 注册
  const register = useCallback(async (email: string, password: string, name?: string) => {
    setError(null);
    try {
      const result = await apiSignUp(email, password, name);
      setUser(result.user as ExtendedUser);
      router.push("/");
      router.refresh();
      return result;
    } catch (err: any) {
      setError(err.message);
      throw err;
    }
  }, [router]);

  // 登出
  const logout = useCallback(async () => {
    await apiSignOut();
    setUser(null);
    router.push("/auth/sign-in");
    router.refresh();
  }, [router]);

  // 跳转到登录页
  const redirectToLogin = useCallback((callbackUrl?: string) => {
    const url = callbackUrl
      ? `/auth/sign-in?callbackUrl=${encodeURIComponent(callbackUrl)}`
      : "/auth/sign-in";
    router.push(url);
  }, [router]);

  // 刷新会话
  const refreshSession = useCallback(async () => {
    await fetchSession();
  }, [fetchSession]);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
    redirectToLogin,
    refreshSession,
  };
}

/**
 * 获取用户头像 URL
 */
export function useUserAvatar(email?: string | null, image?: string | null) {
  if (image) {
    return image;
  }
  if (email) {
    return `https://unavatar.io/${email}?fallback=https://ui-avatars.com/api/?name=${encodeURIComponent(email)}&background=6366f1&color=fff`;
  }
  return `https://ui-avatars.com/api/?name=U&background=6366f1&color=fff`;
}
