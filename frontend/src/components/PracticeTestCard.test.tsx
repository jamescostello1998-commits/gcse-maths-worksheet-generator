import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { PracticeTestCard } from './PracticeTestCard'
import type { PracticeTestSummary } from '../api/types'

const papers: PracticeTestSummary[] = [
  {
    id: 'foundation-01-paper1',
    name: 'Foundation Practice Test 1 – Paper 1 of 3',
    tier: 'foundation',
    sittingId: 'foundation-01',
    paperNumber: 1,
    totalMarks: 100,
    questionCount: 27,
  },
  {
    id: 'foundation-01-paper2',
    name: 'Foundation Practice Test 1 – Paper 2 of 3',
    tier: 'foundation',
    sittingId: 'foundation-01',
    paperNumber: 2,
    totalMarks: 100,
    questionCount: 25,
  },
  {
    id: 'foundation-01-paper3',
    name: 'Foundation Practice Test 1 – Paper 3 of 3',
    tier: 'foundation',
    sittingId: 'foundation-01',
    paperNumber: 3,
    totalMarks: 100,
    questionCount: 24,
  },
]

describe('PracticeTestCard', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    URL.revokeObjectURL = vi.fn()
  })

  it('shows the sitting name once and each paper with its own questions/marks summary', () => {
    render(<PracticeTestCard papers={papers} />)
    expect(screen.getByText('Foundation Practice Test 1')).toBeInTheDocument()
    expect(screen.getByText('Paper 1')).toBeInTheDocument()
    expect(screen.getByText('Paper 2')).toBeInTheDocument()
    expect(screen.getByText('Paper 3')).toBeInTheDocument()
    expect(screen.getByText(/27 questions/)).toBeInTheDocument()
    expect(screen.getAllByText(/100 marks/)).toHaveLength(3)
  })

  it('downloads a specific paper on click', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['%PDF-'], { type: 'application/pdf' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(<PracticeTestCard papers={papers} />)
    await user.click(screen.getAllByText('Test Paper')[1])

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/practice-tests/foundation-01-paper2/paper'),
    )
  })

  it('downloads a specific mark scheme on click', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['%PDF-'], { type: 'application/pdf' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(<PracticeTestCard papers={papers} />)
    await user.click(screen.getAllByText('Mark Scheme')[2])

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/practice-tests/foundation-01-paper3/mark-scheme'),
    )
  })
})
