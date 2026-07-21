import { useCallback, useState } from 'react'
import { generateWorksheet } from '../api/client'
import type { Tier, WorksheetOptions } from '../api/types'

type Status = 'idle' | 'loading' | 'success' | 'error'

interface UseGenerateWorksheetResult {
  status: Status
  error: string | null
  generate: (topicId: string, tier: Tier, options?: WorksheetOptions) => Promise<void>
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function useGenerateWorksheet(): UseGenerateWorksheetResult {
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState<string | null>(null)

  const generate = useCallback(async (topicId: string, tier: Tier, options: WorksheetOptions = {}) => {
    setStatus('loading')
    setError(null)
    try {
      const blob = await generateWorksheet(topicId, tier, options)
      const suffix = options.answersOnly ? '-answers-only' : ''
      triggerDownload(blob, `${topicId}-${tier}-worksheet${suffix}.pdf`)
      setStatus('success')
    } catch (err) {
      console.error('Failed to generate worksheet:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate worksheet')
      setStatus('error')
    }
  }, [])

  return { status, error, generate }
}
