import { useMemo } from 'react'
import type { Section, Topic } from '../api/types'
import { TopicCard } from './TopicCard'

interface TopicSearchProps {
  sections: Section[]
  query: string
}

interface FlatResult {
  topic: Topic
  breadcrumb: string
}

export function TopicSearch({ sections, query }: TopicSearchProps) {
  const allResults = useMemo<FlatResult[]>(() => {
    const results: FlatResult[] = []
    for (const section of sections) {
      for (const group of section.groups) {
        for (const topic of group.topics) {
          results.push({ topic, breadcrumb: `${section.name} › ${group.name}` })
        }
      }
    }
    return results
  }, [sections])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return allResults
    return allResults.filter((r) => r.topic.name.toLowerCase().includes(q))
  }, [allResults, query])

  return (
    <div className="topic-search-results">
      {filtered.map(({ topic, breadcrumb }) => (
        <div key={topic.id} className="topic-search-results__item">
          <p className="topic-search-results__breadcrumb">{breadcrumb}</p>
          <TopicCard topic={topic} />
        </div>
      ))}
      {filtered.length === 0 && (
        <p className="topic-search-results__empty">No topics match &quot;{query}&quot;</p>
      )}
    </div>
  )
}
