'use client'
import useUUIDContext from '@/hooks/useUUIDContext'
import useRoomContext from '@/hooks/useRoomContext'

import { Button } from '@/components/ui/button'

import { RoomEventTypes } from '@/types'

const GameEvaluateButton: React.FC = () => {
  const { uuid } = useUUIDContext()
  const { sendJsonMessage } = useRoomContext()
  const evaluateGame = () => {
    if (!uuid) return
    const message = {
      type: RoomEventTypes.EVALUATE,
      user_id: uuid,
    }
    sendJsonMessage(message)
  }
  return <Button onClick={evaluateGame}>Evaluate game</Button>
}

export default GameEvaluateButton
