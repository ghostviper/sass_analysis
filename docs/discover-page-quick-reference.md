# Discover 页面改进 - 快速参考

**快速查阅**: 所有改进的核心要点

---

## 🎨 UI 改进速查

### 图标使用
```tsx
// ❌ 不要使用 emoji
<div>📊</div>

// ✅ 使用 Lucide 图标
import { Package } from 'lucide-react'
<Package className="h-4 w-4 text-brand-600" />
```

### 文本对比度
```tsx
// ❌ 对比度不足
className="text-content-muted"  // 3.2:1

// ✅ 充足对比度
className="text-slate-600 dark:text-slate-400"  // 7.1:1
```

### Loading 状态
```tsx
// ❌ 不一致的 spinner
{loading && <Loader2 className="animate-spin" />}

// ✅ 统一的骨架屏
{loading && (
  <Card className="animate-pulse">
    <div className="h-48 bg-surface-hover rounded-lg" />
  </Card>
)}
```

---

## 🖱️ 交互改进速查

### 按钮状态
```tsx
// ❌ 只有 hover
className="hover:bg-surface"

// ✅ hover + active
className="
  hover:bg-surface 
  active:bg-surface-hover 
  active:scale-95 
  transition-all duration-150
"
```

### 触摸目标
```tsx
// ❌ 太小 (32px)
className="w-8 h-8"

// ✅ 标准尺寸 (44px)
className="min-w-[44px] min-h-[44px] w-11 h-11"
```

### 卡片链接
```tsx
// ❌ 嵌套链接冲突
<Card hover>
  <Link href="/a">Link A</Link>
  <Link href="/b">Link B</Link>
</Card>

// ✅ 独立链接
<Card>
  <Link href="/a" className="hover:bg-surface">Link A</Link>
  <Link href="/b" className="btn btn-primary">Link B</Link>
</Card>
```

---

## 📱 移动端优化速查

### 触摸间距
```tsx
// ❌ 间距不足
className="flex gap-1"  // 4px

// ✅ 充足间距
className="flex gap-3"  // 12px
```

### 横向滚动
```tsx
// ✅ 添加渐变提示
<div className="relative">
  {canScrollLeft && (
    <div className="absolute left-0 ... bg-gradient-to-r from-background to-transparent" />
  )}
  <div className="overflow-x-auto">...</div>
  {canScrollRight && (
    <div className="absolute right-0 ... bg-gradient-to-l from-background to-transparent" />
  )}
</div>
```

### 防止手势冲突
```tsx
style={{ 
  overscrollBehavior: 'contain',
  WebkitOverflowScrolling: 'touch'
}}
```

---

## 🚨 错误和空状态速查

### 错误状态
```tsx
import { ErrorState } from '@/components/ui/ErrorState'

{error && (
  <ErrorState 
    onRetry={() => refetch()}
  />
)}
```

### 空状态
```tsx
import { EmptyState } from '@/components/ui/EmptyState'
import { Users } from 'lucide-react'

{items.length === 0 && (
  <EmptyState
    icon={Users}
    title="暂无内容"
    description="我们正在努力准备中"
    actionLabel="浏览其他"
    actionHref="/products"
  />
)}
```

---

## 🎯 图标尺寸规范

| 用途 | 尺寸 | Tailwind |
|------|------|----------|
| 标签内 | 12px | `h-3 w-3` |
| 按钮/卡片 | 16px | `h-4 w-4` |
| 标题旁 | 20px | `h-5 w-5` |
| 大图标 | 24px | `h-6 w-6` |
| Hero 区域 | 28px | `h-7 w-7` |

---

## 🎨 颜色使用规范

### 文本颜色
```tsx
// 主要文本
className="text-content-primary"  // #1E293B

// 次要文本
className="text-slate-600 dark:text-slate-400"  // #475569

// 三级文本
className="text-content-tertiary"  // #64748B
```

### 状态颜色
```tsx
// 成功
className="text-emerald-600 dark:text-emerald-400"

// 警告
className="text-amber-600 dark:text-amber-400"

// 错误
className="text-red-600 dark:text-red-400"

// 品牌色
className="text-brand-600 dark:text-brand-400"
```

---

## ⚡ 过渡动画规范

### 标准过渡
```tsx
// 颜色变化
className="transition-colors duration-150"

// 全部属性
className="transition-all duration-200"

// 缩放效果
className="transition-transform duration-150"
```

### 动画时长
- 微交互: 150ms
- 标准交互: 200ms
- 复杂动画: 300ms
- 最大时长: 500ms

---

## 📏 间距规范

### 组件间距
```tsx
// 模块间
className="space-y-8"  // 32px

// 卡片间
className="gap-4"      // 16px
className="gap-5"      // 20px

// 内容间
className="space-y-4"  // 16px
```

### 内边距
```tsx
// 卡片
className="p-6"        // 24px

// 按钮
className="px-4 py-2.5"  // 16px 10px

// 小组件
className="p-2.5"      // 10px
```

---

## ✅ 快速检查清单

### 发布前检查
- [ ] 无 emoji 图标
- [ ] 文本对比度 ≥ 4.5:1
- [ ] 触摸目标 ≥ 44px
- [ ] 所有按钮有 active 状态
- [ ] Loading 使用骨架屏
- [ ] 错误有重试机制
- [ ] 空状态有引导
- [ ] 横向滚动有提示

### 移动端检查
- [ ] 在 375px 宽度测试
- [ ] 触摸间距 ≥ 8px
- [ ] 手势不冲突
- [ ] 键盘类型正确

### 可访问性检查
- [ ] 键盘可导航
- [ ] ARIA 标签完整
- [ ] 焦点状态可见
- [ ] 支持 reduced-motion

---

## 🔗 相关链接

- [完整 UI 审查](./discover-page-ui-review.md)
- [完整 UX 审查](./discover-page-ux-interaction-review.md)
- [实施记录](./discover-page-improvements-applied.md)
- [改进总结](./discover-page-improvements-summary.md)

---

**最后更新**: 2026-01-19
