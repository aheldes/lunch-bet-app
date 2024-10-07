'use client'
import useUUIDContext from '@/hooks/useUUIDContext'
import useRoomContext from '@/hooks/useRoomContext'

import { Button } from '@/components/ui/button'

import { RoomEventTypes } from '@/types'

const GameStartButton: React.FC = () => {
  const { uuid } = useUUIDContext()
  const { sendJsonMessage } = useRoomContext()
  const onStartGame = () => {
    if (!uuid) return
    const message = {
      type: RoomEventTypes.GAME_START,
      user_id: uuid,
    }
    sendJsonMessage(message)
  }
  return <Button onClick={onStartGame}>Start game</Button>
}

export default GameStartButton
