import { useCallback, useState } from 'react'
import { downloadPracticeTestMarkScheme } from '../api/client'

type Status = 'idle' | 'loading' | 'success' | 'error'

interface UseDownloadMarkSchemeResult {
  status: Status
  error: string | null
  download: (paperId: string) => Promise<void>
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

export function useDownloadMarkScheme(): UseDownloadMarkSchemeResult {
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState<string | null>(null)

  const download = useCallback(async (paperId: string) => {
    setStatus('loading')
    setError(null)
    try {
      const blob = await downloadPracticeTestMarkScheme(paperId)
      triggerDownload(blob, `${paperId}-mark-scheme.pdf`)
      setStatus('success')
    } catch (err) {
      console.error('Failed to download mark scheme:', err)
      setError(err instanceof Error ? err.message : 'Failed to download mark scheme')
      setStatus('error')
    }
  }, [])

  return { status, error, download }
}
