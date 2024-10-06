'use client'
import CompoundAvatar from './Avatar'

import useUUIDContext from '@/hooks/useUUIDContext'

const UserAvatar: React.FC = () => {
  const { uuid } = useUUIDContext()

  return uuid ? <CompoundAvatar uuid={uuid} /> : null
}

export default UserAvatar
