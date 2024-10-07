import { SendJsonMessage } from 'react-use-websocket/dist/lib/types'
import PriceDialog from './PriceDialog'
import PricesPanel from './PricesPanel'

import type { Price } from '@/types'

type GameProps = {
  priceSet: boolean
  prices: Price[]
  sendJsonMessage: SendJsonMessage
}

const Game: React.FC<GameProps> = ({ priceSet, sendJsonMessage, prices }) => {
  return (
    <div className="grid grid-cols-5 gap-2">
      <div className="col-span-4">
        <PriceDialog priceSet={priceSet} sendJsonMessage={sendJsonMessage} />
      </div>

      <PricesPanel prices={prices} />
    </div>
  )
}

export default Game
