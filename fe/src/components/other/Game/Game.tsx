import PriceDialog from './PriceDialog'
import PricesPanel from './PricesPanel'

const Game: React.FC = () => {
  return (
    <div className="grid grid-cols-5 gap-2">
      <div className="col-span-4">
        <PriceDialog />
      </div>

      <PricesPanel />
    </div>
  )
}

export default Game
