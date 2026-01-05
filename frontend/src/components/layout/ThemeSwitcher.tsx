'use client'

import { useTheme } from 'next-themes'
import { useEffect, useState, useCallback, useRef } from 'react'
import { Sun, Moon } from 'lucide-react'
import { createPortal } from 'react-dom'

export function ThemeSwitcher() {
  const { setTheme, resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const [isAnimating, setIsAnimating] = useState(false)
  const [overlayTheme, setOverlayTheme] = useState<'light' | 'dark' | null>(null)
  const [expanded, setExpanded] = useState(false)
  const [fading, setFading] = useState(false)
  const timeoutRefs = useRef<NodeJS.Timeout[]>([])

  useEffect(() => {
    setMounted(true)
    return () => {
      timeoutRefs.current.forEach(clearTimeout)
    }
  }, [])

  const handleThemeToggle = useCallback(() => {
    if (isAnimating) return

    const newTheme = resolvedTheme === 'dark' ? 'light' : 'dark'

    // Clear any existing timeouts
    timeoutRefs.current.forEach(clearTimeout)
    timeoutRefs.current = []

    // Step 1: Show overlay at initial state (circle at 0%)
    setOverlayTheme(newTheme)
    setExpanded(false)
    setFading(false)
    setIsAnimating(true)

    // Step 2: Trigger expansion (need a frame delay for CSS transition to work)
    timeoutRefs.current.push(setTimeout(() => {
      setExpanded(true)
    }, 20))

    // Step 3: Switch theme when overlay covers the screen
    timeoutRefs.current.push(setTimeout(() => {
      setTheme(newTheme)
    }, 350))

    // Step 4: Start fading out
    timeoutRefs.current.push(setTimeout(() => {
      setFading(true)
    }, 450))

    // Step 5: Clean up
    timeoutRefs.current.push(setTimeout(() => {
      setIsAnimating(false)
      setOverlayTheme(null)
      setExpanded(false)
      setFading(false)
    }, 650))
  }, [isAnimating, resolvedTheme, setTheme])

  if (!mounted) {
    return (
      <button
        className="flex h-9 w-9 items-center justify-center rounded-lg text-content-muted"
        aria-label="Toggle theme"
      >
        <div className="w-[18px] h-[18px]" />
      </button>
    )
  }

  const isDark = resolvedTheme === 'dark'

  // Calculate position based on viewport
  const circleOrigin = 'calc(100% - 3rem) 1.75rem'

  return (
    <>
      <button
        onClick={handleThemeToggle}
        className="flex h-9 w-9 items-center justify-center rounded-lg text-content-muted hover:text-content-primary hover:bg-surface/50 transition-colors"
        aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
        title={isDark ? '切换到浅色模式' : '切换到深色模式'}
      >
        {isDark ? (
          <Sun className="w-[18px] h-[18px]" />
        ) : (
          <Moon className="w-[18px] h-[18px]" />
        )}
      </button>

      {/* Theme transition overlay */}
      {isAnimating && overlayTheme && typeof window !== 'undefined' && createPortal(
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 99999,
            pointerEvents: 'none',
            background: overlayTheme === 'dark' ? '#0f172a' : '#ffffff',
            clipPath: expanded
              ? `circle(150% at ${circleOrigin})`
              : `circle(0% at ${circleOrigin})`,
            opacity: fading ? 0 : 1,
            transition: fading
              ? 'opacity 0.2s ease-out'
              : 'clip-path 0.4s cubic-bezier(0.22, 1, 0.36, 1)',
          }}
        />,
        document.body
      )}
    </>
  )
}
