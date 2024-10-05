'use client'

import useWebSocketRooms from '@/hooks/useWSRooms'

const URL = 'ws://127.0.0.1:8000/ws/rooms'

export default function Home() {
  const { data, error } = useWebSocketRooms()

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        {data.map((room) => (
          <li key={room.id}>{room.name}</li>
        ))}
        {error ? 'error' : 'no error'}
      </main>
    </div>
  )
}
