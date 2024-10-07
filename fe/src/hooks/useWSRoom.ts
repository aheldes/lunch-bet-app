import { useState } from 'react'
import useWebSocket from 'react-use-websocket'

import useUUIDContext from './useUUIDContext'

const URL = 'ws://127.0.0.1:8000/ws/room'

const useWebSocketRoom = (
  room_id: string,
  onMessageHandler: (message: string) => void
) => {
  const { uuid } = useUUIDContext()
  const [error, setError] = useState<boolean>(false)

  const { sendJsonMessage } = useWebSocket(`${URL}/${room_id}/${uuid}`, {
    onMessage: (event) => {
      onMessageHandler(event.data)
    },
    onError: () => setError(true),
  })

  return { error, sendJsonMessage }
}

export default useWebSocketRoom
