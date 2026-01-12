"use client";

/**
 * 客户端图标组件
 * 
 * 解决 Lucide 图标在 Next.js 中的 hydration 问题
 */

import { useState, useEffect, ComponentType } from "react";
import type { LucideProps } from "lucide-react";

interface ClientIconProps extends LucideProps {
  icon: ComponentType<LucideProps>;
}

export function ClientIcon({ icon: Icon, ...props }: ClientIconProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // 返回一个占位符，保持布局一致
    return <span className={props.className} style={{ display: "inline-block" }} />;
  }

  return <Icon {...props} />;
}
