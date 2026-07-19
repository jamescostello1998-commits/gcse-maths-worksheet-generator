import { useState } from 'react'
import { ErrorBanner } from './components/ErrorBanner'
import { GenerateButton } from './components/GenerateButton'
import { TierToggle } from './components/TierToggle'
import { TopicSearch } from './components/TopicSearch'
import { useGenerateWorksheet } from './hooks/useGenerateWorksheet'
import { useTopics } from './hooks/useTopics'
import type { Tier } from './api/types'
import './App.css'

function App() {
  const { topics, loading: topicsLoading, error: topicsError } = useTopics()
  const [selectedTopicId, setSelectedTopicId] = useState<string | null>(null)
  const [tier, setTier] = useState<Tier>('foundation')
  const { status, error: generateError, generate } = useGenerateWorksheet()

  const selectedTopic = topics.find((t) => t.id === selectedTopicId) ?? null

  return (
    <div className="page">
      <header className="page__header">
        <h1>GCSE Maths Worksheet Generator</h1>
        <p className="page__subtitle">
          Search for a topic, choose a tier, and download a 20-question worksheet with worked solutions.
        </p>
      </header>

      <ErrorBanner message={topicsError ?? generateError} />

      {topicsLoading ? (
        <p className="page__loading">Loading topics…</p>
      ) : (
        <>
          <TopicSearch topics={topics} selectedTopicId={selectedTopicId} onSelect={setSelectedTopicId} />

          <div className="page__controls">
            <TierToggle tier={tier} onChange={setTier} />
            <GenerateButton
              disabled={!selectedTopic}
              loading={status === 'loading'}
              onClick={() => selectedTopic && generate(selectedTopic.id, tier)}
            />
          </div>

          {selectedTopic && (
            <p className="page__selection">
              Selected: <strong>{selectedTopic.name}</strong> ({tier === 'foundation' ? 'Foundation' : 'Higher'})
            </p>
          )}
        </>
      )}
    </div>
  )
}

export default App
