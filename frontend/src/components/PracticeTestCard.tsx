import type { PracticeTestSummary } from '../api/types'
import { useDownloadMarkScheme } from '../hooks/useDownloadMarkScheme'
import { useDownloadTestPaper } from '../hooks/useDownloadTestPaper'

interface PracticeTestCardProps {
  paper: PracticeTestSummary
}

export function PracticeTestCard({ paper }: PracticeTestCardProps) {
  const { status, error, download } = useDownloadTestPaper()
  const { status: markSchemeStatus, error: markSchemeError, download: downloadMarkScheme } = useDownloadMarkScheme()

  return (
    <div className="topic-card">
      <div className="topic-card__header">
        <h4 className="topic-card__name">{paper.name}</h4>
      </div>
      <p className="topic-card__description">
        {paper.questionCount} questions • {paper.totalMarks} marks
      </p>
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
