import { useCallback, useState } from 'react'
import { generateBellTasks, type BellTasksYear } from '../api/client'

type Status = 'idle' | 'loading' | 'success' | 'error'

interface UseGenerateBellTasksResult {
  status: Status
  error: string | null
  generate: (topicIds: string[], year: BellTasksYear) => Promise<void>
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

export function useGenerateBellTasks(): UseGenerateBellTasksResult {
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState<string | null>(null)

  const generate = useCallback(async (topicIds: string[], year: BellTasksYear) => {
    setStatus('loading')
    setError(null)
    try {
      const blob = await generateBellTasks(topicIds, year)
      triggerDownload(blob, 'bell-tasks.pptx')
      setStatus('success')
    } catch (err) {
      console.error('Failed to generate bell tasks:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate bell tasks')
      setStatus('error')
    }
  }, [])

  return { status, error, generate }
}
