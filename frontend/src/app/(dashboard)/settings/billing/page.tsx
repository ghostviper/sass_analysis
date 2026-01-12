/**
 * 订阅与账单页面
 */

"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { getUsage, UsageStats } from "@/lib/user-client";
import { Card } from "@/components/ui/Card";
import { Check, Zap, Crown, Building2, Loader2, RefreshCw, TrendingUp, MessageSquare, Coins } from "lucide-react";
import { cn } from "@/lib/utils";

const plans = [
  {
    name: "免费版",
    price: "¥0",
    period: "永久免费",
    icon: Zap,
    planKey: "free",
    features: [
      "每日 10 次 AI 对话",
      "基础产品分析",
      "公开数据访问",
      "社区支持",
    ],
  },
  {
    name: "Pro",
    price: "¥99",
    period: "/月",
    icon: Crown,
    planKey: "pro",
    features: [
      "每日 100 次 AI 对话",
      "高级产品分析",
      "完整数据导出",
      "优先客服支持",
      "API 访问",
    ],
    popular: true,
  },
  {
    name: "企业版",
    price: "联系我们",
    period: "",
    icon: Building2,
    planKey: "enterprise",
    features: [
      "无限 AI 对话",
      "定制化分析报告",
      "专属客户经理",
      "SLA 保障",
      "私有化部署",
    ],
  },
];

