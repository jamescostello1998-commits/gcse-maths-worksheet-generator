import type { Section } from '../api/types'
import { TopicCard } from './TopicCard'

interface SectionViewProps {
  section: Section
  onBack: () => void
}

export function SectionView({ section, onBack }: SectionViewProps) {
  return (
    <div className="section-view">
      <button type="button" className="section-view__back" onClick={onBack}>
        ← Back
      </button>
      <h2 className="section-view__title">{section.name}</h2>
      {section.groups.length === 0 ? (
        <p className="section-view__empty">No topics yet — check back soon.</p>
      ) : (
        section.groups.map((group) => (
          <div key={group.name} className="topic-group">
            <h3 className="topic-group__name">{group.name}</h3>
            <div className="topic-grid">
              {group.topics.map((topic) => (
                <TopicCard key={topic.id} topic={topic} />
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
