'use client'

import { ThemeProvider } from 'next-themes'
import { ReactNode } from 'react'
import { SidebarProvider } from '@/contexts/SidebarContext'
import { LocaleProvider } from '@/contexts/LocaleContext'

interface ProvidersProps {
  children: ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem={false}
      disableTransitionOnChange
    >
      <LocaleProvider>
        <SidebarProvider>
          {children}
        </SidebarProvider>
      </LocaleProvider>
    </ThemeProvider>
  )
}
