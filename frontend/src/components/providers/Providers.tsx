'use client'

import { ThemeProvider } from 'next-themes'
import { ReactNode } from 'react'
import { SidebarProvider } from '@/contexts/SidebarContext'
import { LocaleProvider } from '@/contexts/LocaleContext'
import { AuthProvider } from '@/components/auth/AuthProvider'

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
      <AuthProvider>
        <LocaleProvider>
          <SidebarProvider>
            {children}
          </SidebarProvider>
        </LocaleProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}
