import type { Action, ActionResponse } from '@/types'
import { RoomEventTypes } from '@/types'

const actionTypeMap: { [key: string]: RoomEventTypes } = {
  join: RoomEventTypes.JOIN,
  leave: RoomEventTypes.LEAVE,
  game_start: RoomEventTypes.GAME_START,
  game_end: RoomEventTypes.GAME_END,
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

    return {
      user_id: action.user_id,
      action: actionType,
      message: action.message,
      timestamp: new Date(action.timestamp),
    }
  })
}

export default parseActionData
