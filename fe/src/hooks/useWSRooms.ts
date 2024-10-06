import { useState } from 'react'
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

  const _ = useWebSocket(`${URL}/${uuid}`, {
    onMessage: (event) => {
      const roomUpdates = JSON.parse(event.data.replace(/'/g, '"'))

      const newRoom = parseRoomData([roomUpdates])
      setData((prevData) => [...newRoom, ...prevData])
    },
    onError: () => setError(true),
  })

  return error
}

export default useWebSocketRooms
