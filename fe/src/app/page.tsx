'use client'

import useWebSocketRooms from '@/hooks/useWSRooms'

import RoomCard from '@/components/other/room-card'

const URL = 'ws://127.0.0.1:8000/ws/rooms'

const Home: React.FC = () => {
  const { data, error } = useWebSocketRooms()

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        {data.map((room) => (
          <RoomCard key={room.id} {...room} />
        ))}
        {error ? 'error' : 'no error'}
      </main>
    </div>
  )
}

export default Home
