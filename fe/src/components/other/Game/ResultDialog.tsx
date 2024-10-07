'use client'
import { useEffect, useState } from 'react'
import useRoomContext from '@/hooks/useRoomContext'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const ResultDialog: React.FC = () => {
  const { result, clearResult } = useRoomContext()
  const [open, setOpen] = useState(false)

  useEffect(() => {
    if (result) {
      setOpen(true)
    }
  }, [result])

  const handleClose = () => {
    setOpen(false)
    clearResult()
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Result!</DialogTitle>
          <DialogDescription>{result}</DialogDescription>
        </DialogHeader>
        <DialogFooter className="sm:justify-end">
          <Button type="submit" variant="secondary" onClick={handleClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default ResultDialog
