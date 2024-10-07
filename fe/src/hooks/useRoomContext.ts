import { useContext } from 'react'
import { RoomContext } from '@/context/RoomContext'
import type { RoomContextType } from '@/context/RoomContext'

export const useRoomContext = (): RoomContextType => {
  const context = useContext(RoomContext)
  if (!context) {
    throw new Error('useRoomContext must be used within a RoomProvider')
  }
  return context
}

export default useRoomContext
