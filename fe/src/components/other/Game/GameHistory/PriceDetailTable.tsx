import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableCell,
  TableHead,
} from '@/components/ui/table'

import type { GamePriceHistory } from '@/types'

interface PriceDetailTableProps {
  prices: GamePriceHistory[]
}

const PriceDetailTable: React.FC<PriceDetailTableProps> = ({ prices }) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>User ID</TableHead>
          <TableHead>Price</TableHead>
          <TableHead>Currency</TableHead>
          <TableHead>Conversion Rate</TableHead>
          <TableHead>Price in CZK</TableHead>
          <TableHead>Created At</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {prices.map((priceHistory, index) => (
          <TableRow key={index}>
            <TableCell>{priceHistory.userId}</TableCell>
            <TableCell>{priceHistory.price}</TableCell>
            <TableCell>{priceHistory.currency}</TableCell>
            <TableCell>{priceHistory.conversionRate ?? 'N/A'}</TableCell>
            <TableCell>{priceHistory.priceInCzk}</TableCell>
            <TableCell>
              {new Date(priceHistory.created_at).toLocaleString()}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export default PriceDetailTable
