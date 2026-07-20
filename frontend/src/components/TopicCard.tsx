import { useState } from 'react'
import type { Tier, Topic } from '../api/types'
import { useGenerateModelledExample } from '../hooks/useGenerateModelledExample'
import { useGenerateWorksheet } from '../hooks/useGenerateWorksheet'

interface TopicCardProps {
  topic: Topic
}

export function TopicCard({ topic }: TopicCardProps) {
  const [selectedTier, setSelectedTier] = useState<Tier>(topic.fixedTier ?? 'foundation')
  const { status, error, generate } = useGenerateWorksheet()
  const {
    status: modelledStatus,
    error: modelledError,
    generate: generateModelled,
  } = useGenerateModelledExample()

  const effectiveTier = topic.fixedTier ?? selectedTier

  return (
    <div className="topic-card">
      <div className="topic-card__header">
        <h4 className="topic-card__name">{topic.name}</h4>
        {topic.fixedTier ? (
          <span className={`tier-badge tier-badge--${topic.fixedTier}`}>
            {topic.fixedTier === 'foundation' ? 'Foundation' : 'Higher'}
          </span>
        ) : (
          <div className="tier-mini-toggle" role="radiogroup" aria-label={`Tier for ${topic.name}`}>
            {(['foundation', 'higher'] as const).map((option) => (
              <button
                key={option}
                type="button"
                role="radio"
                aria-checked={selectedTier === option}
                className={
                  selectedTier === option
                    ? 'tier-mini-toggle__option tier-mini-toggle__option--active'
                    : 'tier-mini-toggle__option'
                }
                onClick={() => setSelectedTier(option)}
              >
                {option === 'foundation' ? 'F' : 'H'}
              </button>
            ))}
          </div>
        )}
      </div>
      <p className="topic-card__description">{topic.description}</p>
      <div className="topic-card__actions">
        <button
          type="button"
          className="topic-card__generate"
          disabled={status === 'loading'}
          onClick={() => generate(topic.id, effectiveTier)}
        >
          {status === 'loading' ? 'Generating…' : 'Generate Worksheet'}
        </button>
        {topic.hasModelledExample && (
          <button
            type="button"
            className="topic-card__generate topic-card__generate--secondary"
            disabled={modelledStatus === 'loading'}
            onClick={() => generateModelled(topic.id, effectiveTier)}
          >
            {modelledStatus === 'loading' ? 'Generating…' : 'Generate Modelled Example'}
          </button>
        )}
      </div>
      {status === 'error' && error && <p className="topic-card__error">{error}</p>}
      {modelledStatus === 'error' && modelledError && <p className="topic-card__error">{modelledError}</p>}
    </div>
  )
}
