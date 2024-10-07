type GameStateTitleProps = {
  title: string
}

const GameStateTitle: React.FC<GameStateTitleProps> = ({ title }) => {
  return <div className="text-2xl mb-4">{title}</div>
}

export default GameStateTitle
