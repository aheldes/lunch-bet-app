'use client'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import useUUIDContext from '@/hooks/useUUIDContext'
import useRoomContext from '@/hooks/useRoomContext'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'

import { RoomEventTypes } from '@/types'

const schema = z.object({
  bet: z
    .number()
    .min(1, { message: 'Bet must be at least 1' })
    .max(10000, { message: 'Bet cannot exceed 10,000' }),
})

type FormData = z.infer<typeof schema>

const BetDialog: React.FC = () => {
  const { uuid } = useUUIDContext()
  const { betSet, sendJsonMessage } = useRoomContext()
  const [open, setOpen] = useState(false)

  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      bet: 1,
    },
  })

  const onSubmit = async (data: FormData) => {
    sendJsonMessage({
      type: RoomEventTypes.SET_BET,
      user_id: uuid,
      bet: data.bet,
    })
    setOpen(false)
  }

  return (
    <>
      {betSet ? (
        <div>Waiting for other players to set their bets.</div>
      ) : (
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button disabled={betSet}>Set Bet</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Place Your Bet</DialogTitle>
              <DialogDescription>
                Choose a bet between 1 and 10,000.
              </DialogDescription>
            </DialogHeader>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="flex flex-col"
              >
                <FormField
                  control={form.control}
                  name="bet"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Bet</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          {...field}
                          onChange={(e) =>
                            field.onChange(Number(e.target.value))
                          }
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <DialogFooter className="sm:justify-end mt-2">
                  <Button type="submit" variant="secondary">
                    Submit
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      )}
    </>
  )
}

export default BetDialog
