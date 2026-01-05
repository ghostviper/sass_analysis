'use client'

import { useState } from 'react'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Search, Menu } from 'lucide-react'
import { ThemeSwitcher } from './ThemeSwitcher'
import { LanguageSwitcher } from './LanguageSwitcher'
import { useLocale } from '@/contexts/LocaleContext'
import { useSidebar } from '@/contexts/SidebarContext'

export function Header() {
  const pathname = usePathname()
  const { t } = useLocale()
  const { openMobile } = useSidebar()
  const [searchOpen, setSearchOpen] = useState(false)

  // 页面配置 - 使用翻译
  const pageConfig: Record<string, { title: string; subtitle: string }> = {
    '/': {
      title: t('nav.dashboard'),
      subtitle: t('nav.dashboardDesc'),
    },
    '/categories': {
      title: t('nav.categories'),
      subtitle: t('nav.categoriesDesc'),
    },
    '/products': {
      title: t('nav.products'),
      subtitle: t('nav.productsDesc'),
    },
    '/assistant': {
      title: t('nav.assistant'),
      subtitle: t('nav.assistantDesc'),
    },
    '/about': {
      title: t('nav.about'),
      subtitle: t('nav.about'),
    },
  }

  // 获取当前页面配置
  const currentPage = pageConfig[pathname] || pageConfig['/']

  // 处理产品详情页
  const isProductDetail = pathname.startsWith('/products/') && pathname !== '/products'

  return (
    <>
      <header className="sticky top-0 z-30 border-b border-surface-border bg-background/80 backdrop-blur-xl">
        <div className="flex h-14 items-center justify-between px-4 sm:px-6">
          {/* 左侧：页面标题 */}
          <div className="flex items-center gap-3">
            {/* 移动端菜单按钮 */}
            <button
              type="button"
              className="lg:hidden -ml-1 flex h-9 w-9 items-center justify-center rounded-lg text-content-muted hover:bg-surface hover:text-content-primary transition-colors"
              onClick={openMobile}
            >
              <Menu className="h-5 w-5" />
            </button>

            <div className="min-w-0">
              <h1 className="text-lg font-semibold tracking-tight text-content-primary truncate">
                {isProductDetail ? '产品详情' : currentPage.title}
              </h1>
            </div>
          </div>

          {/* 右侧：搜索和操作 */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* 搜索框 - 桌面端 */}
            <div className="hidden lg:block">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-content-muted" />
                <input
                  type="text"
                  placeholder={t('common.search')}
                  className="h-9 w-56 rounded-xl border border-surface-border bg-background-secondary pl-9 pr-4 text-sm text-content-primary placeholder:text-content-muted focus:border-brand-500/50 focus:outline-none focus:ring-2 focus:ring-brand-500/20 transition-all duration-150"
                />
              </div>
            </div>

            {/* 移动端搜索按钮 */}
            <button
              type="button"
              className="lg:hidden flex h-9 w-9 items-center justify-center rounded-lg text-content-muted hover:bg-surface hover:text-content-primary transition-colors"
              onClick={() => setSearchOpen(true)}
            >
              <Search className="h-4 w-4" />
            </button>

            {/* 语言切换 */}
            <LanguageSwitcher />

            {/* 主题切换 */}
            <ThemeSwitcher />

            {/* 数据状态指示器 - 仅桌面端 */}
            <div className="hidden md:flex items-center gap-2 rounded-full bg-accent-success/10 px-3 py-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-accent-success animate-pulse" />
              <span className="text-xs font-medium text-accent-success whitespace-nowrap">数据已同步</span>
            </div>
          </div>
        </div>
      </header>

      {/* 移动端搜索弹窗 */}
      {searchOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setSearchOpen(false)}
          />
          <div className="fixed left-4 right-4 top-4 rounded-2xl bg-background-secondary border border-surface-border p-4 animate-fade-in-down shadow-xl">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-content-muted" />
              <input
                type="text"
                placeholder={t('common.search')}
                autoFocus
                className="h-12 w-full rounded-xl border border-surface-border bg-background pl-10 pr-4 text-base text-content-primary placeholder:text-content-muted focus:border-brand-500/50 focus:outline-none focus:ring-2 focus:ring-brand-500/20 transition-all duration-150"
              />
            </div>
            <button
              type="button"
              className="mt-3 w-full rounded-xl bg-surface py-2.5 text-sm font-medium text-content-muted hover:bg-surface-hover hover:text-content-secondary transition-colors"
              onClick={() => setSearchOpen(false)}
            >
              取消
            </button>
          </div>
        </div>
      )}
    </>
  )
}
