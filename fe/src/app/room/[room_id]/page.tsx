'use client'
import { usePathname } from 'next/navigation'
import Body from './body'

const Home: React.FC = () => {
  const room_id = usePathname().split('/').filter(Boolean).pop()

  return <main>{room_id ? <Body room_id={room_id} /> : 'error'}</main>
}

export default Home
