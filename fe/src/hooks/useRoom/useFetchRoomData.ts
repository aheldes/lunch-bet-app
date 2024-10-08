import { useQuery } from '@tanstack/react-query'
import { fetchActions, fetchHistory } from '@/api/api'
import type { Action, GameHistory } from '@/types'

const useFetchRoomData = (room_id: string) => {
  const {
    data: actionsData,
    isLoading: actionsLoading,
    isError: actionsError,
  } = useQuery<Action[]>({
    queryKey: ['room', room_id],
    queryFn: () => fetchActions(room_id),
    staleTime: 5000,
  })

  const {
    data: historyData,
    isLoading: historyLoading,
    isError: historyError,
    refetch: refetchHistory,
  } = useQuery<GameHistory[]>({
    queryKey: ['room_history', room_id],
    queryFn: () => fetchHistory(room_id),
    staleTime: 5000,
  })

  return {
    actionsData,
    actionsLoading,
    actionsError,
    historyData,
    historyLoading,
    historyError,
    refetchHistory,
  }
}

export default useFetchRoomData
