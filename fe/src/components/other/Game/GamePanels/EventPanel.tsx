import { Card, CardContent, CardHeader } from '@/components/ui/card'
import useRoomContext from '@/hooks/useRoomContext'

type EventPanelProps = {
  className?: string
}

const EventPanel: React.FC<EventPanelProps> = ({ className }) => {
  const { eventHistory } = useRoomContext()
  return (
    <Card className={`flex flex-col ${className}`}>
      <CardHeader>Event log</CardHeader>
      <CardContent className="overflow-y-auto max-h-[50vh]">
        {eventHistory.map((event, index) => (
          <div key={index} className="mb-2 flex flex-col gap-1">
            <div className="text-gray-500 text-sm">
              {event.timestamp.toLocaleString()}
            </div>
            {event.message}
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

export default EventPanel
