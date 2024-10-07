import useRoomContext from '@/hooks/useRoomContext'

import PriceDialog from './PriceDialog'
import PricesPanel from './PricesPanel'
import GameStateTitle from './GameStateTitle'
import GameStartButton from './GameStartButton'
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
      title = 'Evaluating'
      content = <div>...</div>
      break

    default:
      title = 'Unknown State'
      content = <div>Error: Unknown game state.</div>
  }
  return (
    <div className="grid grid-cols-5 gap-2">
      <div className="col-span-4">
        <GameStateTitle title={title} />
        {content}
      </div>

      <PricesPanel />
    </div>
  )
}

export default Game
