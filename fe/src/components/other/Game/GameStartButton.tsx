'use client'
import useUUIDContext from '@/hooks/useUUIDContext'
import { Button } from '@/components/ui/button'
import type { SendJsonMessage } from 'react-use-websocket/dist/lib/types'
import { RoomEventTypes } from '@/types'

type GameStartButtonProps = {
  sendJsonMessage: SendJsonMessage
}

const GameStartButton: React.FC<GameStartButtonProps> = ({
  sendJsonMessage,
}) => {
  const { uuid } = useUUIDContext()
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
