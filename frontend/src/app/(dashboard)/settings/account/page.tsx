/**
 * 账户安全设置页面
 */

"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { deleteAccount } from "@/lib/user-client";
import { Card } from "@/components/ui/Card";
import { Eye, EyeOff, Key, Trash2, AlertTriangle, Loader2, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

export default function AccountSettingsPage() {
  const { logout } = useAuth();
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  const handleChangePassword = async () => {
    setPasswordError(null);
    
    if (!currentPassword) {
      setPasswordError("请输入当前密码");
      return;
    }
    if (newPassword.length < 8) {
      setPasswordError("新密码至少需要8位");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("两次输入的密码不一致");
      return;
    }
    
    setIsSaving(true);
    try {
      // TODO: 实现密码修改 API
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      alert("密码修改成功");
    } catch (err) {
      setPasswordError("密码修改失败，请重试");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    setDeleteError(null);
    
    try {
      const success = await deleteAccount();
      if (success) {
        await logout();
      } else {
        setDeleteError("删除失败，请重试");
      }
    } catch (err) {
      setDeleteError("删除失败，请重试");
    } finally {
      setIsDeleting(false);
    }
  };

  const inputClass = "w-full h-10 pl-10 pr-10 rounded-xl border border-surface-border bg-surface/50 text-content-primary placeholder:text-content-muted focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all";

  return (
    <div className="space-y-6">
      {/* 修改密码 */}
      <Card>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          修改密码
        </h2>
        
        {passwordError && (
          <div className="mb-4 p-3 rounded-xl bg-accent-error/10 border border-accent-error/20 text-sm text-accent-error flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {passwordError}
          </div>
        )}
        
        <div className="space-y-4 max-w-md">
          {/* 当前密码 */}
          <div>
            <label className="block text-sm font-medium text-content-secondary mb-1.5">
              当前密码
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
              <input
                type={showCurrentPassword ? "text" : "password"}
                value={currentPassword}
                onChange={(e) => {
                  setCurrentPassword(e.target.value);
                  setPasswordError(null);
                }}
                placeholder="输入当前密码"
                className={inputClass}
              />
              <button
                type="button"
                onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-content-muted hover:text-content-secondary transition-colors"
              >
                {showCurrentPassword ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>

          {/* 新密码 */}
          <div>
            <label className="block text-sm font-medium text-content-secondary mb-1.5">
              新密码
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
              <input
                type={showNewPassword ? "text" : "password"}
                value={newPassword}
                onChange={(e) => {
                  setNewPassword(e.target.value);
                  setPasswordError(null);
                }}
                placeholder="输入新密码（至少8位）"
                className={inputClass}
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-content-muted hover:text-content-secondary transition-colors"
              >
                {showNewPassword ? (
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
              确认新密码
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-content-muted" />
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  setPasswordError(null);
                }}
                placeholder="再次输入新密码"
                className="w-full h-10 pl-10 pr-4 rounded-xl border border-surface-border bg-surface/50 text-content-primary placeholder:text-content-muted focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
              />
            </div>
          </div>

          <button
            onClick={handleChangePassword}
            disabled={isSaving || !currentPassword || !newPassword || !confirmPassword}
            className={cn(
              "inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all",
              isSaving || !currentPassword || !newPassword || !confirmPassword
                ? "bg-surface text-content-muted cursor-not-allowed"
                : "bg-brand-500 text-white hover:bg-brand-600 shadow-sm"
            )}
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                保存中...
              </>
            ) : (
              "修改密码"
            )}
          </button>
        </div>
        
        <p className="text-xs text-content-muted mt-4">
          注意：如果您是通过 Google 登录的，可能没有设置密码。
        </p>
      </Card>

      {/* 登录设备 */}
      <Card>
        <h2 className="text-lg font-display font-bold text-content-primary mb-4 tracking-tight">
          登录设备
        </h2>
        <p className="text-sm text-content-tertiary mb-4">
          管理您的登录会话，可以退出其他设备上的登录
        </p>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 rounded-xl bg-surface/50 border border-surface-border/50">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-brand-500/10 flex items-center justify-center">
                <Shield className="h-5 w-5 text-brand-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-content-primary">
                  当前设备
                </p>
                <p className="text-xs text-content-muted">
                  最后活动：刚刚
                </p>
              </div>
            </div>
            <span className="text-xs text-accent-success bg-accent-success/10 px-3 py-1.5 rounded-lg font-medium">
              当前
            </span>
          </div>
        </div>
        <button 
          className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium bg-surface border border-surface-border text-content-secondary hover:bg-surface-hover transition-all"
          onClick={() => {
            alert("功能开发中");
          }}
        >
          退出所有其他设备
        </button>
      </Card>

      {/* 危险区域 */}
      <Card className="border-accent-error/20">
        <h2 className="text-lg font-display font-bold text-accent-error mb-4 tracking-tight">
          危险区域
        </h2>
        <p className="text-sm text-content-tertiary mb-4">
          删除账户后，您的所有数据将被永久删除，此操作不可撤销。
        </p>
        
        {deleteError && (
          <div className="mb-4 p-3 rounded-xl bg-accent-error/10 border border-accent-error/20 text-sm text-accent-error flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {deleteError}
          </div>
        )}
        
        {!showDeleteConfirm ? (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium bg-accent-error/10 text-accent-error hover:bg-accent-error/20 transition-all"
          >
            <Trash2 className="h-4 w-4" />
            删除账户
          </button>
        ) : (
          <div className="p-4 rounded-xl bg-accent-error/5 border border-accent-error/20">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-accent-error shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-content-primary">
                  确定要删除账户吗？
                </p>
                <p className="text-xs text-content-tertiary mt-1">
                  此操作将永久删除您的账户和所有相关数据，包括：
                </p>
                <ul className="text-xs text-content-tertiary mt-1 list-disc list-inside space-y-0.5">
                  <li>个人资料信息</li>
                  <li>所有聊天会话和消息</li>
                  <li>关联的第三方账户</li>
                </ul>
                <div className="flex gap-2 mt-4">
                  <button
                    onClick={handleDeleteAccount}
                    disabled={isDeleting}
                    className={cn(
                      "inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all",
                      isDeleting 
                        ? "bg-accent-error/50 text-white cursor-not-allowed" 
                        : "bg-accent-error text-white hover:bg-accent-error/90"
                    )}
                  >
                    {isDeleting ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        删除中...
                      </>
                    ) : (
                      "确认删除"
                    )}
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    disabled={isDeleting}
                    className="px-4 py-2 rounded-xl text-sm font-medium bg-surface border border-surface-border text-content-secondary hover:bg-surface-hover transition-all"
                  >
                    取消
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
