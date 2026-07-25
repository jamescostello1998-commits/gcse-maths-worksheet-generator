import { useCallback, useState } from 'react'
import { downloadPracticeTestPaper } from '../api/client'

type Status = 'idle' | 'loading' | 'success' | 'error'

interface UseDownloadTestPaperResult {
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

export function useDownloadTestPaper(): UseDownloadTestPaperResult {
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState<string | null>(null)

  const download = useCallback(async (paperId: string) => {
    setStatus('loading')
    setError(null)
    try {
      const blob = await downloadPracticeTestPaper(paperId)
      triggerDownload(blob, `${paperId}-test-paper.pdf`)
      setStatus('success')
    } catch (err) {
      console.error('Failed to download test paper:', err)
      setError(err instanceof Error ? err.message : 'Failed to download test paper')
      setStatus('error')
    }
  }, [])

  return { status, error, download }
}
