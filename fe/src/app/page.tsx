'use client'
import { useState } from 'react'
import useWebSocketRooms from '@/hooks/useWSRooms'
import useFetchRooms from '@/hooks/useFetchRooms'

import { RoomCard, RoomCardLoading } from '@/components/other/RoomCard'
import RoomCreateDialog from '@/components/other/RoomCreateDialog'

import { Room } from '@/types'

const Home: React.FC = () => {
  const [data, setData] = useState<Room[]>([])
  const { isLoading, isError } = useFetchRooms(setData)
  const socketError = useWebSocketRooms(setData)

  return (
    <div className="grid grid-rows-[20px_1fr_20px] justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2">
        <RoomCreateDialog />
        {isLoading &&
          Array(3)
            .fill(null)
            .map((_, index) => <RoomCardLoading key={index} />)}
        {data.map((room) => (
          <RoomCard key={room.id} {...room} />
        ))}
        {isError && 'error'}
      </main>
    </div>
  )
}

export default Home
