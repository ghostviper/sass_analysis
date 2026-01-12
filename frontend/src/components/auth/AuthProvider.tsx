"use client";

/**
 * 认证 Provider 组件
 * 
 * 简单的认证状态管理，不使用 better-auth-ui
 */

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  // 目前只是一个简单的包装器
  // 认证状态通过 useAuth hook 管理
  return <>{children}</>;
}
