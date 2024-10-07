import type { Action, ActionResponse } from '@/types'
import { Currency, RoomEventTypes } from '@/types'

const actionTypeMap: { [key: string]: RoomEventTypes } = {
  join: RoomEventTypes.JOIN,
  leave: RoomEventTypes.LEAVE,
  game_start: RoomEventTypes.GAME_START,
  game_end: RoomEventTypes.GAME_END,
  set_price: RoomEventTypes.SET_PRICE,
}

const currencyMap: { [key: string]: Currency } = {
  czk: Currency.CZK,
  eur: Currency.EUR,
  usd: Currency.USD,
}

const parseActionData = (actionData: ActionResponse[]): Action[] => {
  return actionData.map((action) => {
    let actionType: RoomEventTypes

    if (action.action in actionTypeMap) {
      actionType = actionTypeMap[action.action]
    } else {
      actionType = RoomEventTypes.ERROR
      console.warn(`Unknown action type: ${action.action}`)
    }

    let currency
    if (action.currency && action.currency in currencyMap) {
      currency = currencyMap[action.currency]
    }

    return {
      user_id: action.user_id,
      action: actionType,
      message: action.message,
      timestamp: new Date(action.timestamp),
      price: action.price,
      currency: currency,
    }
  })
}

export default parseActionData
