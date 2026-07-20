import { useCallback, useState } from 'react'
import { generateModelledExample } from '../api/client'
import type { Tier } from '../api/types'

type Status = 'idle' | 'loading' | 'success' | 'error'

interface UseGenerateModelledExampleResult {
  status: Status
  error: string | null
  generate: (topicId: string, tier: Tier) => Promise<void>
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

export function useGenerateModelledExample(): UseGenerateModelledExampleResult {
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState<string | null>(null)

  const generate = useCallback(async (topicId: string, tier: Tier) => {
    setStatus('loading')
    setError(null)
    try {
      const blob = await generateModelledExample(topicId, tier)
      triggerDownload(blob, `${topicId}-${tier}-modelled-example.pdf`)
      setStatus('success')
    } catch (err) {
      console.error('Failed to generate modelled example:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate modelled example')
      setStatus('error')
    }
  }, [])

  return { status, error, generate }
}
