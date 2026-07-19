import { useEffect, useState } from 'react'
import { fetchTopics } from '../api/client'
import type { Topic } from '../api/types'

interface UseTopicsResult {
  topics: Topic[]
  loading: boolean
  error: string | null
}

export function useTopics(): UseTopicsResult {
  const [topics, setTopics] = useState<Topic[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    fetchTopics()
      .then((result) => {
        if (!cancelled) {
          setTopics(result)
          setLoading(false)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load topics')
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  return { topics, loading, error }
}
