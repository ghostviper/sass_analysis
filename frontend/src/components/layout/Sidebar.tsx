'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useEffect, useState, useRef } from 'react'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Layers,
  Package,
  Trophy,
  Bot,
  X,
  Settings,
  HelpCircle,
  LogOut,
  Gem,
  ChevronUp,
  Lightbulb,
  PanelLeftClose,
  PanelLeft,
} from 'lucide-react'
import { useSidebar } from '@/contexts/SidebarContext'
import { useLocale } from '@/contexts/LocaleContext'

export function Sidebar() {
  const pathname = usePathname()
  const { isCollapsed, isMobileOpen, toggleSidebar, closeMobile } = useSidebar()
  const { t } = useLocale()
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const userMenuRef = useRef<HTMLDivElement>(null)

  // Close mobile menu on route change
  useEffect(() => {
    closeMobile()
  }, [pathname, closeMobile])

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const navigation = [
    { name: t('nav.dashboard'), href: '/', icon: LayoutDashboard },
    { name: t('nav.categories'), href: '/categories', icon: Layers },
    { name: t('nav.products'), href: '/products', icon: Package },
    { name: t('nav.leaderboard'), href: '/leaderboard', icon: Trophy, isNew: true },
    { name: t('nav.assistant'), href: '/assistant', icon: Bot },
  ]

  const userMenuItems = [
    { name: t('nav.settings') || 'Settings', icon: Settings, href: '/settings' },
    { name: t('nav.help') || 'Help', icon: HelpCircle, href: '/about' },
    { name: t('nav.upgrade') || 'Upgrade', icon: Gem, action: 'upgrade' },
    { name: t('nav.logout') || 'Logout', icon: LogOut, action: 'logout' },
  ]

  const sidebarContent = (
    <div className="flex h-full flex-col">
      {/* Logo and Toggle - 与 Header 高度一致 h-14，下方有分割线 */}
      <div
        className={cn(
          'flex h-14 items-center border-b border-surface-border transition-all duration-300',
          isCollapsed && !isMobileOpen ? 'justify-center px-2' : 'justify-between px-4'
        )}
      >
        {/* Collapsed: Show toggle button in logo position */}
        {isCollapsed && !isMobileOpen ? (
          <button
            onClick={toggleSidebar}
            className="hidden lg:flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-brand text-white hover:opacity-90 transition-opacity shadow-sm"
            title={t('nav.expandMenu') || 'Expand menu'}
          >
            <PanelLeft className="h-5 w-5" />
          </button>
        ) : (
          <>
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-brand shadow-sm">
                <Lightbulb className="h-4 w-4 text-white" />
              </div>
              <h1
                className={cn(
                  'font-display font-semibold text-content-primary whitespace-nowrap tracking-tight transition-all duration-300 overflow-hidden',
                  isCollapsed && !isMobileOpen ? 'w-0 opacity-0' : 'w-auto opacity-100'
                )}
              >
                {t('common.appName')}
              </h1>
            </div>

            {/* Desktop collapse button */}
            {!isMobileOpen && (
              <button
                onClick={toggleSidebar}
                className="hidden lg:flex h-8 w-8 items-center justify-center rounded-lg text-content-muted hover:bg-surface hover:text-content-primary transition-colors"
                title={t('nav.collapseMenu') || 'Collapse menu'}
              >
                <PanelLeftClose className="h-5 w-5" />
              </button>
            )}

            {/* Mobile close button */}
            {isMobileOpen && (
              <button
                onClick={closeMobile}
                className="flex lg:hidden h-8 w-8 items-center justify-center rounded-lg text-content-muted hover:bg-surface hover:text-content-primary transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </>
        )}
      </div>

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
                  'group relative flex items-center rounded-xl text-sm font-medium transition-all duration-200',
                  showCollapsed ? 'justify-center p-3' : 'gap-3 px-3 py-3',
                  isActive
                    ? 'bg-brand-50 text-brand-600 dark:bg-brand-950/50 dark:text-brand-400'
                    : 'text-content-secondary hover:bg-surface hover:text-content-primary'
                )}
              >
                <item.icon
                  className={cn(
                    'h-[18px] w-[18px] shrink-0 transition-all duration-200',
                    isActive ? 'text-brand-600 dark:text-brand-400' : 'text-content-muted group-hover:text-content-secondary'
                  )}
                />
                <span
                  className={cn(
                    'whitespace-nowrap transition-all duration-300 overflow-hidden',
                    showCollapsed ? 'w-0 opacity-0' : 'w-auto opacity-100 flex-1'
                  )}
                >
                  {item.name}
                </span>
                {'isNew' in item && item.isNew && (
                  <span
                    className={cn(
                      'rounded-md bg-brand-500/15 px-1.5 py-0.5 text-[10px] font-semibold text-brand-600 dark:text-brand-400 whitespace-nowrap transition-all duration-200',
                      showCollapsed ? 'hidden' : 'block'
                    )}
                  >
                    NEW
                  </span>
                )}

                {/* Tooltip for desktop collapsed */}
                {showCollapsed && (
                  <div className="absolute left-full ml-2 hidden group-hover:block z-50">
                    <div className="whitespace-nowrap rounded-lg bg-surface-elevated px-3 py-2 text-sm shadow-lg border border-surface-border text-content-primary">
                      {item.name}
                    </div>
                  </div>
                )}

                {/* NEW indicator for collapsed */}
                {showCollapsed && 'isNew' in item && item.isNew && (
                  <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-brand-500" />
                )}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* User Profile Section */}
      <div className="px-3 py-2" ref={userMenuRef}>
        <div className="relative">
          <button
            onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            className={cn(
              'group relative flex w-full items-center rounded-xl transition-all duration-200',
              isCollapsed && !isMobileOpen ? 'justify-center p-2' : 'gap-2.5 px-2 py-1.5',
              'hover:bg-surface/80'
            )}
          >
            {/* Avatar */}
            <div className="relative shrink-0">
              <div className="h-8 w-8 rounded-lg bg-gradient-brand flex items-center justify-center text-white text-xs font-semibold shadow-sm">
                U
              </div>
              {/* Online indicator */}
              <span className="absolute -bottom-0.5 -right-0.5 h-2 w-2 rounded-full bg-accent-success border-2 border-background-secondary" />
            </div>

            {/* User info - only show when expanded */}
            <div
              className={cn(
                'flex items-center gap-2 transition-all duration-300 overflow-hidden min-w-0',
                isCollapsed && !isMobileOpen ? 'w-0 opacity-0' : 'w-auto opacity-100 flex-1'
              )}
            >
              <div className="flex-1 text-left min-w-0">
                <p className="text-sm font-medium text-content-primary truncate whitespace-nowrap leading-tight">
                  {t('nav.user') || 'User'}
                </p>
                <p className="text-[11px] text-content-muted truncate whitespace-nowrap leading-tight">
                  {t('nav.freeplan') || 'Free Plan'}
                </p>
              </div>
              <ChevronUp
                className={cn(
                  'h-3.5 w-3.5 text-content-muted transition-transform duration-200 shrink-0',
                  isUserMenuOpen && 'rotate-180'
                )}
              />
            </div>

            {/* Tooltip for collapsed state */}
            {isCollapsed && !isMobileOpen && (
              <div className="absolute left-full ml-2 hidden group-hover:block z-50">
                <div className="whitespace-nowrap rounded-xl bg-surface-elevated px-3 py-2 text-sm shadow-lg border border-surface-border">
                  <p className="font-medium text-content-primary">{t('nav.user') || 'User'}</p>
                  <p className="text-xs text-content-muted">{t('nav.freeplan') || 'Free Plan'}</p>
                </div>
              </div>
            )}
          </button>

          {/* Dropdown Menu */}
          {isUserMenuOpen && (
            <div
              className={cn(
                'absolute z-50 rounded-2xl border border-surface-border bg-surface-elevated shadow-xl overflow-hidden',
                isCollapsed && !isMobileOpen
                  ? 'left-full bottom-0 ml-2 w-52'
                  : 'left-0 right-0 bottom-full mb-2'
              )}
            >
              {/* User info header in dropdown */}
              <div className="px-4 py-3 border-b border-surface-border bg-surface/50">
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-xl bg-gradient-brand flex items-center justify-center text-white text-sm font-semibold shadow-sm">
                    U
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-content-primary truncate">
                      {t('nav.user') || 'User'}
                    </p>
                    <p className="text-xs text-content-muted truncate">
                      {t('nav.freeplan') || 'Free Plan'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="py-1.5">
                {userMenuItems.map((item, index) => {
                  const isLastItem = index === userMenuItems.length - 1

                  if (item.href) {
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        onClick={() => setIsUserMenuOpen(false)}
                        className={cn(
                          'flex items-center gap-3 px-4 py-2.5 text-sm transition-colors',
                          'text-content-secondary hover:bg-surface hover:text-content-primary',
                          isLastItem && 'border-t border-surface-border mt-1 pt-2.5 text-accent-error hover:text-accent-error hover:bg-accent-error/5'
                        )}
                      >
                        <item.icon className="h-4 w-4" />
                        <span>{item.name}</span>
                      </Link>
                    )
                  }

                  return (
                    <button
                      key={item.name}
                      onClick={() => {
                        setIsUserMenuOpen(false)
                        if (item.action === 'logout') {
                          console.log('Logout clicked')
                        } else if (item.action === 'upgrade') {
                          console.log('Upgrade clicked')
                        }
                      }}
                      className={cn(
                        'flex w-full items-center gap-3 px-4 py-2.5 text-sm transition-colors',
                        'text-content-secondary hover:bg-surface hover:text-content-primary',
                        item.action === 'logout' && 'border-t border-surface-border mt-1 pt-2.5 text-accent-error hover:text-accent-error hover:bg-accent-error/5',
                        item.action === 'upgrade' && 'text-brand-600 dark:text-brand-400 hover:text-brand-600 hover:bg-brand-500/5'
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      <span className="flex-1 text-left">{item.name}</span>
                      {item.action === 'upgrade' && (
                        <span className="rounded-md bg-brand-500/15 px-2 py-0.5 text-[10px] font-semibold text-brand-600 dark:text-brand-400">
                          PRO
                        </span>
                      )}
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>
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
