import axios, { AxiosResponse } from 'axios'

import parseRoomData from '@/utils/parseRoomData'

import type { Room, RoomResponse } from '@/types'

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

export const createRoom = async ({
  name,
  user_id,
}: {
  name: string
  user_id: string
}): Promise<AxiosResponse> => {
  return await axios.post(`${API_URL}/rooms`, { name, user_id })
}
