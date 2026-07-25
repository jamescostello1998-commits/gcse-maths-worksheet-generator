import { useEffect, useState } from 'react'
import { fetchPracticeTests } from '../api/client'
import type { PracticeTestSummary } from '../api/types'

interface UsePracticeTestsResult {
  practiceTests: PracticeTestSummary[]
  loading: boolean
  error: string | null
}

export function usePracticeTests(): UsePracticeTestsResult {
  const [practiceTests, setPracticeTests] = useState<PracticeTestSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    fetchPracticeTests()
      .then((result) => {
        if (!cancelled) {
          setPracticeTests(result)
          setLoading(false)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load practice tests')
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  return { practiceTests, loading, error }
}
