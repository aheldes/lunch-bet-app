import useRoomContext from '@/hooks/useRoomContext'

import PriceDialog from './PriceDialog'
import GameStateTitle from './GameStateTitle'
import GameStartButton from './GameStartButton'
import GameEvaluateButton from './GameEvaluateButton'
import BetDialog from './BetDialog'
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
