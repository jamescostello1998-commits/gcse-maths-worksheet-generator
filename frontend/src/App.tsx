import { useState } from 'react'
import { ErrorBanner } from './components/ErrorBanner'
import { HomeScreen } from './components/HomeScreen'
import { SectionView } from './components/SectionView'
import { TopicSearch } from './components/TopicSearch'
import { useSections } from './hooks/useSections'
import './App.css'

function App() {
  const { sections, loading, error } = useSections()
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null)
  const [query, setQuery] = useState('')

  const selectedSection = sections.find((s) => s.id === selectedSectionId) ?? null
  const isSearching = query.trim().length > 0

  return (
    <div className="page">
      <header className="page__header">
        <h1>GCSE Maths Worksheet Generator</h1>
        <p className="page__subtitle">
          Browse by topic, or search directly, then download a 20-question worksheet with worked solutions.
        </p>
      </header>

      <input
        type="text"
        className="page__search"
        placeholder="Search for a topic..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search for a topic"
      />

      <ErrorBanner message={error} />

      {loading ? (
        <p className="page__loading">Loading topics…</p>
      ) : isSearching ? (
        <TopicSearch sections={sections} query={query} />
      ) : selectedSection ? (
        <SectionView section={selectedSection} onBack={() => setSelectedSectionId(null)} />
      ) : (
        <HomeScreen sections={sections} onSelectSection={setSelectedSectionId} />
      )}
    </div>
  )
}

export default App
