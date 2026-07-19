import { useEffect, useState } from 'react'
import { fetchSections } from '../api/client'
import type { Section } from '../api/types'

interface UseSectionsResult {
  sections: Section[]
  loading: boolean
  error: string | null
}

export function useSections(): UseSectionsResult {
  const [sections, setSections] = useState<Section[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    fetchSections()
      .then((result) => {
        if (!cancelled) {
          setSections(result)
          setLoading(false)
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load sections')
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  return { sections, loading, error }
}
