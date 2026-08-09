import { useMemo, useState } from 'react'
import type { Section, Topic } from '../api/types'
import { useGenerateBellTasks } from '../hooks/useGenerateBellTasks'
import { SearchableTopicSelect, type SearchableTopicOption } from './SearchableTopicSelect'

interface BellTasksViewProps {
  sections: Section[]
  onBack: () => void
}

interface FlatTopic {
  topic: Topic
  breadcrumb: string
}

const NUM_BOXES = 6
const TIER_LABELS: Record<'foundation' | 'higher', string> = { foundation: 'Foundation', higher: 'Higher' }

function flattenTopics(sections: Section[]): FlatTopic[] {
  const flat: FlatTopic[] = []
  for (const section of sections) {
    for (const group of section.groups) {
      for (const topic of group.topics) {
        flat.push({ topic, breadcrumb: `${section.name} › ${group.name}` })
      }
    }
  }
  return flat
}

function topicOptionLabel(topic: Topic): string {
  if (!topic.fixedTier) return topic.name
  const tierSuffix = `(${TIER_LABELS[topic.fixedTier]})`
  // Some topic names already end with their own tier disambiguator (e.g.
  // "Dividing Fractions (Foundation)", a naming convention this app uses for
  // Foundation/Higher sibling topics) - don't double it up to "... (Foundation)
  // (Foundation)".
  if (topic.name.endsWith(tierSuffix)) return topic.name
  return `${topic.name} ${tierSuffix}`
}

function toSearchableOptions(flat: FlatTopic[]): SearchableTopicOption[] {
  return flat.map(({ topic, breadcrumb }) => ({
    id: topic.id,
    label: topicOptionLabel(topic),
    breadcrumb,
  }))
}

export function BellTasksView({ sections, onBack }: BellTasksViewProps) {
  const [keyStage, setKeyStage] = useState<'ks3' | 'ks4' | null>(null)
  const [selectedTopicIds, setSelectedTopicIds] = useState<string[]>(Array(NUM_BOXES).fill(''))
  const { status, error, generate } = useGenerateBellTasks()

  const options = useMemo(() => toSearchableOptions(flattenTopics(sections)), [sections])

  if (!keyStage) {
    return (
      <div className="section-view">
        <button type="button" className="section-view__back" onClick={onBack}>
          ← Back
        </button>
        <h2 className="section-view__title">Bell Tasks</h2>
        <div className="tier-picker">
          <button type="button" className="tier-picker__option" onClick={() => setKeyStage('ks4')}>
            <span className="tier-picker__name">KS4</span>
            <span className="tier-picker__count">Generate a 6-topic bell task PowerPoint</span>
          </button>
          <button type="button" className="tier-picker__option tier-picker__option--empty" disabled>
            <span className="tier-picker__name">KS3</span>
            <span className="tier-picker__count">Coming soon</span>
          </button>
        </div>
      </div>
    )
  }

  const filledCount = selectedTopicIds.filter((id) => id !== '').length
  const distinctCount = new Set(selectedTopicIds.filter((id) => id !== '')).size
  const canGenerate = filledCount === NUM_BOXES && distinctCount === NUM_BOXES

  function handleSelect(boxIndex: number, topicId: string) {
    setSelectedTopicIds((prev) => {
      const next = [...prev]
      next[boxIndex] = topicId
      return next
    })
  }

  return (
    <div className="section-view">
      <button type="button" className="section-view__back" onClick={() => setKeyStage(null)}>
        ← Back
      </button>
      <h2 className="section-view__title">
        Bell Tasks <span className="section-view__tier">· KS4</span>
      </h2>
      <p className="page__subtitle">
        Choose 6 topics, one per box. Each box keeps the same topic all week, with a new question in it
        each day (5 questions per topic, 30 in total).
      </p>

      <div className="bell-tasks-picker">
        {selectedTopicIds.map((value, index) => {
          const excludedIds = new Set(selectedTopicIds.filter((_id, i) => i !== index && _id !== ''))
          const availableOptions = options.filter((o) => o.id === value || !excludedIds.has(o.id))
          return (
            <label key={index} className="bell-tasks-picker__box">
              <span className="bell-tasks-picker__box-label">Box {index + 1}</span>
              <SearchableTopicSelect
                ariaLabel={`Box ${index + 1} topic`}
                options={availableOptions}
                value={value}
                onChange={(topicId) => handleSelect(index, topicId)}
              />
            </label>
          )
        })}
      </div>

      <button
        type="button"
        className="topic-card__generate bell-tasks-picker__generate"
        disabled={!canGenerate || status === 'loading'}
        onClick={() => generate(selectedTopicIds)}
      >
        {status === 'loading' ? 'Generating…' : 'Generate Bell Tasks'}
      </button>
      {error && <p className="topic-card__error">{error}</p>}
    </div>
  )
}
