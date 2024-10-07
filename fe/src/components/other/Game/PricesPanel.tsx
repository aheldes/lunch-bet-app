import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Avatar } from '@/components/other/Avatar'
import { Price } from '@/types'

type PricesPanel = {
  prices: Price[]
}

const PricesPanel: React.FC<PricesPanel> = ({ prices }) => {
  return (
    <Card className={`flex flex-col items-center`}>
      <CardHeader>Prices</CardHeader>
      <CardContent className="overflow-y-auto max-h-[50vh]">
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
