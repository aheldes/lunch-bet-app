import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

const RoomCard: React.FC = () => {
  return (
    <Card className="w-[467px]">
      <CardHeader>
        <Skeleton className="h-[24px] w-[418px]" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-[24px] w-[418px] mb-1" />
        <Skeleton className="h-[24px] w-[418px]" />
      </CardContent>
      <CardFooter className="flex justify-end">
        <Skeleton className="h-[34px] w-[34px]" />
      </CardFooter>
    </Card>
  )
}

export default RoomCard
