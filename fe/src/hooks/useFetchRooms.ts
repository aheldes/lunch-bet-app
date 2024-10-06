import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchTasks } from '@/api/api'

import { Room } from '@/types'

const useFetchRooms = (
  setData: React.Dispatch<React.SetStateAction<Room[]>>
) => {
  const { data, isLoading, isError } = useQuery<Room[]>({
    queryKey: ['rooms'],
    queryFn: fetchTasks,
    staleTime: 5000,
  })

  useEffect(() => {
    if (data) {
      setData(data)
    }
  }, [data])

  return { isLoading, isError }
}

export default useFetchRooms
