export enum RoomEventTypes {
  JOIN = 'join',
  LEAVE = 'leave',
  ERROR = 'error',
}

export type ActionResponse = {
  user_id: string
  action: string
  timestamp: string
  message: string
}

export type Action = {
  user_id: string
  action: RoomEventTypes
  timestamp: Date
  message: string
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
