import { useState } from 'react'
import useWebSocket from 'react-use-websocket'
import { Room } from '@/types'

const parseRoomData = (roomData: any[]): Room[] => {
  return roomData.map((room) => ({
    id: room.id,
    name: room.name,
    created_by: room.created_by,
    created_at: new Date(room.created_at),
  }))
}

const URL = 'ws://127.0.0.1:8000/ws/rooms'

const useWebSocketRooms = () => {
  const [data, setData] = useState<Room[]>([])
  const [error, setError] = useState<boolean>(false)

  const _ = useWebSocket(URL, {
    onMessage: (event) => {
      const roomUpdates = JSON.parse(event.data.replace(/'/g, '"'))

      if (Array.isArray(roomUpdates)) {
        const parsedRooms = parseRoomData(roomUpdates)
        setData(parsedRooms)
      } else {
        const newRoom = parseRoomData([roomUpdates])
        setData((prevData) => [...prevData, ...newRoom])
      }
    },
    onError: () => setError(true),
  })

  return { data, error }
}

export default useWebSocketRooms
