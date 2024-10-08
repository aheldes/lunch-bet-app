import type { GameHistory, GameHistoryResponse } from '@/types'

const parseHistoryData = (
  historyData: GameHistoryResponse[]
): GameHistory[] => {
  return historyData.map((history) => {
    return {
      id: history.id,
      roomId: history.room_id,
      loser: history.loser,
      price: history.price,
      createdAt: new Date(history.created_at),
      prices: history.prices.map((priceHistory) => ({
        userId: priceHistory.user_id,
        price: priceHistory.price,
        currency: priceHistory.currency,
        conversionRate: priceHistory.conversion_rate,
        priceInCzk: priceHistory.price_in_czk,
        created_at: new Date(priceHistory.created_at),
      })),
    }
  })
}

export default parseHistoryData
