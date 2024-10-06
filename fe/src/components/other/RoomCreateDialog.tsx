'use client'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { createRoom } from '@/api/api'
import useUUIDContext from '@/hooks/useUUIDContext'
import { useToast } from '@/hooks/use-toast'

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
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'

const schema = z.object({
  roomName: z
    .string()
    .min(2, { message: 'Room name must be at least 2 characters long' })
    .max(15, { message: 'Room name cannot exceed 15 characters' }),
})

type FormData = z.infer<typeof schema>

const RoomCreateDialog: React.FC = () => {
  const [open, setOpen] = useState(false)
  const { uuid } = useUUIDContext()
  const { toast } = useToast()
  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      roomName: '',
    },
  })

  const mutation = useMutation({
    mutationFn: createRoom,
    onSuccess: () => {
      form.reset()
      setOpen(false)
      toast({
        title: 'Success',
        description: 'Room successfully created.',
      })
    },
    onError: (error) => {
      toast({
        variant: 'destructive',
        title: 'Error.',
        description: error.message,
      })
    },
  })

  const onSubmit = async (data: FormData) => {
    if (uuid) {
      mutation.mutate({
        name: data.roomName,
        user_id: uuid,
      })
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary">New Room</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Create a new room</DialogTitle>
          <DialogDescription>
            No one will have access to your room unless you approve their
            request.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="flex flex-col"
          >
            <FormField
              control={form.control}
              name="roomName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Room name</FormLabel>
                  <FormControl>
                    <Input {...field} />
                  </FormControl>
                  <FormDescription>
                    This will be the public name of the room.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <DialogFooter className="sm:justify-end">
              <Button type="submit" variant="secondary">
                Create
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default RoomCreateDialog
