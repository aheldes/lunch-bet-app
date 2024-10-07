export enum RoomEventTypes {
  JOIN = 'join',
  LEAVE = 'leave',
  GAME_START = 'game_start',
  GAME_END = 'game_end',
  SET_PRICE = 'set_price',
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
