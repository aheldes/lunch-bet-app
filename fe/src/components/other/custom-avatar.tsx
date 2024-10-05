'use client'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'

import useUUIDContext from '@/hooks/useUUIDContext'

const CustomAvatar: React.FC = () => {
  const { uuid } = useUUIDContext()
  return (
    <Avatar>
      <AvatarImage
        src={`https://api.dicebear.com/9.x/fun-emoji/svg?seed=${uuid}`}
      />
      <AvatarFallback>CN</AvatarFallback>
    </Avatar>
  )
}

export default CustomAvatar
