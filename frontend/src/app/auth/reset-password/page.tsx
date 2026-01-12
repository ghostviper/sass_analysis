"use client";

/**
 * 重置密码页面
 */

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Lock, Loader2, CheckCircle, XCircle, Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";
import { resetPassword } from "@/lib/auth-client";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  // 检查 token 是否存在
  useEffect(() => {
    if (!token) {
      setError("无效的重置链接");
    }
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // 验证密码
    if (password.length < 6) {
      setError("密码至少需要 6 个字符");
      return;
    }

    if (password !== confirmPassword) {
      setError("两次输入的密码不一致");
      return;
    }

    if (!token) {
      setError("无效的重置链接");
      return;
    }

    setIsLoading(true);

    try {
      await resetPassword(token, password);
      setIsSuccess(true);
    } catch (err: any) {
      setError(err.message || "重置失败，请稍后重试");
    } finally {
      setIsLoading(false);
    }
  };

  // 成功状态
  if (isSuccess) {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto w-16 h-16 rounded-full bg-accent-success/10 flex items-center justify-center">
          <CheckCircle className="h-8 w-8 text-accent-success" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
            密码已重置
          </h1>
          <p className="text-sm text-content-tertiary mt-2">
            您的密码已成功重置，请使用新密码登录
          </p>
        </div>
        <Link href="/auth/sign-in" className="block w-full btn btn-primary py-3">
          前往登录
        </Link>
      </div>
    );
  }

  // 无效 token 状态
  if (!token) {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto w-16 h-16 rounded-full bg-accent-error/10 flex items-center justify-center">
          <XCircle className="h-8 w-8 text-accent-error" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
            链接无效
          </h1>
          <p className="text-sm text-content-tertiary mt-2">
            重置链接无效或已过期，请重新申请
          </p>
        </div>
        <Link href="/auth/forgot-password" className="block w-full btn btn-primary py-3">
          重新申请
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div className="text-center lg:text-left">
        <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
          设置新密码
        </h1>
        <p className="text-sm text-content-tertiary mt-2">
          请输入您的新密码
        </p>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="p-3 rounded-xl bg-accent-error/10 border border-accent-error/20 text-sm text-accent-error">
          {error}
        </div>
      )}

      {/* 表单 */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 新密码 */}
        <div>
          <label className="block text-sm font-medium text-content-secondary mb-1.5">
            新密码
          </label>
          <div className="relative">
            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="至少 6 个字符"
              required
              minLength={6}
              className="input pl-10 pr-10"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-content-muted hover:text-content-secondary transition-colors"
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>

        {/* 确认密码 */}
        <div>
          <label className="block text-sm font-medium text-content-secondary mb-1.5">
            确认密码
          </label>
          <div className="relative">
            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
            <input
              type={showPassword ? "text" : "password"}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="再次输入密码"
              required
              className="input pl-10"
              disabled={isLoading}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !password || !confirmPassword}
          className={cn(
            "w-full btn btn-primary py-3",
            (isLoading || !password || !confirmPassword) && "opacity-50 cursor-not-allowed"
          )}
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              重置中...
            </>
          ) : (
            "重置密码"
          )}
        </button>
      </form>

      {/* 返回登录 */}
      <p className="text-center text-sm text-content-tertiary">
        <Link
          href="/auth/sign-in"
          className="text-brand-500 hover:text-brand-600 font-medium transition-colors"
        >
          返回登录
        </Link>
      </p>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  );
}
