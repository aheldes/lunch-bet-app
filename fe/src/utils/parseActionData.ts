import type { Action, ActionResponse } from '@/types'
import { RoomEventTypes } from '@/types'

const actionTypeMap: { [key: string]: RoomEventTypes } = {
  join: RoomEventTypes.JOIN,
  leave: RoomEventTypes.LEAVE,
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
