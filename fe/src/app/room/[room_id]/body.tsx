'use client'

import useRoom from '@/hooks/useRoom'
import useWebSocketRooms from '@/hooks/useWSRoom'

import EventPanel from '@/components/other/EventPanel'
import UserPanel from '@/components/other/UserPanel'

type BodyProps = {
  room_id: string
}

const Body: React.FC<BodyProps> = ({ room_id }) => {
  const { eventHistory, users, messageHandler } = useRoom(room_id)
  const error = useWebSocketRooms(room_id, messageHandler)

  return (
    <div className="flex flex-col h-screen">
      {' '}
      <div className="grid grid-cols-12 gap-2 px-3 flex-1">
        <div className="col-span-7"></div>
        <EventPanel events={eventHistory} className="col-span-4" />
        <UserPanel users={users} />
      </div>
      <div className="h-1/3">History placeholder</div>
    </div>
  )
}

export default Body
