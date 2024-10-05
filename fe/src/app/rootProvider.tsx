'use client'

import { ReactNode } from 'react'
import { UUIDProvider } from '@/context/UUIDContext'

interface RootProviderProps {
  readonly children: ReactNode
}

// RootProvider component
const RootProvider: React.FC<RootProviderProps> = ({ children }) => (
  <UUIDProvider>{children}</UUIDProvider>
)

export default RootProvider
