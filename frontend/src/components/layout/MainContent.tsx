'use client'

import { ReactNode } from 'react'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useSidebar } from '@/contexts/SidebarContext'
import { useLocale } from '@/contexts/LocaleContext'
import { Header } from './Header'

interface MainContentProps {
  children: ReactNode
}

export function MainContent({ children }: MainContentProps) {
  const { isCollapsed } = useSidebar()
  const { t } = useLocale()
  const pathname = usePathname()

  // 助手页面使用特殊布局
  const isAssistantPage = pathname === '/assistant'

  return (
    <div
      className={cn(
        'flex flex-col min-h-screen transition-all duration-300',
        isCollapsed ? 'lg:pl-16' : 'lg:pl-56'
      )}
    >
      <Header />
      <main className={cn(
        'flex-1',
        isAssistantPage ? 'p-0 overflow-hidden' : 'p-6'
      )}>
        {children}
      </main>

      {/* 页脚 - 助手页面不显示 */}
      {!isAssistantPage && (
        <footer className="border-t border-surface-border bg-background-secondary/50 px-6 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-2 text-sm text-content-muted">
            <p>{t('common.dataSource')}</p>
            <p>{t('common.builtFor')}</p>
          </div>
        </footer>
      )}
    </div>
  )
}
