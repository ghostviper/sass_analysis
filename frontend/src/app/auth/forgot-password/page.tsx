"use client";

/**
 * 忘记密码页面
 */

import { useState } from "react";
import Link from "next/link";
import { Mail, Loader2, ArrowLeft, CheckCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { forgotPassword } from "@/lib/auth-client";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await forgotPassword(email);
      setIsSuccess(true);
    } catch (err: any) {
      // 即使失败也显示成功（安全考虑，不暴露邮箱是否存在）
      setIsSuccess(true);
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto w-16 h-16 rounded-full bg-accent-success/10 flex items-center justify-center">
          <CheckCircle className="h-8 w-8 text-accent-success" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
            邮件已发送
          </h1>
          <p className="text-sm text-content-tertiary mt-2">
            我们已向 <span className="font-medium text-content-secondary">{email}</span> 发送了密码重置链接，请查收邮件。
          </p>
        </div>
        <div className="space-y-3">
          <button
            onClick={() => {
              setIsSuccess(false);
              setEmail("");
            }}
            className="w-full btn btn-secondary"
          >
            使用其他邮箱
          </button>
          <Link href="/auth/sign-in" className="block w-full btn btn-ghost">
            返回登录
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 返回链接 */}
      <Link
        href="/auth/sign-in"
        className="inline-flex items-center gap-2 text-sm text-content-tertiary hover:text-content-secondary transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        返回登录
      </Link>

      {/* 标题 */}
      <div className="text-center lg:text-left">
        <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
          忘记密码
        </h1>
        <p className="text-sm text-content-tertiary mt-2">
          输入您的邮箱，我们将发送密码重置链接
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
        <div>
          <label className="block text-sm font-medium text-content-secondary mb-1.5">
            邮箱
          </label>
          <div className="relative">
            <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              className="input pl-10"
              disabled={isLoading}
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !email}
          className={cn(
            "w-full btn btn-primary py-3",
            (isLoading || !email) && "opacity-50 cursor-not-allowed"
          )}
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              发送中...
            </>
          ) : (
            "发送重置链接"
          )}
        </button>
      </form>
    </div>
  );
}
