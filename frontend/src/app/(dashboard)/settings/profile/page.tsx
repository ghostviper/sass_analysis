/**
 * 个人资料设置页面
 */

"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { UserAvatar } from "@/components/user/UserAvatar";
import { updateProfile } from "@/lib/user-client";
import { Card } from "@/components/ui/Card";
import { Camera, Check, Mail, User, AlertCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function ProfileSettingsPage() {
  const { user, refreshSession } = useAuth();
  const [name, setName] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 初始化表单
  useEffect(() => {
    if (user?.name) {
      setName(user.name);
    }
  }, [user?.name]);

  const handleSave = async () => {
    if (!name.trim()) {
      setError("昵称不能为空");
      return;
    }

    setIsSaving(true);
    setError(null);
    
    try {
      const success = await updateProfile({ name: name.trim() });
      
      if (success) {
        setSaveSuccess(true);
        await refreshSession();
        setTimeout(() => setSaveSuccess(false), 2000);
      } else {
        setError("保存失败，请重试");
      }
    } catch (err) {
      setError("保存失败，请重试");
    } finally {
      setIsSaving(false);
    }
  };

  const hasChanges = name.trim() !== (user?.name || "");

  return (
    <div className="space-y-6">
      {/* 头像区域 */}
      <Card>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          头像
        </h2>
        <div className="flex items-center gap-6">
          <div className="relative group">
            <UserAvatar
              email={user?.email}
              image={user?.image}
              name={user?.name}
              size="xl"
            />
            <button
              className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"
              onClick={() => {
                // TODO: 打开头像上传对话框
                console.log("Upload avatar");
              }}
            >
              <Camera className="h-5 w-5 text-white" />
            </button>
          </div>
          <div>
            <p className="text-sm text-content-secondary font-medium">
              点击头像更换图片
            </p>
            <p className="text-xs text-content-muted mt-1">
              支持 JPG、PNG 格式，最大 2MB
            </p>
          </div>
        </div>
      </Card>

      {/* 基本信息 */}
      <Card>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          基本信息
        </h2>
        
        {/* 错误提示 */}
        {error && (
          <div className="mb-4 p-3 rounded-xl bg-accent-error/10 border border-accent-error/20 flex items-center gap-2 text-sm text-accent-error">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}
        
        <div className="space-y-4 max-w-md">
          {/* 昵称 */}
          <div>
            <label className="block text-sm font-medium text-content-secondary mb-1.5">
              昵称
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
              <input
                type="text"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  setError(null);
                }}
                placeholder="输入您的昵称"
                className="w-full h-10 pl-10 pr-4 rounded-xl border border-surface-border bg-surface/50 text-content-primary placeholder:text-content-muted focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
              />
            </div>
          </div>

          {/* 邮箱（只读） */}
          <div>
            <label className="block text-sm font-medium text-content-secondary mb-1.5">
              邮箱
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
              <input
                type="email"
                value={user?.email || ""}
                disabled
                className="w-full h-10 pl-10 pr-4 rounded-xl border border-surface-border bg-surface/30 text-content-muted cursor-not-allowed"
              />
            </div>
            <p className="text-xs text-content-muted mt-1">
              邮箱地址不可修改
            </p>
          </div>
        </div>

        {/* 保存按钮 */}
        <div className="mt-6 flex items-center gap-3">
          <button
            onClick={handleSave}
            disabled={isSaving || !hasChanges}
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all",
              isSaving || !hasChanges
                ? "bg-surface text-content-muted cursor-not-allowed"
                : "bg-brand-500 text-white hover:bg-brand-600 shadow-sm"
            )}
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                保存中...
              </>
            ) : saveSuccess ? (
              <>
                <Check className="h-4 w-4" />
                已保存
              </>
            ) : (
              "保存更改"
            )}
          </button>
          {hasChanges && !isSaving && (
            <span className="text-xs text-content-muted">有未保存的更改</span>
          )}
        </div>
      </Card>

      {/* 关联账户 */}
      <Card>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          关联账户
        </h2>
        <div className="space-y-3">
          {/* Google */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-surface-border/50">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-white flex items-center justify-center shadow-sm border border-surface-border/50">
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-content-primary">
                  Google
                </p>
                <p className="text-xs text-content-muted">
                  {user?.image ? "已关联" : "未关联"}
                </p>
              </div>
            </div>
            <span className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-medium",
              user?.image 
                ? "bg-accent-success/10 text-accent-success" 
                : "bg-surface text-content-muted"
            )}>
              {user?.image ? "已关联" : "未关联"}
            </span>
          </div>
        </div>
      </Card>

      {/* 账户信息 */}
      <Card>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          账户信息
        </h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2">
            <span className="text-sm text-content-muted">用户 ID</span>
            <span className="text-sm text-content-secondary font-mono">
              {user?.id ? `${user.id.slice(0, 8)}...` : "-"}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-t border-surface-border/50">
            <span className="text-sm text-content-muted">当前计划</span>
            <span className={cn(
              "px-2.5 py-1 rounded-lg text-xs font-medium",
              user?.plan === "pro" 
                ? "bg-brand-500/10 text-brand-600 dark:text-brand-400" 
                : "bg-surface text-content-secondary"
            )}>
              {user?.plan === "pro" ? "Pro" : user?.plan === "enterprise" ? "Enterprise" : "Free"}
            </span>
          </div>
          <div className="flex justify-between items-center py-2 border-t border-surface-border/50">
            <span className="text-sm text-content-muted">注册时间</span>
            <span className="text-sm text-content-secondary">
              {user?.createdAt 
                ? new Date(user.createdAt).toLocaleDateString("zh-CN")
                : "-"
              }
            </span>
          </div>
        </div>
      </Card>
    </div>
  );
}
