import { toast } from 'sonner'
import { Currency, Event, GameState, Price, RoomEventTypes } from '@/types'

type RoomEventMessage = {
  type: RoomEventTypes
  user_id: string
  message: string
  price?: string
  currency?: Currency
}

const useRoomEventHandler = (
  eventHistory: Event[],
  setBets: React.Dispatch<React.SetStateAction<string[]>>,
  setBetSet: React.Dispatch<React.SetStateAction<boolean>>,
  setEventHistory: React.Dispatch<React.SetStateAction<Event[]>>,
  setGameState: React.Dispatch<React.SetStateAction<GameState>>,
  setUsers: React.Dispatch<React.SetStateAction<string[]>>,
  setPrices: React.Dispatch<React.SetStateAction<Price[]>>,
  setPriceSet: React.Dispatch<React.SetStateAction<boolean>>,
  handleResult: (message: string) => void,
  uuid: string | null
) => {
  const handleMessage = (data: RoomEventMessage, timestamp?: Date) => {
    // This check is needed as sometimes happened that WS connection got established before the data was fetched
    // and logged new event into redis and then rest fetched events including this one.
    if (
      eventHistory.some(
        (event) =>
          event.message === data.message &&
          Math.abs(event.timestamp.getTime() - (timestamp?.getTime() || 0)) <
            1000
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
        setGameState(GameState.STARTED)
        toast('Game started', {
          description: data.message,
        })
        break
      case RoomEventTypes.GAME_END:
        setGameState(GameState.IDLE)
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
      case RoomEventTypes.SET_BET:
        if (data.user_id === uuid) {
          setBetSet(true)
        }
        setBets((prevBets) => [...[data.user_id], ...prevBets])
        break
      case RoomEventTypes.RESULT:
        handleResult(data.message)
        break
      default:
        console.error('Unknown message type:', data)
    }
  }

  return handleMessage
}

export default useRoomEventHandler
