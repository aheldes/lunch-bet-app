import { useState, useEffect } from 'react'
import { Event, GameState, Price } from '@/types'

const useGameState = (users: string[]) => {
  const [bets, setBets] = useState<string[]>([])
  const [betSet, setBetSet] = useState(false)
  const [eventHistory, setEventHistory] = useState<Event[]>([])
  const [gameState, setGameState] = useState<GameState>(GameState.IDLE)
  const [prices, setPrices] = useState<Price[]>([])
  const [priceSet, setPriceSet] = useState(false)
  const [result, setResult] = useState<string | null>(null)

  const resetGame = () => {
    setGameState(GameState.IDLE)
    setBetSet(false)
    setPriceSet(false)
    setBets([])
    setPrices([])
  }

  const clearResult = () => setResult('')

  useEffect(() => {
    if (users.length === prices.length && users.length > 1) {
      setGameState(GameState.PRICES_SET)
    }
  }, [users, prices])

  useEffect(() => {
    if (users.length === bets.length && users.length > 1) {
      setGameState(GameState.BETS_SET)
    }
  }, [users, bets])

  return {
    betSet,
    eventHistory,
    gameState,
    prices,
    priceSet,
    result,
    setBets,
    setBetSet,
    setEventHistory,
    setGameState,
    setPrices,
    setPriceSet,
    setResult,
    clearResult,
    resetGame,
  }
}

export default useGameState
