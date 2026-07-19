import { useMemo, useState } from 'react'
import type { Topic } from '../api/types'

interface TopicSearchProps {
  topics: Topic[]
  selectedTopicId: string | null
  onSelect: (topicId: string) => void
}

export function TopicSearch({ topics, selectedTopicId, onSelect }: TopicSearchProps) {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return topics
    return topics.filter((topic) => topic.name.toLowerCase().includes(q))
  }, [topics, query])

  return (
    <div className="topic-search">
      <input
        type="text"
        className="topic-search__input"
        placeholder="Search for a topic..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search for a topic"
      />
      <ul className="topic-search__list">
        {filtered.map((topic) => (
          <li key={topic.id}>
            <button
              type="button"
              className={
                topic.id === selectedTopicId
                  ? 'topic-search__item topic-search__item--selected'
                  : 'topic-search__item'
              }
              onClick={() => onSelect(topic.id)}
            >
              <span className="topic-search__item-name">{topic.name}</span>
              <span className="topic-search__item-description">{topic.description}</span>
            </button>
          </li>
        ))}
        {filtered.length === 0 && <li className="topic-search__empty">No topics match "{query}"</li>}
      </ul>
    </div>
  )
}
