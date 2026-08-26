import { useMemo, useState } from 'react'
import type { BellTasksYear } from '../api/client'
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

// Box count and display label per year group - Year 10 keeps the original
// 6-box template unchanged; Year 11 uses a new 8-box template (see
// backend/app/bell_tasks/generator.py's _TEMPLATES). "Years 7-9" is a
// deliberately disabled placeholder for now, matching how "KS3" was
// deferred previously - not wired to a template at all yet.
const NUM_BOXES: Record<BellTasksYear, number> = { year_10: 6, year_11: 8 }
const YEAR_LABELS: Record<BellTasksYear, string> = { year_10: 'Year 10', year_11: 'Year 11' }
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
  const [year, setYear] = useState<BellTasksYear | null>(null)
  const [selectedTopicIds, setSelectedTopicIds] = useState<string[]>([])
  const { status, error, generate } = useGenerateBellTasks()

  const options = useMemo(() => toSearchableOptions(flattenTopics(sections)), [sections])

  function selectYear(nextYear: BellTasksYear) {
    setYear(nextYear)
    setSelectedTopicIds(Array(NUM_BOXES[nextYear]).fill(''))
  }

  if (!year) {
    return (
      <div className="section-view">
        <button type="button" className="section-view__back" onClick={onBack}>
          ← Back
        </button>
        <h2 className="section-view__title">Bell Tasks</h2>
        <div className="tier-picker">
          <button type="button" className="tier-picker__option" onClick={() => selectYear('year_11')}>
            <span className="tier-picker__name">Year 11</span>
            <span className="tier-picker__count">Generate an 8-topic bell task PowerPoint</span>
          </button>
          <button type="button" className="tier-picker__option" onClick={() => selectYear('year_10')}>
            <span className="tier-picker__name">Year 10</span>
            <span className="tier-picker__count">Generate a 6-topic bell task PowerPoint</span>
          </button>
          <button type="button" className="tier-picker__option tier-picker__option--empty" disabled>
            <span className="tier-picker__name">Years 7-9</span>
            <span className="tier-picker__count">Coming soon</span>
          </button>
        </div>
      </div>
    )
  }

  const numBoxes = NUM_BOXES[year]
  const filledCount = selectedTopicIds.filter((id) => id !== '').length
  const distinctCount = new Set(selectedTopicIds.filter((id) => id !== '')).size
  const canGenerate = filledCount === numBoxes && distinctCount === numBoxes

  function handleSelect(boxIndex: number, topicId: string) {
    setSelectedTopicIds((prev) => {
      const next = [...prev]
      next[boxIndex] = topicId
      return next
    })
  }

  return (
    <div className="section-view">
      <button type="button" className="section-view__back" onClick={() => setYear(null)}>
        ← Back
      </button>
      <h2 className="section-view__title">
        Bell Tasks <span className="section-view__tier">· {YEAR_LABELS[year]}</span>
      </h2>
      <p className="page__subtitle">
        Choose {numBoxes} topics, one per box. Each box keeps the same topic all week, with a new question
        in it each day (5 questions per topic, {numBoxes * 5} in total).
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
        onClick={() => generate(selectedTopicIds, year)}
      >
        {status === 'loading' ? 'Generating…' : 'Generate Bell Tasks'}
      </button>
      {error && <p className="topic-card__error">{error}</p>}
    </div>
  )
}
