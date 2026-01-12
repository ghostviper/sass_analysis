"use client";

/**
 * 认证页面布局
 * 
 * 独立的全屏布局，不包含侧边栏
 * 左右分栏设计（桌面端）/ 单栏设计（移动端）
 */

import { Lightbulb, Sparkles, TrendingUp, Users } from "lucide-react";
import Link from "next/link";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* 左侧品牌展示区 - 仅桌面端显示 */}
      <div className="hidden lg:flex lg:w-[45%] xl:w-[50%] relative bg-gradient-to-br from-brand-600 via-brand-500 to-accent-secondary overflow-hidden">
        {/* 背景装饰 */}
        <div className="absolute inset-0">
          {/* 网格 */}
          <div 
            className="absolute inset-0 opacity-[0.07]"
            style={{
              backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
              backgroundSize: '60px 60px'
            }}
          />
          {/* 光晕效果 */}
          <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-white/10 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/4" />
          <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-white/10 rounded-full blur-[80px] translate-y-1/3 -translate-x-1/4" />
          <div className="absolute top-1/2 left-1/2 w-[300px] h-[300px] bg-accent-secondary/20 rounded-full blur-[60px] -translate-x-1/2 -translate-y-1/2" />
        </div>
        
        {/* 内容 */}
        <div className="relative z-10 flex flex-col justify-between p-8 xl:p-12 w-full">
          {/* 顶部 Logo */}
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/20 backdrop-blur-sm shadow-lg border border-white/10">
              <Lightbulb className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-display font-bold text-white tracking-tight">
              BuildWhat
            </span>
          </Link>
          
          {/* 中间主内容 */}
          <div className="flex-1 flex flex-col justify-center max-w-lg">
            <h1 className="text-4xl xl:text-5xl font-display font-bold text-white leading-[1.15] tracking-tight">
              发现下一个
              <br />
              <span className="text-white/90">独立开发机会</span>
            </h1>
            
            <p className="text-lg text-white/75 mt-6 leading-relaxed">
              基于 AI 驱动的 SaaS 产品分析平台，帮助独立开发者发现蓝海市场、分析竞品策略、找到最适合的创业方向。
            </p>
            
            {/* 特性列表 */}
            <div className="mt-10 space-y-4">
              {[
                { icon: Sparkles, text: "智能分析 1000+ SaaS 产品数据" },
                { icon: TrendingUp, text: "AI 助手实时解答产品问题" },
                { icon: Users, text: "多维度选品评分系统" },
              ].map((feature, index) => (
                <div 
                  key={index} 
                  className="flex items-center gap-4 text-white/90"
                >
                  <div className="h-10 w-10 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center border border-white/10">
                    <feature.icon className="h-5 w-5" />
                  </div>
                  <span className="text-[15px] font-medium">{feature.text}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* 底部信息 */}
          <div className="text-white/50 text-sm">
            © 2026 BuildWhat. All rights reserved.
          </div>
        </div>
      </div>

      {/* 右侧认证表单区 */}
      <div className="flex-1 flex flex-col min-h-screen bg-background">
        {/* 移动端顶部导航 */}
        <div className="lg:hidden flex items-center justify-between p-4 border-b border-surface-border">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-brand shadow-sm">
              <Lightbulb className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-display font-bold text-content-primary tracking-tight">
              BuildWhat
            </span>
          </Link>
        </div>
        
        {/* 表单容器 */}
        <div className="flex-1 flex items-center justify-center p-6 sm:p-8">
          <div className="w-full max-w-[400px]">
            {children}
          </div>
        </div>
        
        {/* 移动端底部信息 */}
        <div className="lg:hidden text-center text-content-muted text-xs py-4 border-t border-surface-border">
          © 2026 BuildWhat. All rights reserved.
        </div>
      </div>
    </div>
  );
}
