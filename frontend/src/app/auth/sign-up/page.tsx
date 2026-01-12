"use client";

/**
 * 注册页面
 */

import { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signUp } from "@/lib/auth-client";
import { Eye, EyeOff, Mail, Lock, User, Check } from "lucide-react";
import { cn } from "@/lib/utils";

function SignUpForm() {
  const router = useRouter();
  
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  // 密码强度检查
  const passwordChecks = {
    length: password.length >= 8,
    hasNumber: /\d/.test(password),
    hasLetter: /[a-zA-Z]/.test(password),
  };
  const isPasswordValid = Object.values(passwordChecks).every(Boolean);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!isPasswordValid) {
      setError("请确保密码符合要求");
      return;
    }

    setIsLoading(true);

    try {
      await signUp(email, password, name || undefined);
      router.push("/");
      router.refresh();
    } catch (err: any) {
      setError(err.message || "注册失败，请稍后重试");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 标题 */}
      <div className="text-center lg:text-left">
        <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
          创建账户
        </h1>
        <p className="text-sm text-content-tertiary mt-2">
          注册以开始使用 BuildWhat
        </p>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="p-3 rounded-xl bg-accent-error/10 border border-accent-error/20 text-sm text-accent-error">
          {error}
        </div>
      )}

      {/* 注册表单 */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* 昵称 */}
        <div>
          <label className="block text-sm font-medium text-content-secondary mb-1.5">
            昵称 <span className="text-content-muted font-normal">(可选)</span>
          </label>
          <div className="relative">
            <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="您的昵称"
              className="input pl-10"
              disabled={isLoading}
            />
          </div>
        </div>

        {/* 邮箱 */}
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

        {/* 密码 */}
        <div>
          <label className="block text-sm font-medium text-content-secondary mb-1.5">
            密码
          </label>
          <div className="relative">
            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
            <input
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="创建密码"
              required
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
          
          {/* 密码强度提示 */}
          {password && (
            <div className="mt-2 space-y-1">
              {[
                { key: "length", label: "至少 8 个字符" },
                { key: "hasLetter", label: "包含字母" },
                { key: "hasNumber", label: "包含数字" },
              ].map((check) => (
                <div
                  key={check.key}
                  className={cn(
                    "flex items-center gap-2 text-xs transition-colors",
                    passwordChecks[check.key as keyof typeof passwordChecks]
                      ? "text-accent-success"
                      : "text-content-muted"
                  )}
                >
                  <Check className="h-3 w-3" />
                  <span>{check.label}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 注册按钮 */}
        <button
          type="submit"
          disabled={isLoading || !email || !password || !isPasswordValid}
          className={cn(
            "w-full btn btn-primary py-3",
            (isLoading || !email || !password || !isPasswordValid) && "opacity-50 cursor-not-allowed"
          )}
        >
          {isLoading ? (
            <>
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              注册中...
            </>
          ) : (
            "创建账户"
          )}
        </button>
      </form>

      {/* 服务条款 */}
      <p className="text-center text-xs text-content-muted leading-relaxed">
        注册即表示您同意我们的{" "}
        <Link href="/terms" className="text-brand-500 hover:underline">
          服务条款
        </Link>{" "}
        和{" "}
        <Link href="/privacy" className="text-brand-500 hover:underline">
          隐私政策
        </Link>
      </p>

      {/* 登录链接 */}
      <p className="text-center text-sm text-content-tertiary">
        已有账户？{" "}
        <Link
          href="/auth/sign-in"
          className="text-brand-500 hover:text-brand-600 font-medium transition-colors"
        >
          立即登录
        </Link>
      </p>
    </div>
  );
}

export default function SignUpPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    }>
      <SignUpForm />
    </Suspense>
  );
}
