'use client'

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'

// Import translations
import zhCN from '../../messages/zh-CN.json'
import en from '../../messages/en.json'

export type Locale = 'zh-CN' | 'en'

const messages: Record<Locale, typeof zhCN> = {
  'zh-CN': zhCN,
  'en': en,
}

interface LocaleContextType {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: string) => string
  messages: typeof zhCN
}

const LocaleContext = createContext<LocaleContextType | undefined>(undefined)

const STORAGE_KEY = 'app-locale'

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('zh-CN')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(STORAGE_KEY) as Locale | null
      if (saved && (saved === 'zh-CN' || saved === 'en')) {
        setLocaleState(saved)
      }
    }
  }, [])

  useEffect(() => {
    if (mounted && typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, locale)
      // Update html lang attribute
      document.documentElement.lang = locale === 'zh-CN' ? 'zh-CN' : 'en'
    }
  }, [locale, mounted])

  const setLocale = useCallback((newLocale: Locale) => {
    setLocaleState(newLocale)
  }, [])

  // Translation function - supports nested keys like "nav.dashboard"
  const t = useCallback((key: string): string => {
    const keys = key.split('.')
    let value: unknown = messages[locale]

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = (value as Record<string, unknown>)[k]
      } else {
        return key // Return key if translation not found
      }
    }

    return typeof value === 'string' ? value : key
  }, [locale])

  return (
    <LocaleContext.Provider value={{ locale, setLocale, t, messages: messages[locale] }}>
      {children}
    </LocaleContext.Provider>
  )
}

export function useLocale() {
  const context = useContext(LocaleContext)
  if (!context) {
    throw new Error('useLocale must be used within LocaleProvider')
  }
  return context
}
