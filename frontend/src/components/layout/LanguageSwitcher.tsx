'use client'

import { useLocale, Locale } from '@/contexts/LocaleContext'
import { cn } from '@/lib/utils'
import { Globe, Check } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'

const languages: { code: Locale; label: string; flag: string }[] = [
  { code: 'zh-CN', label: '简体中文', flag: '🇨🇳' },
  { code: 'en', label: 'English', flag: '🇺🇸' },
]

export function LanguageSwitcher() {
  const { locale, setLocale } = useLocale()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const currentLang = languages.find((l) => l.code === locale)

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex h-9 w-9 items-center justify-center rounded-lg text-content-muted hover:text-content-secondary hover:bg-surface/50 transition-colors"
        title={currentLang?.label}
      >
        <Globe className="w-[18px] h-[18px]" />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-40 rounded-lg border border-surface-border bg-background-secondary shadow-lg z-50">
          <div className="py-1">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  setLocale(lang.code)
                  setIsOpen(false)
                }}
                className={cn(
                  'w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors',
                  locale === lang.code
                    ? 'bg-accent-primary/10 text-accent-primary'
                    : 'text-content-secondary hover:bg-surface hover:text-content-primary'
                )}
              >
                <span className="text-base">{lang.flag}</span>
                <span className="flex-1 text-left">{lang.label}</span>
                {locale === lang.code && (
                  <Check className="w-3.5 h-3.5" />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
