import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card'
import {
  Tooltip,
  TooltipProvider,
  TooltipTrigger,
  TooltipContent,
} from '@/components/ui/tooltip'
import { ChevronRight } from 'lucide-react'
import Link from 'next/link'

import type { Room } from '@/types'

const RoomCard: React.FC<Room> = ({ id, name, created_by, created_at }) => {
  return (
    <Card>
      <CardHeader>{name}</CardHeader>
      <CardContent>
        <p>Created by: {created_by}</p>
        <p>Created on: {created_at.toISOString()}</p>
      </CardContent>
      <TooltipProvider>
        <CardFooter className="flex justify-end">
          <Tooltip>
            <TooltipTrigger asChild>
              <Link href={`/room/${id}`} passHref>
                <Button variant="outline" size="icon">
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </TooltipTrigger>
            <TooltipContent>
              <p>Go to room</p>
            </TooltipContent>
          </Tooltip>
        </CardFooter>
      </TooltipProvider>
    </Card>
  )
}

export default RoomCard
