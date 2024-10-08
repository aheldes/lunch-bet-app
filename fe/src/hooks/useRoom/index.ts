import { useEffect, useState } from 'react'

import useUUIDContext from '@/hooks/useUUIDContext'
import useFetchRoomData from './useFetchRoomData'
import useGameState from './useGameState'
import useRoomEventHandler from './useRoomEventHandler'

import type { RoomEventMessage } from './useRoomEventHandler'
import { RoomEventTypes } from '@/types'

const useRoom = (room_id: string) => {
  const { uuid } = useUUIDContext()

  const [users, setUsers] = useState<string[]>([])

  const {
    actionsData,
    actionsLoading,
    actionsError,
    historyData,
    historyLoading,
    historyError,
    refetchHistory,
  } = useFetchRoomData(room_id)

  const {
    betSet,
    eventHistory,
    gameState,
    prices,
    priceSet,
    result,
    setBets,
    setBetSet,
    setEventHistory,
    setGameState,
    setPrices,
    setPriceSet,
    setResult,
    clearResult,
    resetGame,
  } = useGameState(users)

  const handleResult = (message: string) => {
    resetGame()
    setResult(message)
    refetchHistory()
  }

  const handleMessage = useRoomEventHandler(
    eventHistory,
    setBets,
    setBetSet,
    setEventHistory,
    setGameState,
    setUsers,
    setPrices,
    setPriceSet,
    handleResult,
    uuid
  )

  const messageHandler = (message: string) => {
    try {
      const data = JSON.parse(message)
      handleMessage(data)
    } catch (error) {
      console.error('Failed to parse message:', error)
    }
  }

  useEffect(() => {
    if (actionsData) {
      actionsData.forEach((action) => {
        const parsedAction: RoomEventMessage = {
          type: action.action as RoomEventTypes,
          user_id: action.user_id,
          message: action.message,
          price: action.price,
          currency: action.currency,
        }
        handleMessage(parsedAction, new Date(action.timestamp))
      })
    }
  }, [actionsData])

  return {
    eventHistory,
    users,
    messageHandler,
    gameState,
    priceSet,
    prices,
    betSet,
    result,
    clearResult,
    historyData,
  }
}

export default useRoom
