"use client";

/**
 * 用户头像组件
 * 
 * 支持：
 * - 自定义头像图片
 * - 基于邮箱的 unavatar.io 头像
 * - 默认占位头像
 * - 在线状态指示器
 */

import { cn } from "@/lib/utils";
import { useUserAvatar } from "@/hooks/useAuth";
import Image from "next/image";

interface UserAvatarProps {
  email?: string | null;
  image?: string | null;
  name?: string | null;
  size?: "sm" | "md" | "lg" | "xl";
  showOnlineStatus?: boolean;
  className?: string;
}

const sizeClasses = {
  sm: "h-6 w-6 text-[10px]",
  md: "h-8 w-8 text-xs",
  lg: "h-10 w-10 text-sm",
  xl: "h-12 w-12 text-base",
};

const statusSizeClasses = {
  sm: "h-1.5 w-1.5 border",
  md: "h-2 w-2 border-2",
  lg: "h-2.5 w-2.5 border-2",
  xl: "h-3 w-3 border-2",
};

export function UserAvatar({
  email,
  image,
  name,
  size = "md",
  showOnlineStatus = false,
  className,
}: UserAvatarProps) {
  const avatarUrl = useUserAvatar(email, image);
  const initials = name?.charAt(0).toUpperCase() || email?.charAt(0).toUpperCase() || "U";

  return (
    <div className={cn("relative shrink-0", className)}>
      {avatarUrl ? (
        <div
          className={cn(
            "rounded-lg overflow-hidden bg-gradient-brand",
            sizeClasses[size]
          )}
        >
          <Image
            src={avatarUrl}
            alt={name || email || "User avatar"}
            width={48}
            height={48}
            className="h-full w-full object-cover"
            unoptimized // 外部图片不优化
          />
        </div>
      ) : (
        <div
          className={cn(
            "rounded-lg bg-gradient-brand flex items-center justify-center text-white font-semibold shadow-sm",
            sizeClasses[size]
          )}
        >
          {initials}
        </div>
      )}

      {/* 在线状态指示器 */}
      {showOnlineStatus && (
        <span
          className={cn(
            "absolute -bottom-0.5 -right-0.5 rounded-full bg-accent-success border-background-secondary",
            statusSizeClasses[size]
          )}
        />
      )}
    </div>
  );
}
