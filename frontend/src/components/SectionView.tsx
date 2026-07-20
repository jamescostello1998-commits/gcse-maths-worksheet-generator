import { useState } from 'react'
import type { Section, Tier } from '../api/types'
import { TopicCard } from './TopicCard'

interface SectionViewProps {
  section: Section
  onBack: () => void
}

const TIERS: Tier[] = ['foundation', 'higher']
const TIER_LABELS: Record<Tier, string> = { foundation: 'Foundation', higher: 'Higher' }

function countForTier(section: Section, tier: Tier): number {
  return section.groups.reduce(
    (sum, group) => sum + group.topics.filter((t) => t.fixedTier === tier || t.fixedTier === null).length,
    0,
  )
}

export function SectionView({ section, onBack }: SectionViewProps) {
  const [selectedTier, setSelectedTier] = useState<Tier | null>(null)

  if (section.groups.length === 0) {
    return (
      <div className="section-view">
        <button type="button" className="section-view__back" onClick={onBack}>
          ← Back
        </button>
        <h2 className="section-view__title">{section.name}</h2>
        <p className="section-view__empty">No topics yet — check back soon.</p>
      </div>
    )
  }

  if (!selectedTier) {
    return (
      <div className="section-view">
        <button type="button" className="section-view__back" onClick={onBack}>
          ← Back
        </button>
        <h2 className="section-view__title">{section.name}</h2>
        <div className="tier-picker">
          {TIERS.map((tier) => {
            const count = countForTier(section, tier)
            const isEmpty = count === 0
            return (
              <button
                key={tier}
                type="button"
                className={isEmpty ? 'tier-picker__option tier-picker__option--empty' : 'tier-picker__option'}
                onClick={() => setSelectedTier(tier)}
                disabled={isEmpty}
              >
                <span className="tier-picker__name">{TIER_LABELS[tier]}</span>
                <span className="tier-picker__count">
                  {isEmpty ? 'No topics yet' : `${count} topic${count === 1 ? '' : 's'}`}
                </span>
              </button>
            )
          })}
        </div>
      </div>
    )
  }

  const filteredGroups = section.groups
    .map((group) => ({
      ...group,
      topics: group.topics.filter((t) => t.fixedTier === selectedTier || t.fixedTier === null),
    }))
    .filter((group) => group.topics.length > 0)

  return (
    <div className="section-view">
      <button type="button" className="section-view__back" onClick={() => setSelectedTier(null)}>
        ← Back
      </button>
      <h2 className="section-view__title">
        {section.name} <span className="section-view__tier">· {TIER_LABELS[selectedTier]}</span>
      </h2>
      {filteredGroups.map((group) => (
        <div key={group.name} className="topic-group">
          <h3 className="topic-group__name">{group.name}</h3>
          <div className="topic-grid">
            {group.topics.map((topic) => (
              <TopicCard key={topic.id} topic={topic} showTierBadge={false} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
