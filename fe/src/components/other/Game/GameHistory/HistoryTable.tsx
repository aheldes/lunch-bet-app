'use client'

import { useState } from 'react'
import useRoomContext from '@/hooks/useRoomContext'

import GameHistoryMainTable from './HistoryMainTable'
import PriceDetailTable from './PriceDetailTable'

import type { GamePriceHistory } from '@/types'

const GameHistoryTable = () => {
  const { historyData } = useRoomContext()
  const [selectedPrices, setSelectedPrices] = useState<
    GamePriceHistory[] | null
  >(null)

  const handleShowPriceHistory = (prices: GamePriceHistory[]) => {
    setSelectedPrices(prices)
  }

  return (
    <div className="p-2">
      <div className="text-2xl">History</div>
      <div className="grid grid-cols-2 gap-3">
        <GameHistoryMainTable
          historyData={historyData}
          onShowPriceHistory={handleShowPriceHistory}
        />

        {selectedPrices && <PriceDetailTable prices={selectedPrices} />}
      </div>
    </div>
  )
}

export default GameHistoryTable
