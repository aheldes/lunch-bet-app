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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import { Currency, RoomEventTypes } from '@/types'

const schema = z
  .object({
    price: z.number().positive({ message: 'Price must be positive' }),
    currency: z.nativeEnum(Currency, { message: 'Invalid currency' }),
  })
  .superRefine((data, ctx) => {
    const { price, currency } = data
    if (currency === Currency.CZK && price > 10000) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'CZK price cannot exceed 10,000',
        path: ['price'],
      })
    } else if (
      (currency === Currency.EUR || currency === Currency.USD) &&
      price > 250
    ) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'EUR/USD price cannot exceed 250',
        path: ['price'],
      })
    }
  })

type FormData = z.infer<typeof schema>

const PriceDialog: React.FC = () => {
  const { uuid } = useUUIDContext()
  const { priceSet, sendJsonMessage } = useRoomContext()
  const [open, setOpen] = useState(false)

  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      price: 0,
      currency: Currency.CZK,
    },
  })

  const onSubmit = async (data: FormData) => {
    sendJsonMessage({
      type: RoomEventTypes.SET_PRICE,
      user_id: uuid,
      price: data.price,
      currency: data.currency,
    })
    setOpen(false)
  }

  return (
    <>
      {priceSet ? (
        <div>Waiting for other players to set prices.</div>
      ) : (
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button disabled={priceSet}>Set price</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Select a Price</DialogTitle>
              <DialogDescription>
                Choose a price and currency. Max values: CZK 10,000 / EUR & USD
                250.
              </DialogDescription>
            </DialogHeader>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="flex flex-col"
              >
                {/* Price Input */}
                <FormField
                  control={form.control}
                  name="price"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Price</FormLabel>
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
                <FormField
                  control={form.control}
                  name="currency"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Currency</FormLabel>
                      <FormControl>
                        <Select
                          onValueChange={field.onChange}
                          defaultValue={field.value}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select currency" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value={Currency.CZK}>CZK</SelectItem>
                            <SelectItem value={Currency.EUR}>EUR</SelectItem>
                            <SelectItem value={Currency.USD}>USD</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <DialogFooter className="sm:justify-end">
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

export default PriceDialog
