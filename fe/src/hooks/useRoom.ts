import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchActions } from '@/api/api'

import { toast } from 'sonner'

import type { Action, Currency, Event, Price } from '@/types'
import { RoomEventTypes } from '@/types'
import useUUIDContext from './useUUIDContext'

type RoomEventMessage = {
  type: RoomEventTypes
  user_id: string
  message: string
  price?: string
  currency?: Currency
}

const useRoom = (room_id: string) => {
  const { uuid } = useUUIDContext()
  const [users, setUsers] = useState<string[]>([])
  const [eventHistory, setEventHistory] = useState<Event[]>([])
  const [gameStarted, setGameStarted] = useState<boolean>(false)
  const [priceSet, setPriceSet] = useState<boolean>(false)
  const [prices, setPrices] = useState<Price[]>([])
  const gameReady = users.length === prices.length && users.length != 1
  const { data, isLoading, isError } = useQuery<Action[]>({
    queryKey: ['room', room_id],
    queryFn: () => fetchActions(room_id),
    staleTime: 5000,
  })

  const handleMessage = (data: RoomEventMessage, timestamp?: Date) => {
    // This check is needed as sometimes happened that WS connection got established before the data was fetched
    // and logged new event into redis and then rest fetched events including this one.
    if (
      eventHistory.some(
        (event) =>
          event.message === data.message &&
          event.timestamp.getTime() === timestamp?.getTime()
      )
    ) {
      return
    }
    setEventHistory((prevHistory) => [
      {
        timestamp: timestamp ? timestamp : new Date(),
        message: data.message,
      },
      ...prevHistory,
    ])

    switch (data.type) {
      case RoomEventTypes.JOIN:
        setUsers((prevUsers) => [...[data.user_id], ...prevUsers])
        toast('User Joined', {
          description: data.message,
        })
        break
      case RoomEventTypes.LEAVE:
        setUsers((prevUsers) =>
          prevUsers.filter((user) => user !== data.user_id)
        )
        setPrices((prevPrices) =>
          prevPrices.filter(
            (price) => price.user_id !== data.user_id || data.user_id === uuid
          )
        )
        toast('User Left', {
          description: data.message,
        })
        break
      case RoomEventTypes.GAME_START:
        setGameStarted(true)
        toast('Game started', {
          description: data.message,
        })
        break
      case RoomEventTypes.GAME_END:
        setGameStarted(false)
        toast('Game ended', {
          description: data.message,
        })
        break
      case RoomEventTypes.SET_PRICE:
        if (data.user_id === uuid) {
          setPriceSet(true) // Set priceSet to true when user already set price in the past
        }
        if (data.price !== undefined && data.currency !== undefined) {
          const price = data.price
          const currency = data.currency
          setPrices((prevPrices) => [
            {
              price: price,
              currency: currency,
              user_id: data.user_id,
            },
            ...prevPrices,
          ])
        } else {
          console.log('Unexpected error. Price or currency missing')
        }

        break

      default:
        console.error('Unknown message type:', data)
    }
  }

  const messageHandler = (message: string) => {
    try {
      const data: RoomEventMessage = JSON.parse(message)
      handleMessage(data)
    } catch (error) {
      console.error('Failed to parse message:', error)
    }
  }

  useEffect(() => {
    if (data) {
      data.forEach((action) => {
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
  }, [data])

  return { eventHistory, users, messageHandler, gameStarted, priceSet, prices }
}

export default useRoom
