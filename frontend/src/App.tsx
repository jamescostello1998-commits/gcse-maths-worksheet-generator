import { useState } from 'react'
import { BellTasksView } from './components/BellTasksView'
import { ErrorBanner } from './components/ErrorBanner'
import { HomeScreen } from './components/HomeScreen'
import { PracticeTestsView } from './components/PracticeTestsView'
import { SectionView } from './components/SectionView'
import { TopicSearch } from './components/TopicSearch'
import { useSections } from './hooks/useSections'
import './App.css'

function App() {
  const { sections, loading, error } = useSections()
  const [selectedSectionId, setSelectedSectionId] = useState<string | null>(null)
  const [practiceTestsOpen, setPracticeTestsOpen] = useState(false)
  const [bellTasksOpen, setBellTasksOpen] = useState(false)
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
      ) : practiceTestsOpen ? (
        <PracticeTestsView onBack={() => setPracticeTestsOpen(false)} />
      ) : bellTasksOpen ? (
        <BellTasksView sections={sections} onBack={() => setBellTasksOpen(false)} />
      ) : selectedSection ? (
        <SectionView section={selectedSection} onBack={() => setSelectedSectionId(null)} />
      ) : (
        <>
          <HomeScreen sections={sections} onSelectSection={setSelectedSectionId} />
          <section className="practice-tests-section">
            <h2 className="practice-tests-section__heading">Practice Tests</h2>
            <p className="practice-tests-section__subtitle">
              Fixed, exam-style papers - 10 Foundation and 10 Higher practice tests, each a sitting of 3
              papers, 100 marks and 1 hour 30 minutes per paper.
            </p>
            <button
              type="button"
              className="section-card practice-tests-entry"
              onClick={() => setPracticeTestsOpen(true)}
            >
              <h2 className="section-card__name">Practice Tests</h2>
              <p className="section-card__count">20 practice tests · 60 papers</p>
            </button>
          </section>
          <section className="practice-tests-section">
            <h2 className="practice-tests-section__heading">Bell Tasks</h2>
            <p className="practice-tests-section__subtitle">
              A 5-day starter-activity PowerPoint - pick 6 topics and get a week's worth of quick
              questions, one topic per box, every day.
            </p>
            <button
              type="button"
              className="section-card practice-tests-entry"
              onClick={() => setBellTasksOpen(true)}
            >
              <h2 className="section-card__name">Bell Tasks</h2>
              <p className="section-card__count">KS3 &amp; KS4 · pick 6 topics</p>
            </button>
          </section>
        </>
      )}
    </div>
  )
}

export default App
