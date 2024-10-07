'use client'

import EventPanel from '@/components/other/EventPanel'
import UserPanel from '@/components/other/UserPanel'
import { Game } from '@/components/other/Game'

const Body: React.FC = () => {
  return (
    <div className="flex flex-col h-screen">
      {' '}
      <div className="grid grid-cols-12 gap-2 px-3 flex-1">
        <div className="col-span-7">
          <Game />
        </div>
        <EventPanel className="col-span-4" />
        <UserPanel />
      </div>
      <div className="h-1/3">History placeholder</div>
    </div>
  )
}

export default Body
