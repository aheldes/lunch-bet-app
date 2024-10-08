import useRoomContext from '@/hooks/useRoomContext'

import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Avatar } from '@/components/other/Avatar'

const PricesPanel: React.FC = () => {
  const { prices } = useRoomContext()
  return (
    <Card className={`flex flex-col items-center`}>
      <CardHeader>Prices</CardHeader>
      <CardContent className="overflow-y-auto">
        {prices.map((price, index) => (
          <div key={index} className="flex gap-2 items-center mb-2">
            <Avatar uuid={price.user_id} />
            {price.price} - {price.currency}
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

export default PricesPanel
