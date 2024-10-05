'use client'

import { useContext } from 'react'
import UUIDContext from '@/context/UUIDContext'

const useUUIDContext = () => {
  const context = useContext(UUIDContext)

  if (!context) {
    throw new Error('useUUIDContext must be used within a UUIDProvider')
  }

  return context
}

export default useUUIDContext
