import type { PracticeTestSummary } from '../api/types'
import { useDownloadMarkScheme } from '../hooks/useDownloadMarkScheme'
import { useDownloadTestPaper } from '../hooks/useDownloadTestPaper'

interface PracticeTestCardProps {
  papers: PracticeTestSummary[]
}

function sittingName(papers: PracticeTestSummary[]): string {
  return papers[0].name.split(' – Paper')[0]
}

function PaperRow({ paper }: { paper: PracticeTestSummary }) {
  const { status, error, download } = useDownloadTestPaper()
  const { status: markSchemeStatus, error: markSchemeError, download: downloadMarkScheme } = useDownloadMarkScheme()

  return (
    <div className="practice-test-card__paper">
      <div className="practice-test-card__paper-info">
        <span className="practice-test-card__paper-label">Paper {paper.paperNumber}</span>
        {!paper.calculatorAllowed && <span className="calculator-badge">Non-calculator</span>}
        <span className="topic-card__description">
          {paper.questionCount} questions • {paper.totalMarks} marks
        </span>
      </div>
      <div className="topic-card__actions">
        <button
          type="button"
          className="topic-card__generate"
          disabled={status === 'loading'}
          onClick={() => download(paper.id)}
        >
          {status === 'loading' ? 'Generating…' : 'Test Paper'}
        </button>
        <button
          type="button"
          className="topic-card__generate topic-card__generate--secondary"
          disabled={markSchemeStatus === 'loading'}
          onClick={() => downloadMarkScheme(paper.id)}
        >
          {markSchemeStatus === 'loading' ? 'Generating…' : 'Mark Scheme'}
        </button>
      </div>
      {status === 'error' && error && <p className="topic-card__error">{error}</p>}
      {markSchemeStatus === 'error' && markSchemeError && <p className="topic-card__error">{markSchemeError}</p>}
    </div>
  )
}

export function PracticeTestCard({ papers }: PracticeTestCardProps) {
  return (
    <div className="topic-card">
      <div className="topic-card__header">
        <h4 className="topic-card__name">{sittingName(papers)}</h4>
      </div>
      <div className="practice-test-card__papers">
        {papers.map((paper) => (
          <PaperRow key={paper.id} paper={paper} />
        ))}
      </div>
    </div>
  )
}
