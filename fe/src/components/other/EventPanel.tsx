import { Card, CardContent, CardHeader } from '@/components/ui/card'
import type { Event } from '@/types'

type EventPanelProps = {
  events: Event[]
  className?: string
}

const EventPanel: React.FC<EventPanelProps> = ({ events, className }) => {
  return (
    <Card className={`flex flex-col items-center ${className}`}>
      <CardHeader>Event log</CardHeader>
      <CardContent className="overflow-y-auto max-h-[50vh]">
        {events.map((event, index) => (
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
