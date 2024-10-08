import useRoomContext from '@/hooks/useRoomContext'

import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Avatar } from '@/components/other/Avatar/'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@radix-ui/react-tooltip'

type UserPanelProps = {
  className?: string
}

const UserPanel: React.FC<UserPanelProps> = ({ className }) => {
  const { users } = useRoomContext()
  return (
    <Card className={`flex flex-col items-center ${className}`}>
      <CardHeader>Active users</CardHeader>
      <CardContent className="overflow-y-auto">
        {users.map((uuid) => (
          <div key={uuid} className="mb-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Avatar uuid={uuid} />
                </TooltipTrigger>
                <TooltipContent>
                  <p>User {uuid.split('-').slice(0, 1).join('-')} ...</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

export default UserPanel
