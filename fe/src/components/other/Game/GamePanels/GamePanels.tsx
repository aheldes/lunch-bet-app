import EventPanel from './EventPanel'
import UserPanel from './UserPanel'
import PricesPanel from './PricesPanel'

const GamePanels: React.FC = () => {
  return (
    <>
      <PricesPanel />
      <EventPanel className="col-span-6" />
      <UserPanel />
    </>
  )
}

export default GamePanels
