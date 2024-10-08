export enum RoomEventTypes {
  JOIN = 'join',
  LEAVE = 'leave',
  GAME_START = 'game_start',
  GAME_END = 'game_end',
  SET_PRICE = 'set_price',
  SET_BET = 'set_bet',
  EVALUATE = 'evaluate',
  RESULT = 'result',
  ERROR = 'error',
}

export enum Currency {
  CZK = 'czk',
  EUR = 'eur',
  USD = 'usd',
}

export enum GameState {
  IDLE = 'idle',
  STARTED = 'started',
  PRICES_SET = 'pricesSet',
  BETS_SET = 'betsSet',
}

export type ActionResponse = {
  user_id: string
  action: string
  timestamp: string
  message: string
  price?: string
  currency?: Currency
}

export type Action = {
  user_id: string
  action: RoomEventTypes
  timestamp: Date
  message: string
  price?: string
  currency?: Currency
}

export type Event = Omit<Action, 'user_id' | 'action'>

export type GamePriceHistory = {
  userId: string
  price: string
  currency: string
  conversionRate?: string
  priceInCzk: string
  created_at: Date
}

export type GameHistory = {
  id: string
  roomId: string
  loser: string
  price: string
  createdAt: Date
  prices: GamePriceHistory[]
}

export type GamePriceHistoryResponse = {
  user_id: string
  price: string
  currency: string
  conversion_rate?: string
  price_in_czk: string
  created_at: string
}

export type GameHistoryResponse = {
  id: string
  room_id: string
  loser: string
  price: string
  created_at: string
  prices: GamePriceHistoryResponse[]
}

export type Room = {
  id: string
  name: string
  created_by: string
  created_at: Date
}

export type RoomResponse = {
  id: string
  name: string
  created_by: string
  created_at: string
}

export type Price = {
  price: string
  currency: Currency
  user_id: string
}
