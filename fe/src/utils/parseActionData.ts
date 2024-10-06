import type { Action, ActionResponse } from '@/types'
import { ActionTypes } from '@/types'

const actionTypeMap: { [key: string]: ActionTypes } = {
  join: ActionTypes.JOIN,
  leave: ActionTypes.LEAVE,
}

const parseActionData = (actionData: ActionResponse[]): Action[] => {
  return actionData.map((action) => {
    let actionType: ActionTypes

    if (action.action in actionTypeMap) {
      actionType = actionTypeMap[action.action]
    } else {
      actionType = ActionTypes.ERROR
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
