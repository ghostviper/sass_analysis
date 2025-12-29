'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect } from 'react'
import { cn } from '@/lib/utils'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faChartLine,
  faLayerGroup,
  faBoxesStacked,
  faLightbulb,
  faCircleInfo,
  faRobot,
  faChevronLeft,
  faChevronRight,
  faXmark,
  faTrophy,
} from '@fortawesome/free-solid-svg-icons'
import { useSidebar } from '@/contexts/SidebarContext'
import { useLocale } from '@/contexts/LocaleContext'

export function Sidebar() {
  const pathname = usePathname()
  const { isCollapsed, isMobileOpen, toggleSidebar, closeMobile } = useSidebar()
  const { t } = useLocale()

  // Close mobile menu on route change
  useEffect(() => {
    closeMobile()
  }, [pathname, closeMobile])

  const navigation = [
    { name: t('nav.dashboard'), href: '/', icon: faChartLine },
    { name: t('nav.categories'), href: '/categories', icon: faLayerGroup },
    { name: t('nav.products'), href: '/products', icon: faBoxesStacked },
    { name: t('nav.leaderboard'), href: '/leaderboard', icon: faTrophy, isNew: true },
    { name: t('nav.assistant'), href: '/assistant', icon: faRobot },
  ]

  const secondaryNavigation = [
    { name: t('nav.about'), href: '/about', icon: faCircleInfo },
  ]

  const sidebarContent = (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div
        className={cn(
          'flex h-14 items-center transition-all duration-300',
          isCollapsed && !isMobileOpen ? 'justify-center px-2' : 'justify-between px-4'
        )}
      >
        <div className={cn('flex items-center gap-3', isCollapsed && !isMobileOpen && 'justify-center')}>
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-accent-primary to-accent-secondary">
            <FontAwesomeIcon icon={faLightbulb} className="h-4 w-4 text-white" />
          </div>
          {(!isCollapsed || isMobileOpen) && (
            <h1 className="font-display font-semibold text-content-primary whitespace-nowrap tracking-tight">
              {t('common.appName')}
            </h1>
          )}
        </div>

        {/* Desktop collapse button */}
        {!isCollapsed && !isMobileOpen && (
          <button
            onClick={toggleSidebar}
            className="hidden lg:flex h-6 w-6 items-center justify-center rounded text-content-muted hover:bg-surface hover:text-content-primary transition-colors"
          >
            <FontAwesomeIcon icon={faChevronLeft} className="h-3 w-3" />
          </button>
        )}

        {/* Mobile close button */}
        {isMobileOpen && (
          <button
            onClick={closeMobile}
            className="flex lg:hidden h-6 w-6 items-center justify-center rounded text-content-muted hover:bg-surface hover:text-content-primary transition-colors"
          >
            <FontAwesomeIcon icon={faXmark} className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Desktop expand button */}
      {isCollapsed && !isMobileOpen && (
        <div className="hidden lg:flex justify-center py-3">
          <button
            onClick={toggleSidebar}
            className="flex h-7 w-7 items-center justify-center rounded text-content-muted hover:bg-surface hover:text-content-primary transition-colors"
          >
            <FontAwesomeIcon icon={faChevronRight} className="h-3 w-3" />
          </button>
        </div>
      )}

      {/* 主导航 */}
      <nav className="flex-1 px-3 py-4">
        <div className="space-y-1.5">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
            const showCollapsed = isCollapsed && !isMobileOpen

            return (
              <Link
                key={item.name}
                href={item.href}
                title={showCollapsed ? item.name : undefined}
                className={cn(
                  'group relative flex items-center rounded-xl text-sm font-medium transition-colors',
                  showCollapsed ? 'justify-center p-3' : 'gap-3 px-3 py-3',
                  isActive
                    ? 'bg-accent-primary/10 text-accent-primary'
                    : 'text-content-secondary hover:bg-surface hover:text-content-primary'
                )}
              >
                <FontAwesomeIcon
                  icon={item.icon}
                  className={cn(
                    'h-[18px] w-[18px] shrink-0',
                    isActive ? 'text-accent-primary' : 'text-content-muted group-hover:text-content-secondary'
                  )}
                />
                {!showCollapsed && (
                  <span className="flex-1">{item.name}</span>
                )}
                {'isNew' in item && item.isNew && !showCollapsed && (
                  <span className="rounded bg-accent-primary/20 px-1.5 py-0.5 text-[10px] font-medium text-accent-primary">
                    NEW
                  </span>
                )}

                {/* Tooltip for desktop collapsed */}
                {showCollapsed && (
                  <div className="absolute left-full ml-2 hidden group-hover:block z-50">
                    <div className="whitespace-nowrap rounded-md bg-background-tertiary px-2.5 py-1.5 text-sm shadow-lg border border-surface-border text-content-primary">
                      {item.name}
                    </div>
                  </div>
                )}

                {/* NEW indicator for collapsed */}
                {showCollapsed && 'isNew' in item && item.isNew && (
                  <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-accent-primary" />
                )}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* 次级导航 */}
      <div className="border-t border-surface-border px-3 py-4">
        {secondaryNavigation.map((item) => {
          const isActive = pathname === item.href
          const showCollapsed = isCollapsed && !isMobileOpen

          return (
            <Link
              key={item.name}
              href={item.href}
              title={showCollapsed ? item.name : undefined}
              className={cn(
                'group relative flex items-center rounded-xl text-sm font-medium transition-colors',
                showCollapsed ? 'justify-center p-3' : 'gap-3 px-3 py-3',
                isActive
                  ? 'bg-surface text-content-primary'
                  : 'text-content-muted hover:bg-surface/50 hover:text-content-secondary'
              )}
            >
              <FontAwesomeIcon icon={item.icon} className="h-[18px] w-[18px] shrink-0" />
              {!showCollapsed && <span>{item.name}</span>}

              {showCollapsed && (
                <div className="absolute left-full ml-2 hidden group-hover:block z-50">
                  <div className="whitespace-nowrap rounded-md bg-background-tertiary px-2.5 py-1.5 text-sm shadow-lg border border-surface-border text-content-primary">
                    {item.name}
                  </div>
                </div>
              )}
            </Link>
          )
        })}
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-40 h-screen border-r border-surface-border bg-background-secondary/80 backdrop-blur-xl transition-all duration-300',
          'hidden lg:block',
          isCollapsed ? 'w-16' : 'w-56'
        )}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Sidebar Overlay */}
      {isMobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
            onClick={closeMobile}
          />

          {/* Sidebar */}
          <aside className="fixed left-0 top-0 h-screen w-64 border-r border-surface-border bg-background-secondary animate-slide-in-left">
            {sidebarContent}
          </aside>
        </div>
      )}
    </>
  )
}
