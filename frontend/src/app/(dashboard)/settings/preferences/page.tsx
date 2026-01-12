/**
 * 偏好设置页面
 */

"use client";

import { useState } from "react";
import { useTheme } from "next-themes";
import { useLocale } from "@/contexts/LocaleContext";
import { Card } from "@/components/ui/Card";
import { Globe, Moon, Sun, Monitor, Check, Bell, Mail } from "lucide-react";
import { cn } from "@/lib/utils";

const languages = [
  { code: "zh-CN", name: "简体中文", flag: "🇨🇳" },
  { code: "en", name: "English", flag: "🇺🇸" },
];

const themes = [
  { value: "light", name: "浅色", icon: Sun, desc: "明亮的界面" },
  { value: "dark", name: "深色", icon: Moon, desc: "护眼模式" },
  { value: "system", name: "跟随系统", icon: Monitor, desc: "自动切换" },
];

export default function PreferencesSettingsPage() {
  const { theme, setTheme } = useTheme();
  const { locale, setLocale } = useLocale();
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [marketingEmails, setMarketingEmails] = useState(false);

  return (
    <div className="space-y-6">
      {/* 语言设置 */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-xl bg-brand-500/10 flex items-center justify-center">
            <Globe className="h-5 w-5 text-brand-500" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              语言
            </h2>
            <p className="text-sm text-content-muted">
              选择您偏好的界面语言
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setLocale(lang.code as "zh-CN" | "en")}
              className={cn(
                "flex items-center gap-3 p-4 rounded-xl border transition-all duration-200",
                locale === lang.code
                  ? "border-brand-500 bg-brand-500/5"
                  : "border-surface-border hover:border-brand-500/30 hover:bg-surface/50"
              )}
            >
              <span className="text-2xl">{lang.flag}</span>
              <span className="text-sm font-medium text-content-primary flex-1 text-left">
                {lang.name}
              </span>
              {locale === lang.code && (
                <div className="h-5 w-5 rounded-full bg-brand-500 flex items-center justify-center">
                  <Check className="h-3 w-3 text-white" />
                </div>
              )}
            </button>
          ))}
        </div>
      </Card>

      {/* 主题设置 */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-xl bg-accent-secondary/10 flex items-center justify-center">
            <Sun className="h-5 w-5 text-accent-secondary" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              主题
            </h2>
            <p className="text-sm text-content-muted">
              选择您偏好的界面主题
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {themes.map((t) => (
            <button
              key={t.value}
              onClick={() => setTheme(t.value)}
              className={cn(
                "flex flex-col items-center gap-2 p-4 rounded-xl border transition-all duration-200",
                theme === t.value
                  ? "border-brand-500 bg-brand-500/5"
                  : "border-surface-border hover:border-brand-500/30 hover:bg-surface/50"
              )}
            >
              <div className={cn(
                "h-12 w-12 rounded-xl flex items-center justify-center",
                theme === t.value
                  ? "bg-brand-500/10"
                  : "bg-surface"
              )}>
                <t.icon
                  className={cn(
                    "h-6 w-6",
                    theme === t.value
                      ? "text-brand-500"
                      : "text-content-muted"
                  )}
                />
              </div>
              <span className="text-sm font-medium text-content-primary">
                {t.name}
              </span>
              <span className="text-xs text-content-muted">
                {t.desc}
              </span>
              {theme === t.value && (
                <div className="h-5 w-5 rounded-full bg-brand-500 flex items-center justify-center">
                  <Check className="h-3 w-3 text-white" />
                </div>
              )}
            </button>
          ))}
        </div>
      </Card>

      {/* 通知设置 */}
      <Card>
        <div className="flex items-center gap-3 mb-4">
          <div className="h-10 w-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
            <Bell className="h-5 w-5 text-amber-500" />
          </div>
          <div>
            <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
              通知
            </h2>
            <p className="text-sm text-content-muted">
              管理您的通知偏好
            </p>
          </div>
        </div>
        <div className="space-y-4">
          <label className="flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-surface-border/50 cursor-pointer hover:bg-surface/80 transition-colors">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-brand-500/10 flex items-center justify-center">
                <Mail className="h-5 w-5 text-brand-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-content-primary">
                  邮件通知
                </p>
                <p className="text-xs text-content-muted">
                  接收产品更新和重要通知
                </p>
              </div>
            </div>
            <div className="relative">
              <input
                type="checkbox"
                checked={emailNotifications}
                onChange={(e) => setEmailNotifications(e.target.checked)}
                className="sr-only peer"
              />
              <div className={cn(
                "w-11 h-6 rounded-full transition-colors",
                emailNotifications ? "bg-brand-500" : "bg-surface-border"
              )}>
                <div className={cn(
                  "absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform",
                  emailNotifications && "translate-x-5"
                )} />
              </div>
            </div>
          </label>
          
          <label className="flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-surface-border/50 cursor-pointer hover:bg-surface/80 transition-colors">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-accent-secondary/10 flex items-center justify-center">
                <Mail className="h-5 w-5 text-accent-secondary" />
              </div>
              <div>
                <p className="text-sm font-medium text-content-primary">
                  营销邮件
                </p>
                <p className="text-xs text-content-muted">
                  接收促销和优惠信息
                </p>
              </div>
            </div>
            <div className="relative">
              <input
                type="checkbox"
                checked={marketingEmails}
                onChange={(e) => setMarketingEmails(e.target.checked)}
                className="sr-only peer"
              />
              <div className={cn(
                "w-11 h-6 rounded-full transition-colors",
                marketingEmails ? "bg-brand-500" : "bg-surface-border"
              )}>
                <div className={cn(
                  "absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform",
                  marketingEmails && "translate-x-5"
                )} />
              </div>
            </div>
          </label>
        </div>
      </Card>
    </div>
  );
}
