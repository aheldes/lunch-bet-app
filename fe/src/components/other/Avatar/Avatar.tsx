'use client'
import {
  Avatar,
  AvatarImage,
  AvatarFallback,
} from '@/components/ui/base-avatar'

type AvatarProps = {
  uuid: string
}

const CompundAvatar: React.FC<AvatarProps> = ({ uuid }) => {
  return (
    <Avatar>
      <AvatarImage
        src={`https://api.dicebear.com/9.x/fun-emoji/svg?seed=${uuid}`}
      />
      <AvatarFallback>CN</AvatarFallback>
    </Avatar>
  )
}

export default CompundAvatar
