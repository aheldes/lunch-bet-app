import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchActions } from '@/api/api'

import { toast } from 'sonner'

import type { Action, Event } from '@/types'
import { ActionTypes } from '@/types'

type RoomMessage = {
  type: ActionTypes
  user_id: string
  message: string
}

const useRoom = (room_id: string) => {
  const [users, setUsers] = useState<string[]>([])
  const [eventHistory, setEventHistory] = useState<Event[]>([])
  const { data, isLoading, isError } = useQuery<Action[]>({
    queryKey: ['room', room_id],
    queryFn: () => fetchActions(room_id),
    staleTime: 5000,
  })

  const handleMessage = (data: RoomMessage, timestamp?: Date) => {
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
      case ActionTypes.JOIN:
        setUsers((prevUsers) => [...[data.user_id], ...prevUsers])
        toast('User Joined', {
          description: data.message,
        })
        break

      case ActionTypes.LEAVE:
        setUsers((prevUsers) =>
          prevUsers.filter((user) => user !== data.user_id)
        )
        toast('User Left', {
          description: data.message,
        })
        break

      default:
        console.error('Unknown message type:', data)
    }
  }

  const messageHandler = (message: string) => {
    try {
      const data: RoomMessage = JSON.parse(message)
      handleMessage(data)
    } catch (error) {
      console.error('Failed to parse message:', error)
    }
  }

  useEffect(() => {
    if (data) {
      data.forEach((action) => {
        const parsedAction: RoomMessage = {
          type: action.action as ActionTypes,
          user_id: action.user_id,
          message: action.message,
        }

        handleMessage(parsedAction, new Date(action.timestamp))
      })
    }
  }, [data])

  return { eventHistory, users, messageHandler }
}

export default useRoom
