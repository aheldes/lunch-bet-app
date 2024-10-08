import useRoomContext from '@/hooks/useRoomContext'

import PriceDialog from './GameStateLogic/PriceDialog'
import GameStateTitle from './GameStateLogic/GameStateTitle'
import GameStartButton from './GameStateLogic/GameStartButton'
import GameEvaluateButton from './GameStateLogic/GameEvaluateButton'
import BetDialog from './GameStateLogic/BetDialog'
import { GameState } from '@/types'

const Game: React.FC = () => {
  const { gameState } = useRoomContext()
  let title: string
  let content: JSX.Element

  switch (gameState) {
    case GameState.IDLE:
      title = 'Start Game'
      content = <GameStartButton />
      break
    case GameState.STARTED:
      title = 'Set Price'
      content = <PriceDialog />
      break
    case GameState.PRICES_SET:
      title = 'Set Bets'
      content = <BetDialog />
      break
    case GameState.BETS_SET:
      title = 'Evaluate'
      content = <GameEvaluateButton />
      break
    default:
      title = 'Unknown State'
      content = <div>Error: Unknown game state.</div>
  }
  return (
    <div className="flex gap-2">
      <GameStateTitle title={title} />
      {content}
    </div>
  )
}

export default Game
