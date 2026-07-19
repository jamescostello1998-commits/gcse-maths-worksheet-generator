import type { Section } from '../api/types'

interface HomeScreenProps {
  sections: Section[]
  onSelectSection: (sectionId: string) => void
}

export function HomeScreen({ sections, onSelectSection }: HomeScreenProps) {
  return (
    <div className="home-screen">
      {sections.map((section) => {
        const topicCount = section.groups.reduce((sum, g) => sum + g.topics.length, 0)
        const isEmpty = topicCount === 0
        return (
          <button
            key={section.id}
            type="button"
            className={isEmpty ? 'section-card section-card--empty' : 'section-card'}
            onClick={() => onSelectSection(section.id)}
            disabled={isEmpty}
          >
            <h2 className="section-card__name">{section.name}</h2>
            <p className="section-card__count">
              {isEmpty ? 'No topics yet' : `${topicCount} topic${topicCount === 1 ? '' : 's'}`}
            </p>
          </button>
        )
      })}
    </div>
  )
}
