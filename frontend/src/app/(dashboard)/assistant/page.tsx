'use client'

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import AssistantChat from './AssistantChat'
import { Loader2 } from 'lucide-react'

function AssistantPageContent() {
  const searchParams = useSearchParams()
  const initialMessage = searchParams.get('message')
  
  return <AssistantChat initialMessage={initialMessage || undefined} />
}

export default function AssistantPage() {
  return (
    <Suspense fallback={
      <div className="h-[calc(100vh-3.5rem)] flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    }>
      <AssistantPageContent />
    </Suspense>
  )
}
