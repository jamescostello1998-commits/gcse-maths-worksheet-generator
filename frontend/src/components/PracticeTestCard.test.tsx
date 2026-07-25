import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { PracticeTestCard } from './PracticeTestCard'
import type { PracticeTestSummary } from '../api/types'

const paper: PracticeTestSummary = {
  id: 'foundation-01',
  name: 'Foundation Practice Test 1',
  tier: 'foundation',
  totalMarks: 100,
  questionCount: 27,
}

describe('PracticeTestCard', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    URL.revokeObjectURL = vi.fn()
  })

  it('shows the paper name and a questions/marks summary', () => {
    render(<PracticeTestCard paper={paper} />)
    expect(screen.getByText('Foundation Practice Test 1')).toBeInTheDocument()
    expect(screen.getByText(/27 questions/)).toBeInTheDocument()
    expect(screen.getByText(/100 marks/)).toBeInTheDocument()
  })

  it('downloads the test paper on click', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['%PDF-'], { type: 'application/pdf' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(<PracticeTestCard paper={paper} />)
    await user.click(screen.getByText('Test Paper'))

    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/api/practice-tests/foundation-01/paper'))
  })

  it('downloads the mark scheme on click', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['%PDF-'], { type: 'application/pdf' }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(<PracticeTestCard paper={paper} />)
    await user.click(screen.getByText('Mark Scheme'))

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/practice-tests/foundation-01/mark-scheme'),
    )
  })
})
