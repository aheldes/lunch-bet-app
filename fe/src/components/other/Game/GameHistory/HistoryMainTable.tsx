import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableCell,
  TableHead,
} from '@/components/ui/table'
import { Button } from '@/components/ui/button'

import type { GameHistory } from '@/types'

interface GameHistoryMainTableProps {
  historyData: GameHistory[] | undefined
  onShowPriceHistory: (prices: GameHistory['prices']) => void
}

const GameHistoryMainTable: React.FC<GameHistoryMainTableProps> = ({
  historyData,
  onShowPriceHistory,
}) => {
  return (
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
              <Button onClick={() => onShowPriceHistory(game.prices)}>
                Price History
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export default GameHistoryMainTable
