import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { PracticeTestsView } from './PracticeTestsView'

const rawPracticeTests = [
  {
    id: 'foundation-01-paper1',
    name: 'Foundation Practice Test 1 – Paper 1 of 3',
    tier: 'foundation',
    sitting_id: 'foundation-01',
    paper_number: 1,
    calculator_allowed: true,
    total_marks: 100,
    question_count: 27,
  },
  {
    id: 'higher-01-paper1',
    name: 'Higher Practice Test 1 – Paper 1 of 3',
    tier: 'higher',
    sitting_id: 'higher-01',
    paper_number: 1,
    calculator_allowed: true,
    total_marks: 100,
    question_count: 23,
  },
]

function stubFetchWithPracticeTests(): void {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: async () => rawPracticeTests,
    }),
  )
}

describe('PracticeTestsView', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    URL.createObjectURL = vi.fn(() => 'blob:mock-url')
    URL.revokeObjectURL = vi.fn()
  })

  it('shows a Foundation/Higher tier picker before any papers', async () => {
    stubFetchWithPracticeTests()
    render(<PracticeTestsView onBack={vi.fn()} />)
    await waitFor(() => expect(screen.getByText('Foundation')).toBeInTheDocument())
    expect(screen.getByText('Higher')).toBeInTheDocument()
    expect(screen.queryByText('Foundation Practice Test 1')).not.toBeInTheDocument()
  })

  it('shows only papers for the selected tier after picking a tier', async () => {
    stubFetchWithPracticeTests()
    const user = userEvent.setup()
    render(<PracticeTestsView onBack={vi.fn()} />)
    await waitFor(() => expect(screen.getByText('Foundation')).toBeInTheDocument())
    await user.click(screen.getByText('Foundation'))
    expect(screen.getByText('Foundation Practice Test 1')).toBeInTheDocument()
    expect(screen.queryByText('Higher Practice Test 1')).not.toBeInTheDocument()
  })

  it('going back from the paper list returns to the tier picker, not Home', async () => {
    stubFetchWithPracticeTests()
    const user = userEvent.setup()
    const onBack = vi.fn()
    render(<PracticeTestsView onBack={onBack} />)
    await waitFor(() => expect(screen.getByText('Foundation')).toBeInTheDocument())
    await user.click(screen.getByText('Foundation'))
    expect(screen.getByText('Foundation Practice Test 1')).toBeInTheDocument()
    await user.click(screen.getByText('← Back'))
    expect(screen.getByText('Foundation')).toBeInTheDocument()
    expect(screen.queryByText('Foundation Practice Test 1')).not.toBeInTheDocument()
    expect(onBack).not.toHaveBeenCalled()
  })

  it('calls onBack when the back button is clicked from the tier picker', async () => {
    stubFetchWithPracticeTests()
    const user = userEvent.setup()
    const onBack = vi.fn()
    render(<PracticeTestsView onBack={onBack} />)
    await waitFor(() => expect(screen.getByText('Foundation')).toBeInTheDocument())
    await user.click(screen.getByText('← Back'))
    expect(onBack).toHaveBeenCalled()
  })

  it('surfaces a load error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('down')))
    render(<PracticeTestsView onBack={vi.fn()} />)
    await waitFor(() => expect(screen.getByText(/reach the server/i)).toBeInTheDocument())
  })
})
