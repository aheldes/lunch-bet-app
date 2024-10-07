import React, { createContext, useContext } from 'react'
import useRoom from '@/hooks/useRoom'
import useWebSocketRooms from '@/hooks/useWSRoom'
import { GameState, Price, Event } from '@/types'

export type RoomContextType = {
  room_id: string
  eventHistory: Event[]
  users: string[]
  gameState: GameState
  priceSet: boolean
  betSet: boolean
  prices: Price[]
  messageHandler: (message: string) => void
  sendJsonMessage: (message: any) => void
  result: string | null
  clearResult: () => void
}

export const RoomContext = createContext<RoomContextType | undefined>(undefined)

export const RoomProvider: React.FC<{
  room_id: string
  children: React.ReactNode
}> = ({ room_id, children }) => {
  const {
    eventHistory,
    users,
    messageHandler,
    gameState,
    priceSet,
    prices,
    betSet,
    result,
    clearResult,
  } = useRoom(room_id)
  const { sendJsonMessage } = useWebSocketRooms(room_id, messageHandler)

  const value = {
    room_id,
    eventHistory,
    users,
    gameState,
    priceSet,
    betSet,
    prices,
    messageHandler,
    sendJsonMessage,
    result,
    clearResult,
  }

  return <RoomContext.Provider value={value}>{children}</RoomContext.Provider>
}
