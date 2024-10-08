'use client'

import {
  Game,
  GamePanels,
  GameHistoryTables,
  ResultDialog,
} from '@/components/other/Game'

const Body: React.FC = () => {
  return (
    <>
      <div className="grid grid-rows-12 gap-3 h-full">
        <Game />

        <div className="grid grid-cols-8 gap-2 px-3 row-span-8">
          <GamePanels />
        </div>

        <div className="row-span-5">
          <GameHistoryTables />
        </div>
      </div>
      <ResultDialog />
    </>
  )
}

export default Body
