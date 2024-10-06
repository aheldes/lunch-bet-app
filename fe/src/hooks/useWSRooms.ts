import { useEffect, useState } from 'react'
import useWebSocket from 'react-use-websocket'

import parseRoomData from '@/utils/parseRoomData'

import { Room } from '@/types'
import useUUIDContext from './useUUIDContext'

const URL = 'ws://127.0.0.1:8000/ws/rooms'

const useWebSocketRooms = (
  setData: React.Dispatch<React.SetStateAction<Room[]>>
) => {
  const { uuid } = useUUIDContext()
  const [error, setError] = useState<boolean>(false)

  const { lastMessage } = useWebSocket(`${URL}/${uuid}`, {
    onMessage: (message) => {
      if (message !== null) {
        const roomUpdates = JSON.parse(message.data.replace(/'/g, '"'))

        const newRoom = parseRoomData([roomUpdates])
        setData((prevData) => [...newRoom, ...prevData])
      }
    },
    onError: () => setError(true),
  })

  useEffect(() => {
    if (lastMessage !== null) {
      const roomUpdates = JSON.parse(lastMessage.data.replace(/'/g, '"'))

      const newRoom = parseRoomData([roomUpdates])
      setData((prevData) => [...newRoom, ...prevData])
    }
  }, [lastMessage])

  return error
}

export default useWebSocketRooms
