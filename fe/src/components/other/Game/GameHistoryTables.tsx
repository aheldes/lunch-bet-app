import { useState } from 'react'
import useRoomContext from '@/hooks/useRoomContext'

import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableCell,
  TableHead,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'

import { GameHistory, GamePriceHistory } from '@/types'

const GameHistoryTable = () => {
  const { historyData } = useRoomContext()
  const [selectedPrices, setSelectedPrices] = useState<
    GamePriceHistory[] | null
  >(null)

  const handleShowPriceHistory = (prices: GamePriceHistory[]) => {
    setSelectedPrices(prices)
  }

  return (
    <div className="grid grid-cols-2">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Room ID</TableHead>
            <TableHead>Loser</TableHead>
            <TableHead>Price</TableHead>
            <TableHead>Created At</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {historyData?.map((game) => (
            <TableRow key={game.id}>
              <TableCell>{game.id}</TableCell>
              <TableCell>{game.roomId}</TableCell>
              <TableCell>{game.loser}</TableCell>
              <TableCell>{game.price}</TableCell>
              <TableCell>{game.createdAt.toLocaleString()}</TableCell>
              <TableCell>
                <Button onClick={() => handleShowPriceHistory(game.prices)}>
                  Price History
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {selectedPrices && (
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
            {selectedPrices.map((priceHistory, index) => (
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
      )}
    </div>
  )
}

export default GameHistoryTable
