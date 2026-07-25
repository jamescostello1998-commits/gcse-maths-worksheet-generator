import { useState } from 'react'
import type { Tier } from '../api/types'
import { usePracticeTests } from '../hooks/usePracticeTests'
import { PracticeTestCard } from './PracticeTestCard'

interface PracticeTestsViewProps {
  onBack: () => void
}

const TIERS: Tier[] = ['foundation', 'higher']
const TIER_LABELS: Record<Tier, string> = { foundation: 'Foundation', higher: 'Higher' }

export function PracticeTestsView({ onBack }: PracticeTestsViewProps) {
  const { practiceTests, loading, error } = usePracticeTests()
  const [selectedTier, setSelectedTier] = useState<Tier | null>(null)

  if (!selectedTier) {
    return (
      <div className="section-view">
        <button type="button" className="section-view__back" onClick={onBack}>
          ← Back
        </button>
        <h2 className="section-view__title">Practice Tests</h2>
        {loading && <p className="page__loading">Loading practice tests…</p>}
        {error && <p className="topic-card__error">{error}</p>}
        {!loading && !error && (
          <div className="tier-picker">
            {TIERS.map((tier) => {
              const count = practiceTests.filter((p) => p.tier === tier).length
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
                    {isEmpty ? 'No papers yet' : `${count} paper${count === 1 ? '' : 's'}`}
                  </span>
                </button>
              )
            })}
          </div>
        )}
      </div>
    )
  }

  const filtered = practiceTests.filter((p) => p.tier === selectedTier)

  return (
    <div className="section-view">
      <button type="button" className="section-view__back" onClick={() => setSelectedTier(null)}>
        ← Back
      </button>
      <h2 className="section-view__title">
        Practice Tests <span className="section-view__tier">· {TIER_LABELS[selectedTier]}</span>
      </h2>
      <div className="topic-grid">
        {filtered.map((paper) => (
          <PracticeTestCard key={paper.id} paper={paper} />
        ))}
      </div>
    </div>
  )
}
