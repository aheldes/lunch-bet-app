'use client'

import { createContext, useState, useEffect, ReactNode, FC } from 'react'
import { v4 as uuidv4 } from 'uuid'

interface UUIDContextType {
  uuid: string | null
}

const UUIDContext = createContext<UUIDContextType | undefined>(undefined)

interface UUIDProviderProps {
  children: ReactNode
}

export const UUIDProvider: FC<UUIDProviderProps> = ({ children }) => {
  const [uuid, setUuid] = useState<string | null>(null)

  useEffect(() => {
    const storedUUID = localStorage.getItem('user-uuid')
    if (storedUUID) {
      setUuid(storedUUID)
    } else {
      const newUUID = uuidv4()
      localStorage.setItem('user-uuid', newUUID)
      setUuid(newUUID)
    }
  }, [])

  return (
    <UUIDContext.Provider value={{ uuid }}>{children}</UUIDContext.Provider>
  )
}

export default UUIDContext