export default function BillingSettingsPage() {
  const { user } = useAuth();
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const currentPlan = user?.plan || "free";

  const fetchUsage = async (showRefresh = false) => {
    if (showRefresh) setIsRefreshing(true);
    else setIsLoading(true);
    
    try {
      const data = await getUsage();
      setUsage(data);
    } catch (err) {
      console.error("Failed to fetch usage:", err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchUsage();
  }, []);

  // 计算使用百分比
  const usagePercent = usage 
    ? Math.min((usage.daily_chat_used / usage.daily_chat_limit) * 100, 100)
    : 0;

  return (
    <div className="space-y-6">
      {/* 当前订阅 */}
      <Card>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          当前订阅
        </h2>
        <div className="flex items-center justify-between p-4 rounded-xl bg-gradient-to-r from-brand-500/5 to-accent-secondary/5 border border-brand-500/20">
          <div className="flex items-center gap-4">
            <div className={cn(
              "h-12 w-12 rounded-xl flex items-center justify-center shadow-sm",
              currentPlan === "pro" 
                ? "bg-gradient-to-br from-brand-500 to-brand-600" 
                : currentPlan === "enterprise"
                  ? "bg-gradient-to-br from-purple-500 to-purple-600"
                  : "bg-surface border border-surface-border"
            )}>
              {currentPlan === "pro" ? (
                <Crown className="h-6 w-6 text-white" />
              ) : currentPlan === "enterprise" ? (
                <Building2 className="h-6 w-6 text-white" />
              ) : (
                <Zap className="h-6 w-6 text-content-muted" />
              )}
            </div>
            <div>
              <p className="text-base font-semibold text-content-primary">
                {currentPlan === "pro" 
                  ? "Pro 会员" 
                  : currentPlan === "enterprise"
                    ? "企业版"
                    : "免费版"
                }
              </p>
              <p className="text-sm text-content-muted">
                {currentPlan === "free"
                  ? "升级解锁更多功能"
                  : "感谢您的支持！"
                }
              </p>
            </div>
          </div>
          {currentPlan === "free" && (
            <button 
              className="px-4 py-2 rounded-xl text-sm font-medium bg-brand-500 text-white hover:bg-brand-600 shadow-sm transition-all"
              onClick={() => alert("支付功能开发中")}
            >
              升级 Pro
            </button>
          )}
        </div>
      </Card>

      {/* 使用统计 */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-display font-bold text-content-primary tracking-tight">
            使用统计
          </h2>
          <button
            onClick={() => fetchUsage(true)}
            disabled={isRefreshing}
            className="p-2 rounded-lg hover:bg-surface transition-colors"
          >
            <RefreshCw className={cn("h-4 w-4 text-content-muted", isRefreshing && "animate-spin")} />
          </button>
        </div>
        
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-content-muted" />
          </div>
        ) : (
          <>
            {/* 今日配额进度条 */}
            <div className="mb-6 p-4 rounded-xl bg-surface/50 border border-surface-border/50">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-content-secondary">今日 AI 对话配额</span>
                <span className="text-sm font-semibold text-content-primary tabular-nums">
                  {usage?.daily_chat_used || 0} / {usage?.daily_chat_limit || 10}
                </span>
              </div>
              <div className="h-2.5 bg-surface rounded-full overflow-hidden">
                <div 
                  className={cn(
                    "h-full rounded-full transition-all duration-500",
                    usagePercent >= 90 
                      ? "bg-gradient-to-r from-accent-error to-accent-error/80" 
                      : usagePercent >= 70 
                        ? "bg-gradient-to-r from-accent-warning to-accent-warning/80"
                        : "bg-gradient-to-r from-brand-500 to-brand-400"
                  )}
                  style={{ width: `${usagePercent}%` }}
                />
              </div>
              {usagePercent >= 90 && (
                <p className="text-xs text-accent-error mt-2 font-medium">
                  配额即将用尽，升级 Pro 获取更多对话次数
                </p>
              )}
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-surface/50 border border-surface-border/50">
                <div className="flex items-center gap-2 mb-2">
                  <div className="h-8 w-8 rounded-lg bg-brand-500/10 flex items-center justify-center">
                    <MessageSquare className="h-4 w-4 text-brand-500" />
                  </div>
                  <span className="text-xs text-content-muted">总会话数</span>
                </div>
                <p className="text-2xl font-bold text-content-primary tabular-nums">
                  {usage?.total_sessions || 0}
                </p>
              </div>
              <div className="p-4 rounded-xl bg-surface/50 border border-surface-border/50">
                <div className="flex items-center gap-2 mb-2">
                  <div className="h-8 w-8 rounded-lg bg-accent-secondary/10 flex items-center justify-center">
                    <TrendingUp className="h-4 w-4 text-accent-secondary" />
                  </div>
                  <span className="text-xs text-content-muted">总消息数</span>
                </div>
                <p className="text-2xl font-bold text-content-primary tabular-nums">
                  {usage?.total_messages || 0}
                </p>
              </div>
              <div className="p-4 rounded-xl bg-surface/50 border border-surface-border/50">
                <div className="flex items-center gap-2 mb-2">
                  <div className="h-8 w-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                    <Coins className="h-4 w-4 text-amber-500" />
                  </div>
                  <span className="text-xs text-content-muted">Token 消耗</span>
                </div>
                <p className="text-2xl font-bold text-content-primary tabular-nums">
                  {((usage?.total_tokens || 0) / 1000).toFixed(1)}
                  <span className="text-sm font-normal text-content-muted ml-1">K</span>
                </p>
              </div>
            </div>
            
            {usage && usage.total_cost > 0 && (
              <div className="mt-4 p-3 rounded-xl bg-surface/50 border border-surface-border/50">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-content-muted">累计 API 消耗</span>
                  <span className="text-sm font-semibold text-content-primary tabular-nums">
                    ${usage.total_cost.toFixed(4)}
                  </span>
                </div>
              </div>
            )}
          </>
        )}
      </Card>

      {/* 套餐对比 */}
      <Card>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          套餐对比
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {plans.map((plan) => {
            const isCurrent = plan.planKey === currentPlan;
            return (
              <div
                key={plan.name}
                className={cn(
                  "relative p-5 rounded-xl border transition-all duration-200",
                  plan.popular
                    ? "border-brand-500 bg-gradient-to-b from-brand-500/5 to-transparent"
                    : isCurrent
                      ? "border-brand-500/50 bg-brand-500/5"
                      : "border-surface-border hover:border-brand-500/30"
                )}
              >
                {plan.popular && !isCurrent && (
                  <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-brand-500 text-white text-[10px] font-semibold shadow-sm">
                    推荐
                  </span>
                )}
                {isCurrent && (
                  <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-accent-success text-white text-[10px] font-semibold shadow-sm">
                    当前
                  </span>
                )}
                <div className="flex items-center gap-2 mb-3">
                  <plan.icon
                    className={cn(
                      "h-5 w-5",
                      plan.popular || isCurrent ? "text-brand-500" : "text-content-muted"
                    )}
                  />
                  <h3 className="font-semibold text-content-primary">
                    {plan.name}
                  </h3>
                </div>
                <div className="mb-4">
                  <span className="text-2xl font-bold text-content-primary">
                    {plan.price}
                  </span>
                  <span className="text-sm text-content-muted">{plan.period}</span>
                </div>
                <ul className="space-y-2.5 mb-5">
                  {plan.features.map((feature) => (
                    <li
                      key={feature}
                      className="flex items-center gap-2 text-sm text-content-secondary"
                    >
                      <Check className="h-4 w-4 text-accent-success shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <button
                  className={cn(
                    "w-full py-2.5 rounded-xl text-sm font-medium transition-all",
                    isCurrent
                      ? "bg-surface text-content-muted cursor-default"
                      : plan.popular
                        ? "bg-brand-500 text-white hover:bg-brand-600 shadow-sm"
                        : "bg-surface border border-surface-border text-content-secondary hover:bg-surface-hover"
                  )}
                  disabled={isCurrent}
                  onClick={() => {
                    if (!isCurrent) {
                      alert(plan.price === "联系我们" ? "请联系 support@buildwhat.com" : "支付功能开发中");
                    }
                  }}
                >
                  {isCurrent ? "当前套餐" : plan.price === "联系我们" ? "联系销售" : "升级"}
                </button>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
