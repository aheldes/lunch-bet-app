import type { Room, RoomResponse } from '@/types'

const parseRoomData = (roomData: RoomResponse[]): Room[] => {
  return roomData.map((room) => ({
    id: room.id,
    name: room.name,
    created_by: room.created_by,
    created_at: new Date(room.created_at),
  }))
}

export default parseRoomData
