"use client";

/**
 * 邮箱验证页面
 */

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Loader2, CheckCircle, XCircle, Mail } from "lucide-react";
import { verifyEmail } from "@/lib/auth-client";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("无效的验证链接");
      return;
    }

    // 自动验证
    const verify = async () => {
      try {
        const result = await verifyEmail(token);
        setStatus("success");
        setMessage(result.message || "邮箱验证成功");
      } catch (err: any) {
        setStatus("error");
        setMessage(err.message || "验证失败，链接可能已过期");
      }
    };

    verify();
  }, [token]);

  // 加载状态
  if (status === "loading") {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto w-16 h-16 rounded-full bg-brand-500/10 flex items-center justify-center">
          <Loader2 className="h-8 w-8 text-brand-500 animate-spin" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
            正在验证
          </h1>
          <p className="text-sm text-content-tertiary mt-2">
            请稍候，正在验证您的邮箱...
          </p>
        </div>
      </div>
    );
  }

  // 成功状态
  if (status === "success") {
    return (
      <div className="space-y-6 text-center">
        <div className="mx-auto w-16 h-16 rounded-full bg-accent-success/10 flex items-center justify-center">
          <CheckCircle className="h-8 w-8 text-accent-success" />
        </div>
        <div>
          <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
            验证成功
          </h1>
          <p className="text-sm text-content-tertiary mt-2">
            {message}
          </p>
        </div>
        <Link href="/auth/sign-in" className="block w-full btn btn-primary py-3">
          前往登录
        </Link>
      </div>
    );
  }

  // 错误状态
  return (
    <div className="space-y-6 text-center">
      <div className="mx-auto w-16 h-16 rounded-full bg-accent-error/10 flex items-center justify-center">
        <XCircle className="h-8 w-8 text-accent-error" />
      </div>
      <div>
        <h1 className="text-2xl font-display font-bold text-content-primary tracking-tight">
          验证失败
        </h1>
        <p className="text-sm text-content-tertiary mt-2">
          {message}
        </p>
      </div>
      <div className="space-y-3">
        <Link href="/auth/sign-in" className="block w-full btn btn-primary py-3">
          返回登录
        </Link>
        <p className="text-sm text-content-tertiary">
          需要重新发送验证邮件？请登录后在设置中操作
        </p>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}
