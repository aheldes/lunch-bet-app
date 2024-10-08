'use client'
import { usePathname } from 'next/navigation'
import Body from './body'
import { RoomProvider } from '@/context/RoomContext'

const Home: React.FC = () => {
  const room_id = usePathname().split('/').filter(Boolean).pop()

  return (
    <main>
      {room_id ? (
        <RoomProvider room_id={room_id}>
          <Body />
        </RoomProvider>
      ) : (
        'Unexpected error'
      )}
    </main>
  )
}

export default Home
