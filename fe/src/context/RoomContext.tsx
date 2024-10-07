import React, { createContext, useContext } from 'react'
import useRoom from '@/hooks/useRoom'
import useWebSocketRooms from '@/hooks/useWSRoom'
import { Price, Event } from '@/types'

export type RoomContextType = {
  room_id: string
  eventHistory: Event[]
  users: string[]
  gameStarted: boolean
  priceSet: boolean
  prices: Price[]
  messageHandler: (message: string) => void
  sendJsonMessage: (message: any) => void
}

export const RoomContext = createContext<RoomContextType | undefined>(undefined)

export const RoomProvider: React.FC<{
  room_id: string
  children: React.ReactNode
}> = ({ room_id, children }) => {
  const { eventHistory, users, messageHandler, gameStarted, priceSet, prices } =
    useRoom(room_id)
  const { sendJsonMessage } = useWebSocketRooms(room_id, messageHandler)

  const value = {
    room_id,
    eventHistory,
    users,
    gameStarted,
    priceSet,
    prices,
    messageHandler,
    sendJsonMessage,
  }

  return <RoomContext.Provider value={value}>{children}</RoomContext.Provider>
}
