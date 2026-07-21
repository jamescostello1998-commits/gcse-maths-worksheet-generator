import { useState } from 'react'
import type { Tier, Topic } from '../api/types'
import { useGenerateModelledExample } from '../hooks/useGenerateModelledExample'
import { useGenerateWorksheet } from '../hooks/useGenerateWorksheet'

const MIN_QUESTION_COUNT = 5
const MAX_QUESTION_COUNT = 40

interface TopicCardProps {
  topic: Topic
  showTierBadge?: boolean
}

export function TopicCard({ topic, showTierBadge = true }: TopicCardProps) {
  const [selectedTier, setSelectedTier] = useState<Tier>(topic.fixedTier ?? 'foundation')
  const [showOptions, setShowOptions] = useState(false)
  // Kept as free-typed text (not clamped per keystroke) so typing a two-digit
  // number doesn't get mangled by an intermediate single-digit value being
  // clamped mid-entry. Clamped once, on blur and on generate.
  const [questionCountInput, setQuestionCountInput] = useState(String(topic.defaultQuestionCount))
  const [answersOnly, setAnswersOnly] = useState(false)
  const { status, error, generate } = useGenerateWorksheet()
  const {
    status: modelledStatus,
    error: modelledError,
    generate: generateModelled,
  } = useGenerateModelledExample()

  const effectiveTier = topic.fixedTier ?? selectedTier

  const clampedQuestionCount = () => {
    const parsed = Number(questionCountInput)
    if (Number.isNaN(parsed)) return topic.defaultQuestionCount
    return Math.min(MAX_QUESTION_COUNT, Math.max(MIN_QUESTION_COUNT, Math.round(parsed)))
  }

  const handleQuestionCountBlur = () => {
    setQuestionCountInput(String(clampedQuestionCount()))
  }

  const handleGenerate = () => {
    const count = clampedQuestionCount()
    generate(topic.id, effectiveTier, {
      count: count !== topic.defaultQuestionCount ? count : undefined,
      answersOnly,
    })
  }

  return (
    <div className="topic-card">
      <div className="topic-card__header">
        <h4 className="topic-card__name">{topic.name}</h4>
        {topic.fixedTier ? (
          showTierBadge && (
            <span className={`tier-badge tier-badge--${topic.fixedTier}`}>
              {topic.fixedTier === 'foundation' ? 'Foundation' : 'Higher'}
            </span>
          )
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
      <button
        type="button"
        className="topic-card__options-toggle"
        aria-expanded={showOptions}
        onClick={() => setShowOptions((v) => !v)}
      >
        {showOptions ? 'Hide options ▲' : 'Options ▾'}
      </button>
      {showOptions && (
        <div className="topic-card__options">
          <label className="topic-card__count-label" htmlFor={`count-${topic.id}`}>
            Questions
            <input
              id={`count-${topic.id}`}
              type="number"
              className="topic-card__count-input"
              min={MIN_QUESTION_COUNT}
              max={MAX_QUESTION_COUNT}
              value={questionCountInput}
              onChange={(e) => setQuestionCountInput(e.target.value)}
              onBlur={handleQuestionCountBlur}
            />
          </label>
          <label className="topic-card__checkbox-label">
            <input
              type="checkbox"
              checked={answersOnly}
              onChange={(e) => setAnswersOnly(e.target.checked)}
            />
            Answers only
          </label>
        </div>
      )}
      <div className="topic-card__actions">
        <button
          type="button"
          className="topic-card__generate"
          disabled={status === 'loading'}
          onClick={handleGenerate}
        >
          {status === 'loading' ? 'Generating…' : 'Worksheet'}
        </button>
        {topic.hasModelledExample && (
          <button
            type="button"
            className="topic-card__generate topic-card__generate--secondary"
            disabled={modelledStatus === 'loading'}
            onClick={() => generateModelled(topic.id, effectiveTier)}
          >
            {modelledStatus === 'loading' ? 'Generating…' : 'Modelled Example'}
          </button>
        )}
      </div>
      {status === 'error' && error && <p className="topic-card__error">{error}</p>}
      {modelledStatus === 'error' && modelledError && <p className="topic-card__error">{modelledError}</p>}
    </div>
  )
}
