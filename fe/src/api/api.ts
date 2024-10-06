import axios, { AxiosResponse } from 'axios'

import parseActionData from '@/utils/parseActionData'
import parseRoomData from '@/utils/parseRoomData'

import type { Action, ActionResponse, Room, RoomResponse } from '@/types'

// Manually set as cannot inject via environment variables in docker-compose
export const API_URL = 'http://localhost:8000'

export const fetchTasks = async (): Promise<Room[]> => {
  try {
    const response = await axios.get<RoomResponse[]>(`${API_URL}/rooms`)
    const rawTasks = response.data
    return parseRoomData(rawTasks)
  } catch (error) {
    throw error
  }
}

export const fetchActions = async (room_id: string): Promise<Action[]> => {
  try {
    const response = await axios.get<ActionResponse[]>(
      `${API_URL}/rooms/${room_id}/actions`
    )
    const rawTasks = response.data
    return parseActionData(rawTasks)
  } catch (error) {
    throw error
  }
}

export const createRoom = async ({
  name,
  user_id,
}: {
  name: string
  user_id: string
}): Promise<AxiosResponse> => {
  try {
    return await axios.post(`${API_URL}/rooms`, { name, user_id })
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(
        error.response?.data?.detail ||
          'An error occurred while creating the room'
      )
    }
    throw new Error('An error occurred while creating the room')
  }
}
