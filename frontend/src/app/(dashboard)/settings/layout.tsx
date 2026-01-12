/**
 * 设置页面布局
 * 
 * 与项目其他页面风格一致的设置页面布局
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { User, Shield, Palette, CreditCard, Settings } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useEffect } from "react";
import { Card } from "@/components/ui/Card";

const settingsNav = [
  {
    name: "个人资料",
    href: "/settings/profile",
    icon: User,
    description: "管理您的个人信息",
  },
  {
    name: "账户安全",
    href: "/settings/account",
    icon: Shield,
    description: "密码和登录设置",
  },
  {
    name: "偏好设置",
    href: "/settings/preferences",
    icon: Palette,
    description: "语言、主题等",
  },
  {
    name: "订阅与账单",
    href: "/settings/billing",
    icon: CreditCard,
    description: "管理您的订阅",
  },
];

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { isAuthenticated, isLoading, redirectToLogin } = useAuth();

  // 未登录重定向
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      redirectToLogin("/settings");
    }
  }, [isLoading, isAuthenticated, redirectToLogin]);

  // 加载中
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-8 w-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // 未登录
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* 页面标题横幅 - 与 Dashboard 风格一致 */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-brand-500/10 via-brand-400/5 to-accent-secondary/10 border border-brand-500/20 p-6 md:p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-brand-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-accent-secondary/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2" />
        <div className="relative flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-brand-500 via-brand-600 to-accent-secondary flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Settings className="h-7 w-7 text-white" />
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-display font-bold tracking-tight bg-gradient-to-r from-content-primary via-content-primary to-brand-600 dark:to-brand-400 bg-clip-text text-transparent">
              设置
            </h1>
            <p className="text-sm text-content-secondary mt-1 font-medium">
              管理您的账户设置和偏好
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* 左侧导航 */}
        <nav className="lg:w-60 shrink-0">
          <Card padding="sm" className="lg:sticky lg:top-20">
            <div className="space-y-1">
              {settingsNav.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all duration-200",
                      isActive
                        ? "bg-brand-500/10 text-brand-600 dark:text-brand-400"
                        : "text-content-secondary hover:bg-surface hover:text-content-primary"
                    )}
                  >
                    <item.icon
                      className={cn(
                        "h-4 w-4",
                        isActive
                          ? "text-brand-600 dark:text-brand-400"
                          : "text-content-muted"
                      )}
                    />
                    <span className="font-medium">{item.name}</span>
                  </Link>
                );
              })}
            </div>
          </Card>
        </nav>

        {/* 右侧内容 */}
        <div className="flex-1 min-w-0">{children}</div>
      </div>
    </div>
  );
}
