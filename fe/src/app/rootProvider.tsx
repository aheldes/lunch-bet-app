'use client'

import { ReactNode } from 'react'
import { UUIDProvider } from '@/context/UUIDContext'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

interface RootProviderProps {
  readonly children: ReactNode
}

const queryClient = new QueryClient()

const RootProvider: React.FC<RootProviderProps> = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    <UUIDProvider>{children}</UUIDProvider>
  </QueryClientProvider>
)

export default RootProvider
